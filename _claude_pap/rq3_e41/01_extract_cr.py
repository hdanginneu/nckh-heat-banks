"""01_extract_cr.py — trích Call Report Q4 1994–2004 theo đúng mã MDRM mà Phase 1 (2005–2025) và bước 07 dùng.
Nguồn: Chicago Fed (SAS XPORT) 1994–2000; FFIEC CDR bulk (TSV) 2001–2004. Đơn vị nghìn USD.
Quy tắc chọn mã (chép từ cột *_source của Phase 1 và docstring 07_ffiec_ag_extract.py):
  - mục bảng cân đối và RI: RCFD nếu có giá trị, nếu không thì RCON (Phase 1 dùng RCFD cho ~19 ngân hàng có chi nhánh nước ngoài);
  - đất NN RCON1420 (chỉ RCON); RC-N: RCON trước, RCFD nếu RCON trống (như 07);
  - bán vốn liên ngân hàng: RCONB987 + (RCFDB989 hoặc RCONB989) từ 2002; trước 2002 mục gộp RCFD1350/RCON1350 (cùng khái niệm, MDRM tách năm 2002).
Ô trống = NaN, không điền 0. Mọi lựa chọn mã ghi trong MDRM_MAP.csv để Hữu Anh kiểm (D37/G4h).
Lệnh: python3 01_extract_cr.py [năm ...]   (mặc định 1994–2004; mỗi năm lưu riêng ở OUT/cr_parts)
Đầu ra: OUT/cr_1994_2004.parquet, OUT/cr_coverage.csv, MDRM_MAP.csv (cạnh file này)."""
import os, glob, zipfile, sys
import numpy as np, pandas as pd
from e41_common import EXT, OUT, TMP, CR_YEARS

BAL = {  # tên Phase 1: mã không tiền tố (RCFD trước, RCON sau)
    "total_assets_kusd": "2170", "total_loans_kusd": "2122", "ag_production_loans_kusd": "1590", "htm_securities_kusd": "1754",
    "afs_securities_kusd": "1773", "allowance_legacy_kusd": "3123", "total_equity_kusd": "3210"}
CASH = ["0081", "0071"]
RIAD = {"chargeoffs_ytd_kusd": "4635", "recoveries_ytd_kusd": "4605", "farmland_chargeoff": "3584", "farmland_recovery": "3585",
        "farm_chargeoff": "4655", "farm_recovery": "4665", "net_income_ytd_kusd": "4340", "provision_ytd_kusd": "4230"}
RCN = {"farmland_pd30_89": "3493", "farmland_pd90": "3494", "farmland_nonaccrual": "3495",
       "farm_pd30_89": "1594", "farm_pd90": "1597", "farm_nonaccrual": "1583"}
ALLC = (["RSSD9001", "RSSD9050", "RSSD9200"] + [p + c for c in list(BAL.values()) + CASH + ["1350", "B989"] for p in ("RCFD", "RCON")] +
        ["RCON1420", "RCONB987"] + ["RIAD" + c for c in RIAD.values()] + [p + c for c in RCN.values() for p in ("RCON", "RCFD")])

def num(d, c): return pd.to_numeric(d[c], errors="coerce") if c in d.columns else pd.Series(np.nan, index=d.index)
def fd_con(d, code):
    fd, con = num(d, "RCFD" + code), num(d, "RCON" + code); return fd.where(fd.notna(), con)
def con_fd(d, code):
    fd, con = num(d, "RCFD" + code), num(d, "RCON" + code); return con.where(con.notna(), fd)

def derive(d, year):
    o = pd.DataFrame({"idrssd": num(d, "RSSD9001").astype("Int64"), "cert": num(d, "RSSD9050"), "hq_state": d["RSSD9200"].astype(str)})
    for k, c in BAL.items(): o[k] = fd_con(d, c)
    o["farmland_loans_kusd"] = num(d, "RCON1420")
    o["cash_and_due_kusd"] = fd_con(d, "0081") + fd_con(d, "0071")
    if "RCONB987" in d.columns and d["RCONB987"].notna().any():
        o["fed_funds_sold_kusd"] = num(d, "RCONB987") + fd_con(d, "B989"); o["ffs_basis"] = "B987+B989"
    else:
        o["fed_funds_sold_kusd"] = fd_con(d, "1350"); o["ffs_basis"] = "1350"
    for k, c in RIAD.items(): o[k] = num(d, "RIAD" + c)
    for k, c in RCN.items(): o[k] = con_fd(d, c)
    o["year"] = year
    return o

