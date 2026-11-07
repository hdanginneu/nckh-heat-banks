"""T2 — tương quan nhiệt t với nhiệt t+1 sau FE (bank + div×năm), và các placebo hai-vế (không dùng hệ số nhiệt thật)."""
from _v2_spec import *
from _pap_common import absorb, codes
b = pd.read_parquet(f"{V2}/out/panel_v2.parquet")
s = frame(b, "dALLOW_h0", True, need_lead=True)
gc = [codes(s[c]) for c in ["idrssd", "div_year"]]
Z = absorb(np.column_stack([s.heat.to_numpy(float), s.heat_lead1.to_numpy(float), (s.heat * s.FS10).to_numpy(float), (s.heat_lead1 * s.FS10).to_numpy(float)]), gc)
print("corr sau FE: heat vs lead1:", np.corrcoef(Z[:, 0], Z[:, 1])[0, 1].round(3), "| heat×FS10 vs lead1×FS10:", np.corrcoef(Z[:, 2], Z[:, 3])[0, 1].round(3))
# placebo hai-vế: y trên heat_t-terms VÀ lead-terms đồng thời. Chỉ đọc hệ số lead (đúng dạng placebo); KHÔNG in hệ số heat_t.
s2 = s.copy()
for hv, pre in (("heat", ""), ("heat_lead1", "L")):
    s2[pre + "x_fs"] = s2[hv] * s2.FS10
    for z in Z_INT: s2[pre + "x_" + z[2:]] = s2[hv] * s2[z]
xs = ["Lx_fs", "heat_lead1"] + ["Lx_" + z[2:] for z in Z_INT] + ["x_fs", "heat"] + ["x_" + z[2:] for z in Z_INT] + RAIN + BANK_CTRL + COND
for se in ("conley", "state"):
    if se == "conley": r = fit_lp(s2, "dALLOW_h0", xs, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
    else: r = fit_lp(s2, "dALLOW_h0", xs, ["idrssd", "div_year"], se="cluster", cluster="hq_state")
    print(f"placebo hai-vế dALLOW|cond [{se}]: lead×FS10 b={r['beta'][0]:.4f} se={r['se'][0]:.4f} t={r['beta'][0]/r['se'][0]:.2f}")
