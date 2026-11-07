"""T0_checks.py — kiểm tra kỹ thuật trước đóng băng. Không ước lượng hệ số nhiệt."""
import pandas as pd, numpy as np, os
V2 = os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v2")
b = pd.read_parquet(f"{V2}/out/panel_v2.parquet")
pd.set_option("display.width", 200)
print("== 1. CECL: năm đầu có allowance_cecl_kusd (theo ngân hàng) ==")
f = b[b.allowance_cecl_kusd.notna()].groupby("idrssd").year.min()
print(f.value_counts().sort_index().to_dict())
print("== tỷ lệ hàng có allowance_cecl notna / allowance_legacy notna, theo năm ==")
t = b.groupby("year").agg(cecl=("allowance_cecl_kusd", lambda s: s.notna().mean()), legacy=("allowance_legacy_kusd", lambda s: s.notna().mean()),
        both=("allowance_cecl_kusd", lambda s: (s.notna() & b.loc[s.index, "allowance_legacy_kusd"].notna()).mean()))
print(t.round(3).tail(8).to_string())
b["al_ratio"] = 100 * b.allowance_legacy_kusd / b.totloans_l1
print("== trung vị allowance_legacy/dư nợ_{t−1} (%) theo năm × cecl_post ==")
print(b[b.year >= 2019].groupby(["year", "cecl_post"]).al_ratio.median().round(3).unstack().to_string())
print("== dALLOW_h0 trung vị theo năm (cecl_post=1 vs 0), 2021–2024 ==")
print(b[b.year >= 2021].groupby(["year", "cecl_post"]).dALLOW_h0.median().round(3).unstack().to_string())
print("== 2. Đồng nhất thức dALLOW ≈ PROV − NCO ==")
x = b[["dALLOW_h0", "S_prov_cum_h0", "NCO_h0", "year"]].dropna(); x = x[(x.S_prov_cum_h0.abs() < 20) & (x.dALLOW_h0.abs() < 20)]
print("corr", np.corrcoef(x.dALLOW_h0, x.S_prov_cum_h0 - x.NCO_h0)[0, 1].round(3), "n", len(x),
      "| hệ số hồi quy dALLOW trên (PROV−NCO):", np.polyfit(x.S_prov_cum_h0 - x.NCO_h0, x.dALLOW_h0, 1).round(3))
xx = x[x.year <= 2022]; print("2006–2022 corr", np.corrcoef(xx.dALLOW_h0, xx.S_prov_cum_h0 - xx.NCO_h0)[0, 1].round(3))
print("== 3. Thanh khoản ==")
liq2 = (b.cash_and_due_kusd + b.htm_securities_kusd.fillna(0) + b.afs_securities_kusd.fillna(0)) / b.total_assets_kusd
y = pd.concat([b.liquidity_ratio, liq2, (b.cash_and_due_kusd + b.afs_securities_kusd.fillna(0)) / b.total_assets_kusd], axis=1).dropna()
print("corr liquidity_ratio vs (cash+htm+afs)/TA:", np.corrcoef(y.iloc[:, 0], y.iloc[:, 1])[0, 1].round(4), "| vs (cash+afs)/TA:", np.corrcoef(y.iloc[:, 0], y.iloc[:, 2])[0, 1].round(4),
      "| max|diff| (cash+htm+afs):", (y.iloc[:, 0] - y.iloc[:, 1]).abs().max().round(5))
nxt = b.groupby("idrssd").liquidity_ratio_l1.shift(-1); yn = b.groupby("idrssd").year.shift(-1)
m = (yn == b.year + 1) & nxt.notna() & b.liquidity_ratio.notna()
print("liquidity_ratio_l1(t+1) == liquidity_ratio(t)? max|diff|:", (nxt[m] - b.liquidity_ratio[m]).abs().max().round(6), "n", int(m.sum()))
print("== 4. Phân phối outcome (đơn vị % dư nợ t−1; dLIQ: điểm % tài sản) ==")
for c in ("S_prov_cum_h0", "NCO_h0", "S_npl_total_h0", "dALLOW_h0", "ALLOWlag", "dLIQ_h0"):
    s = b[(b.year.between(2007, 2022))][c].dropna()
    print(f"{c:16s} n={len(s):6d} mean={s.mean():8.3f} sd={s.std():8.3f} p1={s.quantile(.01):8.3f} p50={s.median():8.3f} p99={s.quantile(.99):8.3f} min={s.min():9.2f} max={s.max():9.2f}")
print("== 5. Mẫu chính 2007–2022: số ngân hàng-năm theo bin FarmShare_pre ==")
s = b[b.year.between(2007, 2022)].dropna(subset=["dALLOW_h0", "heat", "ppt_season_z", "FS10", "log_total_assets_l1", "liquidity_ratio_l1", "loans_to_assets_l1", "S_prov_cum_h0", "dLIQ_h0"])
print(pd.cut(s.farmshare_pre, [-.001, .05, .15, .25, .35, 1.0]).value_counts().sort_index().to_dict(), "| N", len(s), "banks", s.idrssd.nunique())
print("== 6. cov_dep ==")
u = b.drop_duplicates("idrssd")
print(u.cov_dep.describe(percentiles=[.01, .05, .5, .95, .99]).round(3).to_dict())
print("số ngân hàng cov_dep>1:", int((u.cov_dep > 1).sum()), "| cov_dep NaN:", int(u.cov_dep.isna().sum()))
print("== 7. Z tiền xác định: tương quan với FS10 (cấp ngân hàng) ==")
print(u[["FS10", "z_size", "z_liq", "z_loans", "z_lat"]].corr().round(3).to_string())