def read_chicago(year):
    z = f"{EXT}/chicagofed/call{str(year)[2:]}12-zip.zip"
    with zipfile.ZipFile(z) as zf:
        nm = [n for n in zf.namelist() if n.upper().endswith(".XPT")][0]; path = os.path.join(TMP, nm)
        if not os.path.exists(path): zf.extract(nm, TMP)
    parts = []
    for ch in pd.read_sas(path, format="xport", chunksize=4000, encoding="latin-1"):
        parts.append(ch[[c for c in ALLC if c in ch.columns]])
    d = pd.concat(parts, ignore_index=True)
    return d

def read_ffiec(year):
    z = f"{EXT}/ffiec_bulk/FFIEC_CDR_Call_Bulk_All_Schedules_1231{year}.zip"; parts = []
    with zipfile.ZipFile(z) as zf:
        for s in ("RC", "RCB", "RCCI", "RCN", "RIBI", "RI"):
            for nm in [n for n in zf.namelist() if n.startswith(f"FFIEC CDR Call Schedule {s} 1231{year}")]:
                with zf.open(nm) as f:
                    df = pd.read_csv(f, sep="\t", dtype=str, skiprows=[1], encoding="latin-1", quotechar='"', low_memory=False)
                df.columns = [c.strip().strip('"') for c in df.columns]
                df = df.set_index("IDRSSD"); parts.append(df[[c for c in df.columns if c in ALLC]])
        por = [n for n in zf.namelist() if "Bulk POR" in n][0]
        with zf.open(por) as f:
            p = pd.read_csv(f, sep="\t", dtype=str, encoding="latin-1", quotechar='"')
        p.columns = [c.strip().strip('"') for c in p.columns]
        p = p.set_index("IDRSSD")[["FDIC Certificate Number", "Financial Institution State"]].rename(
            columns={"FDIC Certificate Number": "RSSD9050", "Financial Institution State": "RSSD9200"})
    d = pd.concat(parts, axis=1); d = d.loc[:, ~d.columns.duplicated()].join(p, how="left")
    d.index = pd.to_numeric(d.index, errors="coerce"); d = d.reset_index().rename(columns={"IDRSSD": "RSSD9001", "index": "RSSD9001"})
    return d

def main(years):
    os.makedirs(f"{OUT}/cr_parts", exist_ok=True)
    for y in years:                                    # mỗi năm một file, chạy lại được từng năm
        f = f"{OUT}/cr_parts/cr_{y}.parquet"
        if os.path.exists(f): continue
        d = read_chicago(y) if y <= 2000 else read_ffiec(y)
        o = derive(d, y); o = o[o.idrssd.notna() & o.total_assets_kusd.notna()]
        assert not o.duplicated("idrssd").any(), y
        o["hq_state"] = o.hq_state.str.replace(r"^b'|'$", "", regex=True).str.strip()
        o.to_parquet(f, index=False); print(y, "nguồn", "Chicago Fed" if y <= 2000 else "FFIEC", "ngân hàng", len(o), "ffs:", o.ffs_basis.iloc[0], flush=True)
    if not all(os.path.exists(f"{OUT}/cr_parts/cr_{y}.parquet") for y in CR_YEARS): return
    cr = pd.concat([pd.read_parquet(f"{OUT}/cr_parts/cr_{y}.parquet") for y in CR_YEARS], ignore_index=True)
    cr.to_parquet(f"{OUT}/cr_1994_2004.parquet", index=False)
    cov = cr.drop(columns=["idrssd", "cert", "hq_state", "ffs_basis"]).groupby("year").agg(lambda s: s.notna().mean()).round(3)
    cov.to_csv(f"{OUT}/cr_coverage.csv"); pd.set_option("display.width", 250); print(cov.T.to_string())
    rows = [(k, f"RCFD{c} nếu có, không thì RCON{c}") for k, c in BAL.items()] + [("farmland_loans_kusd", "RCON1420"),
            ("cash_and_due_kusd", "(RCFD|RCON)0081 + (RCFD|RCON)0071"),
            ("fed_funds_sold_kusd", "2002–2004: RCONB987 + (RCFD|RCON)B989; 1994–2001: (RCFD|RCON)1350")] + \
           [(k, f"RIAD{c}") for k, c in RIAD.items()] + [(k, f"RCON{c} nếu có, không thì RCFD{c}") for k, c in RCN.items()]
    pd.DataFrame(rows, columns=["bien", "ma_MDRM"]).to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "MDRM_MAP.csv"), index=False)

if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or list(CR_YEARS))
