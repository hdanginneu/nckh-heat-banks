"""10_process_rma.py — RMA (Cause of Loss + Summary of Business) → panel hạt-năm.
Đầu vào: ~/Projects/nckh_data/external/rma/{colsom,sobcov}_YYYY.zip (2001-2022; bản sao www.rma.usda.gov).
Đầu ra (`_claude_pap/out/`):
  rma_cause_codes.csv         mã nguyên nhân, mô tả, bồi thường tổng theo năm (để pre-register tập mã)
  rma_county_year.parquet     fips × commodity_year: bồi thường theo nhóm nguyên nhân, liability, premium, subsidy
  rma_coverage_ratio.csv      fips: liability TB 2001-05 / doanh thu cây trồng BEA TB 2001-05 (dòng 60)
Quy ước:
  - Năm = Commodity Year (năm thu hoạch; khớp nhiệt mùa vụ). Tiền bồi thường = cột 29 'Indemnity Amount' (USD).
  - Nhóm nguyên nhân (đăng ký trước): HD_main = {11 Drought, 12 Heat, 62 Hot Wind}; HEAT_only = {12, 62};
    HD_wide (robustness) = HD_main + {13 Failure of Irrigation Supply, 22 Excess Sun}. Mã 55 (GRP/ARPI/SCO/STAX/MP)
    không có nguyên nhân cụ thể → chỉ vào tổng, không vào nhóm nhiệt/hạn.
  - Không cộng lại một hàng hai lần: mỗi hàng là một tổ hợp (hạt, cây, gói bảo hiểm, giai đoạn, nguyên nhân, tháng, năm lỗ).
  - Hạt '999' (All Other Counties) không có FIPS thật → loại khỏi panel hạt, đếm phần bị loại.
  - Không điền 0 cho hạt-năm không có hàng: hạt-năm vắng nghĩa là 'không có bản ghi RMA' (ghi rõ ở đầu ra).
"""
import zipfile
import pandas as pd
import numpy as np
from _pap_common import *

COL = ["year", "st", "stab", "cty", "ctyname", "cmd", "cmdname", "plan", "planab", "cov", "stage", "cause", "causedesc", "mon", "monname",
       "lossyr", "pol_prem", "pol_ind", "netq", "endacres", "liab", "prem", "prod_prem", "subsidy", "stsub", "addsub", "efa", "detq", "indem", "lr"]
SOB = ["year", "st", "stab", "cty", "ctyname", "cmd", "cmdname", "plan", "planab", "cov", "delivery", "covlevel", "pol_sold", "pol_prem", "pol_ind",
       "units_prem", "units_ind", "qtype", "netq", "endacres", "liab", "prem", "subsidy", "stsub", "addsub", "efa", "indem", "lr"]
HD_MAIN, HEAT_ONLY, HD_WIDE = {"11", "12", "62"}, {"12", "62"}, {"11", "12", "62", "13", "22"}
YEARS = range(2001, 2023)


def read_zip(path, cols):
    z = zipfile.ZipFile(path)
    df = pd.read_csv(z.open(z.namelist()[0]), sep="|", header=None, names=cols, dtype=str, encoding="latin1")
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].str.strip()
    return df


cause_tot, rows, sob_rows, drops = [], [], [], []
for y in YEARS:
    c = read_zip(RMA / f"colsom_{y}.zip", COL)
    assert c.shape[1] == 30 and c["indem"].notna().all(), y
    for k in ["indem", "liab", "prem", "subsidy", "pol_ind"]:
        c[k] = pd.to_numeric(c[k])
    c["mon"] = pd.to_numeric(c["mon"], errors="coerce")
    cause_tot.append(c.groupby(["cause", "causedesc"], as_index=False)["indem"].sum().assign(year=y))
    c["fips"] = c["st"].str.zfill(2) + c["cty"].str.zfill(3)
    drops.append(dict(year=y, kind="col", n_rows=len(c), n_other_counties=(c["cty"] == "999").sum(),
                      indem_other_counties=c.loc[c["cty"] == "999", "indem"].sum(), indem_total=c["indem"].sum()))
    c = c[c["cty"] != "999"]
    c["gs"] = c["mon"].between(4, 9)  # tháng thiệt hại Apr-Sep
    g = c.groupby("fips")
    out = pd.DataFrame({
        "indem_total": g["indem"].sum(),
        "indem_hd_main": c[c["cause"].isin(HD_MAIN)].groupby("fips")["indem"].sum(),
        "indem_heat_only": c[c["cause"].isin(HEAT_ONLY)].groupby("fips")["indem"].sum(),
        "indem_hd_wide": c[c["cause"].isin(HD_WIDE)].groupby("fips")["indem"].sum(),
        "indem_hd_main_gs": c[c["cause"].isin(HD_MAIN) & c["gs"]].groupby("fips")["indem"].sum(),
        "indem_excess_moist": c[c["cause"] == "31"].groupby("fips")["indem"].sum(),
        "indem_cause55": c[c["cause"] == "55"].groupby("fips")["indem"].sum(),
    }).fillna(0.0)  # hạt có hàng RMA nhưng không có bồi thường ở nhóm đó = 0 hợp lệ (có bản ghi)
    out["year"] = y
    out["col_liab_ind_rows"] = g.size()
    rows.append(out.reset_index())

    s = read_zip(RMA / f"sobcov_{y}.zip", SOB)
    assert s.shape[1] == 28, y
    for k in ["liab", "prem", "subsidy", "indem", "pol_ind"]:
        s[k] = pd.to_numeric(s[k])
    s["fips"] = s["st"].str.zfill(2) + s["cty"].str.zfill(3)
    drops.append(dict(year=y, kind="sob", n_rows=len(s), n_other_counties=(s["cty"] == "999").sum(),
                      indem_other_counties=s.loc[s["cty"] == "999", "indem"].sum(), indem_total=s["indem"].sum(),
                      liab_other=s.loc[s["cty"] == "999", "liab"].sum(), liab_total=s["liab"].sum()))
    s = s[s["cty"] != "999"]
    sg = s.groupby("fips").agg(liab=("liab", "sum"), prem=("prem", "sum"), subsidy=("subsidy", "sum"), sob_indem=("indem", "sum")).reset_index()
    sg["year"] = y
    sob_rows.append(sg)
    print(y, len(c), len(s), flush=True)

