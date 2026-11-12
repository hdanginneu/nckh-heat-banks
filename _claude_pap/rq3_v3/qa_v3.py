"""qa_v3.py — kiểm panel_v3 (bước S2). Không ước lượng hệ số nhiệt; chỉ đếm, so khớp, mô tả và tương quan nhiệt–hạn hán.
Đầu ra: rq3_v3/qa/*.csv (nhỏ, commit được) và in tóm tắt."""
import os, sys, json
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
for p in (f"{ROOT}/_claude_pap/rq3_v2", f"{ROOT}/_claude_pap/scripts"):
    sys.path.insert(0, p)
import numpy as np, pandas as pd, scipy.sparse as sp
from _pap_common import codes, absorb, TAB
HERE = os.path.dirname(os.path.abspath(__file__)); QA = f"{HERE}/qa"; os.makedirs(QA, exist_ok=True)
v3 = pd.read_parquet(f"{ROOT}/_claude_pap/rq3_v3/out/panel_v3.parquet")
v2 = pd.read_parquet(f"{ROOT}/_claude_pap/rq3_v2/out/panel_v2.parquet")
rep = {}

# 1. Nghiệm thu S2: cột v2 trùng khớp tuyệt đối
cols = list(v2.columns); assert len(v2) == len(v3)
bad = []
for c in cols:
    a, b = v2[c], v3[c]
    if a.dtype.kind in "fiub" and b.dtype.kind in "fiub":
        na = a.isna().to_numpy() != b.isna().to_numpy(); d = np.nanmax(np.abs(a.to_numpy(float) - b.to_numpy(float))) if a.notna().any() else 0.0
        if na.any() or d > 0: bad.append((c, int(na.sum()), float(d)))
    elif not a.astype(str).equals(b.astype(str)): bad.append((c, -1, np.nan))
rep["v2_cols_checked"] = len(cols); rep["v2_cols_mismatch"] = bad

