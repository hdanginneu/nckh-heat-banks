"""10_build_county_panel.py — panel hạt-năm cho họ A (first stage), B (trợ cấp), E (RMA).
Đầu ra: out/county_panel.parquet, out/county_sample_flow.csv, out/county_scales.json.
Quy ước đã đăng ký trong kế hoạch: năm t = 2006–2022; nhiệt = gdd_ex29 (Tmax) cấp hạt; mưa = ppt_season_z (1/4–30/9) và z²;
baseline = trung bình 2001–2005 (phải đủ 5 năm, không điền); đơn vị BEA = nghìn USD; RMA = USD.
Script này KHÔNG ước lượng hệ số nào; chỉ dựng biến và đếm mẫu.
"""
import json
import numpy as np
import pandas as pd
from _pap_common import *

BEA_DIR = FEAS / "external" / "bea" / "extracted"
YEARS = list(range(2001, 2023))
LINES = {10: "cash_total", 60: "crop", 130: "govpay", 290: "netinc"}

flow = []
bea = []
for f in sorted(BEA_DIR.glob("CAINC45_[A-Z][A-Z]_1969_2022.csv")):
    d = pd.read_csv(f, encoding="latin1", dtype=str)
    d["fips"] = d["GeoFIPS"].str.strip().str.strip('"')
    d["line"] = pd.to_numeric(d["LineCode"].str.strip(), errors="coerce")
    d = d[d["line"].isin(LINES) & ~d["fips"].str.endswith("000")]
    for y in YEARS:  # "(D)" và "(NA)" → NaN; không điền 0
        d[str(y)] = pd.to_numeric(d[str(y)].str.strip(), errors="coerce")
    bea.append(d[["fips", "line"] + [str(y) for y in YEARS]])
bea = pd.concat(bea)
long = bea.melt(id_vars=["fips", "line"], var_name="year", value_name="v")
long["year"] = long["year"].astype(int)
long["name"] = long["line"].map(LINES)
b = long.pivot_table(index=["fips", "year"], columns="name", values="v", aggfunc="first", dropna=False).reset_index()
flow.append(("BEA: hạt-năm 2001–2022 (hạt thật, mã không kết thúc 000)", len(b), b.fips.nunique()))

# baseline 2001–05: đủ 5 năm
pre = b[b.year.between(2001, 2005)].groupby("fips").agg(base_crop_kusd=("crop", lambda s: s.mean() if s.notna().all() and len(s) == 5 else np.nan),
                                                        base_cash_kusd=("cash_total", lambda s: s.mean() if s.notna().all() and len(s) == 5 else np.nan))
b = b.merge(pre, on="fips", how="left")
b = b[b.year.between(2006, 2022)].copy()

# nhiệt và mưa (cấp hạt)
h = pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips", "year", "gdd_ex29", "heatdays_p90", "days_gt32_season", "total_heatexcess_p90"]).rename(columns={"county_fips": "fips"})
hl = h[["fips", "year", "gdd_ex29"]]
leads = []
for k in (1, 2, 3):   # nhiệt năm t+k (placebo)
    x = hl.copy(); x["year"] -= k; leads.append(x.rename(columns={"gdd_ex29": f"gdd_lead{k}"}).set_index(["fips", "year"]))
h = h.merge(pd.concat(leads, axis=1).reset_index(), on=["fips", "year"], how="left")
p = pd.read_parquet(TAB / "ppt_county_year.parquet", columns=["county_fips", "year", "ppt_season_z"]).rename(columns={"county_fips": "fips"})
b = b.merge(h, on=["fips", "year"], how="left").merge(p, on=["fips", "year"], how="left")
flow.append(("Sau khi nối nhiệt + mưa (2006–2022)", len(b), b.fips.nunique()))