ct = pd.concat(cause_tot)
codes_tab = ct.pivot_table(index=["cause", "causedesc"], columns="year", values="indem", aggfunc="sum").fillna(0)
codes_tab["total_2001_2022"] = codes_tab.sum(axis=1)
codes_tab.sort_values("total_2001_2022", ascending=False).round(0).to_csv(OUT / "rma_cause_codes.csv")

col = pd.concat(rows)
sob = pd.concat(sob_rows)
pan = col.merge(sob, on=["fips", "year"], how="outer")
pan["has_col"] = pan["indem_total"].notna()
pan["has_sob"] = pan["liab"].notna()
pan.to_parquet(OUT / "rma_county_year.parquet", index=False)
pd.DataFrame(drops).to_csv(OUT / "rma_dropped_other_counties.csv", index=False)

# kiểm tra chéo: tổng bồi thường COL (hạt thật) vs SOB
chk = pan.groupby("year")[["indem_total", "sob_indem"]].sum()
chk["ratio_col_sob"] = chk["indem_total"] / chk["sob_indem"]
chk.round(3).to_csv(OUT / "rma_crosscheck_col_vs_sob.csv")
print(chk.round(3))

# tỉ lệ bao phủ trước kỳ: liability TB 2001-05 / doanh thu cây trồng BEA TB 2001-05
bea = []
for f in sorted((FEAS / "external" / "bea" / "extracted").glob("CAINC45_[A-Z][A-Z]_1969_2022.csv")):  # chỉ file theo bang (bỏ file ALL_AREAS)
    d = pd.read_csv(f, encoding="latin1", dtype=str)
    d["GeoFIPS"] = d["GeoFIPS"].str.strip().str.strip('"')
    d = d[(d["LineCode"].str.strip() == "60") & ~d["GeoFIPS"].str.endswith("000")]
    bea.append(d[["GeoFIPS"] + [str(y) for y in range(2001, 2006)]])
bea = pd.concat(bea)
for y in range(2001, 2006):
    bea[str(y)] = pd.to_numeric(bea[str(y)], errors="coerce")  # (D) = không công bố → NaN, không điền 0
bea["crop_rec_0105_usd"] = bea[[str(y) for y in range(2001, 2006)]].mean(axis=1, skipna=False) * 1000
pre = sob[sob["year"].between(2001, 2005)].groupby("fips")["liab"].agg(["mean", "count"]).rename(columns={"mean": "liab_0105", "count": "n_years_sob"})
cov = pre.reset_index().merge(bea[["GeoFIPS", "crop_rec_0105_usd"]].rename(columns={"GeoFIPS": "fips"}), on="fips", how="left")
cov["coverage_ratio_0105"] = cov["liab_0105"] / cov["crop_rec_0105_usd"].where(cov["crop_rec_0105_usd"] > 0)  # mẫu số 0 hoặc (D) → NaN, không điền
cov.to_csv(OUT / "rma_coverage_ratio.csv", index=False)
print(cov["coverage_ratio_0105"].describe())
assert cov["fips"].is_unique
print("hạt có tỉ lệ:", cov["coverage_ratio_0105"].notna().sum(), "/", len(cov))
log_run("10_process_rma: xong; panel hạt-năm RMA 2001-2022, bảng mã nguyên nhân, kiểm tra chéo COL vs SOB, tỉ lệ bao phủ 2001-05 (`out/rma_*.csv|parquet`).")