# 2. Dựng lại heat từ cùng W (kiểm cách cân trọng số dùng cho hạn hán)
h = pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips", "year", "gdd_ex29"])
cty = np.sort(h.county_fips.unique())
G = h.pivot(index="county_fips", columns="year", values="gdd_ex29").reindex(index=cty, columns=range(1981, 2026)).to_numpy()
fw = pd.read_parquet(f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet", columns=["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"])
fw = fw[(fw.deposit_weight_l1 > 0) & fw.analysis_year.between(2006, 2024)].copy(); fw["idrssd"] = fw.idrssd.astype(v3.idrssd.dtype)
k = v3[["idrssd", "year"]].reset_index(drop=True); k["row"] = np.arange(len(k))
m = fw.merge(k, left_on=["idrssd", "analysis_year"], right_on=["idrssd", "year"], how="inner"); m["ci"] = np.searchsorted(cty, m.county_fips.to_numpy())
W = sp.csr_matrix((m.deposit_weight_l1.to_numpy(float), (m.row.to_numpy(), m.ci.to_numpy())), shape=(len(k), len(cty)))
sd = json.load(open(f"{ROOT}/_claude_pap/out/bank_scales.json"))["sd_gdd_bank"]
hr = np.full(len(k), np.nan); yr = k.year.to_numpy()
for t in np.unique(yr):
    s = np.where(yr == t)[0]; hr[s] = (W[s] @ np.nan_to_num(G[:, t - 1981])) / sd
d = np.abs(hr - v3.heat.to_numpy()); rep["heat_rebuild_maxabs"] = float(np.nanmax(d)); rep["heat_rebuild_n"] = int(np.isfinite(d).sum())

# 3. Đồng nhất với định nghĩa v1/v2 trên các dòng cùng có số
def same(a, b):
    ok = v3[a].notna() & v3[b].notna(); return int(ok.sum()), float(np.max(np.abs(v3.loc[ok, a] - v3.loc[ok, b]))) if ok.any() else np.nan
ident = {"NCOc_h0~NCO_h0(v2)": same("NCOc_h0", "NCO_h0"), "LIQ_h0~dLIQ_h0(v2)": same("LIQ_h0", "dLIQ_h0"), "ALLOW_h0~dALLOW_h0(v2)": same("ALLOW_h0", "dALLOW_h0"),
         "ALLOW_h1~dALLOW_h1(v2)": same("ALLOW_h1", "dALLOW_h1"), "LIQ_h1~dLIQ_h1(v2)": same("LIQ_h1", "dLIQ_h1")}
for hh in range(4):
    v3[f"_d{hh}"] = v3[f"D1_h{hh}"] + v3[f"D2_h{hh}"]; ident[f"AGLt_h{hh}~D1+D2_h{hh}(v1)"] = same(f"AGLt_h{hh}", f"_d{hh}")
    v3[f"_c{hh}"] = v3[f"C2_h{hh}"]; ident[f"NCOfl_h{hh}~C2_h{hh}(v1)"] = same(f"NCOfl_h{hh}", f"_c{hh}")
rep["identities"] = ident

# 4. Số quan sát theo outcome × h (cửa sổ cú sốc t ∈ [2007, Tmax]; đủ biến của frame v2: heat, mưa, controls, FS10, Z)
BASE = ["heat", "ppt_season_z", "ppt_z2", "log_total_assets_l1", "liquidity_ratio_l1", "loans_to_assets_l1", "FS10", "z_size", "z_liq", "z_lat"]
ok0 = v3[BASE].notna().all(axis=1)
OUTS = ["NCOc", "ALLOW", "PDNAfl", "PDNAflt", "PDNAag", "LIQ", "AGL", "AGLt", "NCOfl", "NCOag"]
rows = []
for o in OUTS:
    for hh in range(7):
        y = f"{o}_h{hh}"
        for lab, tmax in (("tmax_2024-h", 2024 - hh), ("tmax_2025-h", min(2025 - hh, 2024))):
            s = v3[ok0 & v3.year.between(2007, tmax) & v3[y].notna()]
            rows.append(dict(outcome=o, h=hh, window=lab, t_last=tmax, shock_years=s.year.nunique(), n=len(s), banks=s.idrssd.nunique(),
                             n_fs_gt15=int((s.farmshare_pre > .15).sum())))
obs = pd.DataFrame(rows); obs.to_csv(f"{QA}/obs_by_outcome_h.csv", index=False)
# C2 cửa sổ ≤ 2022 và bỏ NH áp dụng CECL sớm trong cửa sổ
rows = []
for hh in (0, 1, 3, 4, 5, 6):
    s = v3[ok0 & v3.year.between(2007, 2022 - hh) & v3[f"ALLOW_h{hh}"].notna()]
    s2 = s[~(s.cecl_first.between(s.year, s.year + hh))]
    rows.append(dict(h=hh, t_last=2022 - hh, n=len(s), n_drop_early_cecl=len(s) - len(s2), banks=s2.idrssd.nunique()))
pd.DataFrame(rows).to_csv(f"{QA}/obs_C2_cecl_window.csv", index=False)

# 5. Thiếu dữ liệu theo FarmShare_pre: C3 bản farmland vs bản Thịnh (farmland + vay sản xuất NN)
v3["fs_bin"] = pd.cut(v3.farmshare_pre, [-.01, .05, .15, .25, 1.0], labels=["<=5%", "5-15%", "15-25%", ">25%"])
base = v3[ok0 & v3.year.between(2007, 2023)]
cov = base.groupby("fs_bin", observed=True).agg(n=("idrssd", "size"), PDNAfl_h0=("PDNAfl_h0", lambda s: s.notna().mean()),
      PDNAag_h0=("PDNAag_h0", lambda s: s.notna().mean()), NCOag_h0=("NCOag_h0", lambda s: s.notna().mean()), AGL_h0=("AGL_h0", lambda s: s.notna().mean())).round(3)
cov.to_csv(f"{QA}/coverage_by_farmshare.csv")

# 6. Sống sót theo h (attrition) trong cửa sổ có thể quan sát
att = []
for hh in range(1, 7):
    s = v3[ok0 & v3.year.between(2007, 2024 - hh) & (v3.alive_h0 == 1)]
    att.append(dict(h=hh, share_alive=round(float(s[f"alive_h{hh}"].mean()), 4), n=len(s)))
pd.DataFrame(att).to_csv(f"{QA}/attrition.csv", index=False)

# 7. Tương quan nhiệt–hạn hán (thô, và sau khử FE ngân hàng + division×năm như đặc tả)
s = v3[ok0 & v3.Dr.notna() & v3.year.between(2007, 2022)].copy(); s["div_year"] = s.division + "_" + s.year.astype(str)
g = [codes(s.idrssd), codes(s.div_year)]
Z = absorb(s[["heat", "Dr", "Dr3", "ppt_season_z"]].to_numpy(float), g)
cr = dict(raw_heat_Dr=np.corrcoef(s.heat, s.Dr)[0, 1], raw_heat_Dr3=np.corrcoef(s.heat, s.Dr3)[0, 1], raw_Dr_rain=np.corrcoef(s.Dr, s.ppt_season_z)[0, 1],
          fe_heat_Dr=np.corrcoef(Z[:, 0], Z[:, 1])[0, 1], fe_heat_Dr3=np.corrcoef(Z[:, 0], Z[:, 2])[0, 1], fe_Dr_rain=np.corrcoef(Z[:, 1], Z[:, 3])[0, 1],
          fe_heat_rain=np.corrcoef(Z[:, 0], Z[:, 3])[0, 1], n=len(s), Dr_weight_coverage_min=float(s.Dr_wcov.min()))
x = s.assign(hxF=s.heat * s.FS10, dxF=s.Dr * s.FS10)
Zi = absorb(x[["hxF", "dxF"]].to_numpy(float), g); cr["fe_heatxFS10_DrxFS10"] = np.corrcoef(Zi[:, 0], Zi[:, 1])[0, 1]
pd.Series(cr).round(4).to_csv(f"{QA}/heat_drought_corr.csv", header=["value"])
yc = s.groupby("year").apply(lambda d: np.corrcoef(d.heat, d.Dr)[0, 1], include_groups=False).round(3); yc.to_csv(f"{QA}/heat_drought_corr_by_year.csv", header=["corr_heat_Dr"])

# 8. Mô tả outcome (không liên quan nhiệt)
desc = []
for o in OUTS:
    for hh in range(7):
        y = v3.loc[ok0 & v3.year.between(2007, 2024 - hh), f"{o}_h{hh}"].dropna()
        if len(y): desc.append(dict(outcome=o, h=hh, n=len(y), mean=y.mean(), sd=y.std(), p1=y.quantile(.01), p50=y.median(), p99=y.quantile(.99)))
pd.DataFrame(desc).round(4).to_csv(f"{QA}/outcome_describe.csv", index=False)

json.dump(rep, open(f"{QA}/qa_summary.json", "w"), indent=1, default=str, ensure_ascii=False)
print(json.dumps(rep, indent=1, default=str, ensure_ascii=False))
print(obs[obs.window == "tmax_2024-h"].pivot(index="outcome", columns="h", values="n").to_string())
print(cov.to_string()); print(pd.DataFrame(att).to_string(index=False)); print(pd.Series(cr).round(3).to_string())