# địa lý và chia mẫu
sp = state_split()
b["state"] = b.fips.str[:2].map(STATE_FIPS)
b = b[b.state.notna()].copy()
b["division"] = b.state.map(sp["division"])
b["half"] = b.state.map(sp["half"])
ct = county_centroids().rename(columns={"county_fips": "fips"})
b = b.merge(ct, on="fips", how="left")
flow.append(("48 bang + DC, có tâm hạt", int(b.lat.notna().sum()), b[b.lat.notna()].fips.nunique()))
b = b[b.lat.notna()].copy()

# RMA
r = pd.read_parquet(OUT / "rma_county_year.parquet").rename(columns={"year": "year"})
r = r.rename(columns={"fips": "fips"})
b = b.merge(r[["fips", "year", "has_col", "indem_total", "indem_hd_main", "indem_heat_only", "indem_hd_wide", "liab"]], on=["fips", "year"], how="left")
cov = pd.read_csv(OUT / "rma_coverage_ratio.csv", dtype={"fips": str})[["fips", "coverage_ratio_0105"]]
b = b.merge(cov, on="fips", how="left")

# biến kết cục (đơn vị: tỉ lệ so với baseline hoặc log)
b["y_lncrop"] = np.log(b["crop"].where(b["crop"] > 0))                                  # A
b["crop_kusd"] = b["crop"]
b["y_govpay"] = b["govpay"] / b["base_cash_kusd"].where(b["base_cash_kusd"] > 0)       # B: trợ cấp / doanh thu tiền mặt baseline
bc = b["base_crop_kusd"].where(b["base_crop_kusd"] > 0) * 1000.0                         # USD
has = b["has_col"].fillna(False).astype(bool)
b["y_indem_hd"] = (b["indem_hd_main"] / bc).where(has)                                   # E1: không điền 0 khi hạt-năm không có bản ghi RMA
b["y_indem_heat"] = (b["indem_heat_only"] / bc).where(has)                               # E2
b["y_indem_total"] = (b["indem_total"] / bc).where(has)                                  # phụ
b["y_indem_hdwide"] = (b["indem_hd_wide"] / bc).where(has)                               # phụ (robustness)
b["ppt_z2"] = b["ppt_season_z"] ** 2

# chuẩn hóa nhiệt theo SD của hạt-năm 2006–2022 (hằng số, ghi lại)
sd_gdd = float(b["gdd_ex29"].std())
b["heat"] = b["gdd_ex29"] / sd_gdd
b["heat_p90"] = b["heatdays_p90"] / float(b["heatdays_p90"].std())
b["heat_gt32"] = b["days_gt32_season"] / float(b["days_gt32_season"].std())
b["heat_hex90"] = b["total_heatexcess_p90"] / float(b["total_heatexcess_p90"].std())
for k in (1, 2, 3):
    b[f"heat_lead{k}"] = b[f"gdd_lead{k}"] / sd_gdd
scales = {"sd_gdd_county": sd_gdd, "sd_p90_county": float(b["heatdays_p90"].std())}
json.dump(scales, open(OUT / "county_scales.json", "w"))

for nm, col in (("A: ln doanh thu cây trồng", "y_lncrop"), ("B: trợ cấp / baseline", "y_govpay"), ("E1: bồi thường nhiệt-hạn / baseline", "y_indem_hd")):
    ok = b[col].notna() & b["heat"].notna() & b["ppt_season_z"].notna()
    flow.append((f"Mẫu họ {nm}", int(ok.sum()), b[ok].fips.nunique()))
pd.DataFrame(flow, columns=["bước", "hạt-năm", "số hạt"]).to_csv(OUT / "county_sample_flow.csv", index=False)
b.to_parquet(OUT / "county_panel.parquet", index=False)
print(pd.DataFrame(flow, columns=["bước", "hạt-năm", "số hạt"]).to_string(index=False))
log_run(f"10_build_county_panel: {len(b):,} hạt-năm, {b.fips.nunique():,} hạt (không ước lượng gì).")
