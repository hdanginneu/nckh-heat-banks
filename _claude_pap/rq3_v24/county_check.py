"""Kiểm tra cấp hạt (mô tả, PAP v2.4 mục Phụ): nhiệt → ln doanh thu chăn nuôi, ln doanh thu trồng trọt, thu nhập ròng nông trại; FE hạt + division×năm; SE cụm bang."""
import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"))
from _pap_est import fit_lp
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
L = []
for f in sorted(glob.glob(f"{ROOT}/_claude_feasibility/external/bea/extracted/CAINC45_[A-Z][A-Z]_1969_2022.csv")):
    d = pd.read_csv(f, encoding="latin1", dtype=str); d["fips"] = d.GeoFIPS.str.strip().str.strip('"'); d["line"] = pd.to_numeric(d.LineCode.str.strip(), errors="coerce")
    d = d[d.line.isin([20, 60, 290]) & ~d.fips.str.endswith("000")]
    m = d.melt(id_vars=["fips", "line"], value_vars=[str(y) for y in range(2006, 2023)], var_name="year", value_name="v")
    m["v"] = pd.to_numeric(m.v.str.strip(), errors="coerce"); L.append(m)
B = pd.concat(L); B["year"] = B.year.astype(int); B = B.pivot_table(index=["fips", "year"], columns="line", values="v").reset_index().rename(columns={20: "liv", 60: "crop", 290: "netinc"})
c = pd.read_parquet(f"{ROOT}/_claude_pap/out/county_panel.parquet", columns=["fips", "year", "heat", "ppt_season_z", "ppt_z2", "division", "state"])
s = c.merge(B, on=["fips", "year"]); s["div_year"] = s.division + "_" + s.year.astype(str)
base = s[s.year <= 2010].groupby("fips")[["liv", "crop"]].mean(); s = s.merge((base.liv / (base.liv + base.crop)).rename("livsh"), on="fips")
out = []
for y, sub in (("ln_liv", s[s.liv > 0].assign(ln_liv=lambda d: np.log(d.liv))), ("ln_crop", s[s.crop > 0].assign(ln_crop=lambda d: np.log(d.crop))),
               ("netinc_per_receipts", s.assign(netinc_per_receipts=lambda d: d.netinc / (d.liv + d.crop).where((d.liv + d.crop) > 0)))):
    sub = sub.dropna(subset=[y, "heat", "ppt_season_z"])
    if y == "netinc_per_receipts": lo, hi = sub[y].quantile([.01, .99]); sub[y] = sub[y].clip(lo, hi)
    r = fit_lp(sub, y, ["heat", "ppt_season_z", "ppt_z2"], ["fips", "div_year"], se="cluster", cluster="state")
    out.append(dict(y=y, beta=r["beta"][0], se=r["se"][0], p=r["p"][0], n=r["n"]))
    if y == "netinc_per_receipts":
        sub = sub.dropna(subset=["livsh"]).assign(hx=lambda d: d.heat * d.livsh)
        r = fit_lp(sub, y, ["hx", "heat", "ppt_season_z", "ppt_z2"], ["fips", "div_year"], se="cluster", cluster="state")
        out.append(dict(y="netinc × livestock share", beta=r["beta"][0], se=r["se"][0], p=r["p"][0], n=r["n"]))
O = pd.DataFrame(out); O.to_csv("results/county_check.csv", index=False); print(O.round(4).to_string(index=False))
