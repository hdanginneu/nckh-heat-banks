"""_v2_build.py — dựng panel phân tích RQ3 (PAP v2). Chỉ dựng biến; KHÔNG ước lượng hệ số nhiệt.
Đầu ra: out/panel_v2.parquet. Dùng chung _pap_est (đã đóng băng ở v1) để cùng định nghĩa heat, mưa, controls, FE."""
import sys, os
S = os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"); sys.path.insert(0, S)
from _pap_est import *
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
V2 = os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v2")
P1 = f"{ROOT}/_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet"
SPECS_V2 = f"{V2}/out/specs_run_v2.csv"

def build():
    cols = ["idrssd", "year", "allowance_legacy_kusd", "allowance_cecl_kusd", "chargeoffs_ytd_kusd", "recoveries_ytd_kusd",
            "provision_ytd_kusd", "liquidity_ratio", "cash_and_due_kusd", "htm_securities_kusd", "afs_securities_kusd", "total_assets_kusd"]
    p = pd.read_parquet(P1, columns=cols).drop_duplicates(["idrssd", "year"])
    b = load_bank().merge(p, on=["idrssd", "year"], how="left", suffixes=("", "_p"))
    b = b.sort_values(["idrssd", "year"]).reset_index(drop=True)
    L1 = b["totloans_l1"]
    v = b.groupby("idrssd")["allowance_legacy_kusd"].shift(1); yr = b.groupby("idrssd")["year"].shift(1)
    Am1 = pd.Series(np.where(yr == b.year - 1, v, np.nan), index=b.index)
    b["NCO_h0"] = 100 * (b.chargeoffs_ytd_kusd - b.recoveries_ytd_kusd) / L1
    b["dALLOW_h0"] = 100 * (b.allowance_legacy_kusd - Am1) / L1
    b["ALLOWlag"] = 100 * Am1 / L1
    # ΔLIQ_h0 = liquidity_ratio(t) − liquidity_ratio(t−1); liquidity_ratio_l1 là giá trị năm t−1 theo hàng của năm t
    b["dLIQ_h0"] = 100 * (b["liquidity_ratio"] - b["liquidity_ratio_l1"])
    def at1(col):   # giá trị tại năm t+1 nếu năm liền kề
        v = b.groupby("idrssd")[col].shift(-1); y1 = b.groupby("idrssd")["year"].shift(-1)
        return pd.Series(np.where(y1 == b["year"] + 1, v, np.nan), index=b.index)
    b["dALLOW_h1"] = 100 * (at1("allowance_legacy_kusd") - Am1) / L1
    b["dLIQ_h1"] = 100 * (at1("liquidity_ratio") - b["liquidity_ratio_l1"])
    first = b[b.allowance_cecl_kusd.notna()].groupby("idrssd").year.min()
    b["cecl_adopt_year"] = (b.year == b.idrssd.map(first)).astype(float)
    b["cecl_post"] = (b.year >= b.idrssd.map(first)).astype(float)
    # biến tiền xác định cấp ngân hàng: trung bình 3 quan sát đầu (cùng quy ước FarmShare_pre)
    b["FS10"] = b.farmshare_pre * 10
    g = b.groupby("idrssd")
    for c, nm in (("log_total_assets_l1", "z_size"), ("liquidity_ratio_l1", "z_liq"), ("loans_to_assets_l1", "z_loans")):
        pre = g[c].transform(lambda s: s.iloc[:3].mean())
        b[nm + "_raw"] = pre
    b["z_lat_raw"] = b["hq_lat"]
    cov = pd.read_parquet(f"{ROOT}/_claude_pap/rq3_explore/bank_coverage_pre.parquet")
    cov["idrssd"] = cov.idrssd.astype(b.idrssd.dtype)
    b = b.merge(cov[["idrssd", "cov_dep"]], on="idrssd", how="left")
    # chuẩn hoá cấp ngân hàng (mỗi ngân hàng một giá trị) trên tập ngân hàng duy nhất
    u = b.drop_duplicates("idrssd")
    for nm in ("z_size", "z_liq", "z_loans", "z_lat"):
        m, s = u[nm + "_raw"].mean(), u[nm + "_raw"].std()
        b[nm] = (b[nm + "_raw"] - m) / s
    # bao phủ bảo hiểm: cắt ở p99 theo ngân hàng rồi chuẩn hoá (quy tắc PAP v2)
    cap = u.cov_dep.quantile(0.99); cd = b.cov_dep.clip(upper=cap); uc = cd[u.index] if False else b.drop_duplicates("idrssd").cov_dep.clip(upper=cap)
    b["Cov"] = (cd - uc.mean()) / uc.std()
    # nhị phân theo ngưỡng và bin FarmShare_pre (độ nhạy)
    b["ag15f"], b["ag25f"], b["ag35f"] = [b[c].astype(float) for c in ("ag15", "ag25", "ag35")]
    fs = b.farmshare_pre
    b["bin2"] = ((fs > .05) & (fs <= .15)).astype(float); b["bin3"] = ((fs > .15) & (fs <= .25)).astype(float)
    b["bin4"] = ((fs > .25) & (fs <= .35)).astype(float); b["bin5"] = (fs > .35).astype(float)
    return b

if __name__ == "__main__":
    b = build()
    b.to_parquet(f"{V2}/out/panel_v2.parquet", index=False)
    print(b.shape, b.idrssd.nunique())
