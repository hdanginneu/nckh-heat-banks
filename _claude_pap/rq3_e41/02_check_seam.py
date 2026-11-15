"""02_check_seam.py — kiểm chỗ nối 2004 (tự trích) / 2005 (Phase 1) và thang đơn vị 1994–2004. Chỉ kiểm, không sửa dữ liệu.
  (a) Biến 2004 tự trích so với cột *_l1 của hàng 2005 trong Phase 1 (Phase 1 lưu giá trị năm trước): tài sản, dư nợ, thanh khoản,
      dư nợ/tài sản, log tài sản, FarmShare.
  (b) Tổng tài sản tự trích so với ASSET của FDIC (api financials) từng năm — kiểm đơn vị nghìn USD và khớp mã ngân hàng.
  (c) Cờ ngân hàng cộng đồng FDIC (CB) năm 2005 so với tập ngân hàng của Phase 1 năm 2005.
Đầu ra: OUT/check_02.txt"""
import numpy as np, pandas as pd
from e41_common import EXT, OUT, P1F, CR_YEARS

def ratios(d):
    d = d.copy(); TA = d.total_assets_kusd.where(d.total_assets_kusd > 0)
    d["liquidity_ratio"] = (d.cash_and_due_kusd + d.fed_funds_sold_kusd + d.htm_securities_kusd + d.afs_securities_kusd) / TA
    d["loans_to_assets"] = d.total_loans_kusd / TA; d["log_total_assets"] = np.log(TA)
    d["farm_share"] = (d.farmland_loans_kusd + d.ag_production_loans_kusd) / d.total_loans_kusd.where(d.total_loans_kusd > 0)
    return d

def main():
    L = []
    cr = ratios(pd.read_parquet(f"{OUT}/cr_1994_2004.parquet"))
    p = pd.read_parquet(P1F, columns=["idrssd", "year", "total_assets_kusd_l1", "total_loans_kusd_l1", "liquidity_ratio_l1", "loans_to_assets_l1",
                                      "log_total_assets_l1", "farm_share_l1"])
    p = p[p.year == 2005].copy(); p["idrssd"] = pd.to_numeric(p.idrssd)
    m = p.merge(cr[cr.year == 2004].assign(idrssd=lambda x: x.idrssd.astype("int64")), on="idrssd", how="left")
    L.append(f"(a) Ngân hàng Phase 1 năm 2005: {len(p):,}; tìm thấy trong trích 2004: {m.total_assets_kusd.notna().sum():,}")
    for a, b in (("total_assets_kusd_l1", "total_assets_kusd"), ("total_loans_kusd_l1", "total_loans_kusd"), ("liquidity_ratio_l1", "liquidity_ratio"),
                 ("loans_to_assets_l1", "loans_to_assets"), ("log_total_assets_l1", "log_total_assets"), ("farm_share_l1", "farm_share")):
        ok = m[a].notna() & m[b].notna(); d = (m.loc[ok, a] - m.loc[ok, b]).abs(); tol = 1e-6 * np.maximum(1, m.loc[ok, a].abs())
        L.append(f"    {b}: so được {ok.sum():,}; khớp (sai số tương đối ≤ 1e-6) {(d <= tol).mean():.2%}; |lệch| lớn nhất {d.max():.3g}; "
                 f"Phase 1 có mà trích thiếu {int((m[a].notna() & m[b].isna()).sum())}")
    for y in CR_YEARS:
        f = pd.read_parquet(f"{EXT}/fdic_cb/cb_{y}.parquet"); f["RSSDID"] = pd.to_numeric(f.RSSDID); f["ASSET"] = pd.to_numeric(f.ASSET)
        q = cr[cr.year == y].merge(f, left_on="idrssd", right_on="RSSDID", how="inner")
        r = q.total_assets_kusd / q.ASSET
        L.append(f"(b) {y}: khớp mã {len(q):,}/{(cr.year == y).sum():,}; tài sản trích / ASSET FDIC: trung vị {r.median():.4f}, "
                 f"tỷ lệ |lệch| ≤ 0,1%: {(abs(r - 1) <= 1e-3).mean():.2%}; CB=1: {(q.CB == '1').sum():,}")
    f = pd.read_parquet(f"{EXT}/fdic_cb/cb_2005.parquet"); f["CERT"] = pd.to_numeric(f.CERT)
    c = pd.read_parquet(P1F, columns=["idrssd", "year", "cert"]); c = c[c.year == 2005]; c["cert"] = pd.to_numeric(c.cert, errors="coerce")
    mm = c.merge(f, left_on="cert", right_on="CERT", how="left")
    L.append(f"(c) 2005: Phase 1 {len(c):,} ngân hàng; nối theo CERT với FDIC: {mm.CB.notna().sum():,}; trong đó CB=1: {(mm.CB == '1').sum():,}; CB=0: {(mm.CB == '0').sum():,}")
    open(f"{OUT}/check_02.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L))

if __name__ == "__main__":
    main()
