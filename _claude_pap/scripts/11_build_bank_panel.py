"""11_build_bank_panel.py — panel ngân hàng-năm cho họ C, D, pass-through, H5, thất bại và robustness.
Đầu ra: out/bank_panel.parquet, out/bank_sample_flow.csv, out/bank_scales.json.
Quy ước đã đăng ký trong kế hoạch (mục 5–6):
  - Mẫu cơ sở: ngân hàng cộng đồng 48 bang + DC trong Phase 1, có nhiệt/mưa footprint (tổng trọng số ≥ 0,98, không renormalize),
    đủ controls t−1, có tọa độ hạt trụ sở (SOD t−1). Panel không cân bằng, không impute, không điền 0 cho ô trống.
  - Kết cục (đơn vị: điểm %, ×100): hiệu số Y(t+h) − Y(t−1) cho tồn lượng; tích lũy Σ_{k=0..h} cho dòng (chia dư nợ danh mục t−1).
  - Ngân hàng nông nghiệp = FarmShare_pre ≥ 25% (trung bình 3 quan sát đầu), từ _claude_feasibility/out/02_bank_exposure_group.parquet.
Script này chỉ dựng biến và đếm mẫu; KHÔNG ước lượng hệ số nào.
"""
import json
import numpy as np
import pandas as pd
from _pap_common import *

P1 = DRIVE / "full_obs" / "phase1" / "phase1_community_all_observations_2005_2025-2.parquet"
P2 = DRIVE / "full_obs_2005_25_tmax30" / "PHASE2"
P5 = DRIVE / "full_obs_2005_25_tmax30" / "PHASE5"
H = [0, 1, 2, 3]
flow = []

cols = ["idrssd", "year", "cert", "hq_state", "in_contiguous_us_dc", "total_assets_kusd", "total_loans_kusd", "farmland_loans_kusd",
        "ag_production_loans_kusd", "chargeoffs_ytd_kusd", "recoveries_ytd_kusd", "provision_ytd_kusd", "npl_ratio_current_loans_robust", "roa",
        "equity_to_assets", "loan_growth", "log_total_assets_l1", "liquidity_ratio_l1", "loans_to_assets_l1"]
b = pd.read_parquet(P1, columns=cols)
b = b[b.in_contiguous_us_dc.astype(bool)].drop(columns="in_contiguous_us_dc").drop_duplicates(["idrssd", "year"]).copy()
flow.append(("Phase 1, ngân hàng cộng đồng 48 bang + DC", len(b), b.idrssd.nunique()))
b["netco_kusd"] = b.chargeoffs_ytd_kusd - b.recoveries_ytd_kusd

# FFIEC raw: chất lượng tín dụng nông nghiệp (nghìn USD); ô trống = NaN
f = pd.read_parquet(FEAS / "out" / "07_ffiec_ag_bank_year.parquet")
f["idrssd"] = f["idrssd"].astype(b["idrssd"].dtype)
b = b.merge(f, on=["idrssd", "year"], how="left")
b["npl_farmland"] = b.farmland_pd90 + b.farmland_nonaccrual            # NaN nếu một trong hai trống
b["npl_farm"] = b.farm_pd90 + b.farm_nonaccrual
b["nco_farmland"] = b.farmland_chargeoff - b.farmland_recovery
b["nco_farm"] = b.farm_chargeoff - b.farm_recovery
b["npl_both"] = b.npl_farmland + b.npl_farm
b["nco_both"] = b.nco_farmland + b.nco_farm

b = b.set_index(["idrssd", "year"]).sort_index()


def at(col, k):
    """Giá trị col tại năm t+k theo hàng (idrssd, t)."""
    idx = pd.MultiIndex.from_arrays([b.index.get_level_values(0), b.index.get_level_values(1) + k])
    return pd.Series(b[col].reindex(idx).values, index=b.index)


Lf, La, Lt = at("farmland_loans_kusd", -1), at("ag_production_loans_kusd", -1), at("total_loans_kusd", -1)
Lf, La, Lt = Lf.where(Lf > 0), La.where(La > 0), Lt.where(Lt > 0)
Y = {}
for h in H:
    def cum(col):
        s = sum(at(col, k) for k in range(h + 1))   # NaN nếu thiếu bất kỳ năm nào
        return s
    Y[f"C1_h{h}"] = 100 * (at("npl_farmland", h) - at("npl_farmland", -1)) / Lf       # Δ(90+ & nonaccrual) farmland / farmland t−1
    Y[f"C2_h{h}"] = 100 * cum("nco_farmland") / Lf                                     # net charge-off tích lũy farmland
    Y[f"C3_h{h}"] = 100 * (at("npl_farm", h) - at("npl_farm", -1)) / La                # vay sản xuất nông nghiệp (farm loans)
    Y[f"C4_h{h}"] = 100 * cum("nco_farm") / La
    Y[f"D1_h{h}"] = 100 * (at("ag_production_loans_kusd", h) - at("ag_production_loans_kusd", -1)) / Lt   # H4 chính
    Y[f"D2_h{h}"] = 100 * (at("farmland_loans_kusd", h) - at("farmland_loans_kusd", -1)) / Lt               # H4 phụ
    # tổn thất tín dụng nông nghiệp bằng nghìn USD (tử số pass-through) và dạng tỷ lệ trên (farmland + vay sản xuất) t−1
    loss = cum("nco_both") + (at("npl_both", h) - at("npl_both", -1))
    Y[f"LOSS_kusd_h{h}"] = loss
    Y[f"LOSS_pct_h{h}"] = 100 * loss / (Lf + La)
    # thứ cấp
    Y[f"S_pd30_farmland_h{h}"] = 100 * (at("farmland_pd30_89", h) - at("farmland_pd30_89", -1)) / Lf
    Y[f"S_npl_total_h{h}"] = 100 * (at("npl_ratio_current_loans_robust", h) - at("npl_ratio_current_loans_robust", -1))
    Y[f"S_roa_h{h}"] = 100 * (at("roa", h) - at("roa", -1))
    Y[f"S_ea_h{h}"] = 100 * (at("equity_to_assets", h) - at("equity_to_assets", -1))
    Y[f"S_loan_growth_h{h}"] = 100 * (at("total_loans_kusd", h) - at("total_loans_kusd", -1)) / Lt
    Y[f"S_prov_cum_h{h}"] = 100 * cum("provision_ytd_kusd") / Lt
Y = pd.DataFrame(Y).replace([np.inf, -np.inf], np.nan)
bank = b[["cert", "hq_state", "total_assets_kusd", "log_total_assets_l1", "liquidity_ratio_l1", "loans_to_assets_l1", "equity_to_assets"]].copy()
bank["farmland_l1"], bank["agprod_l1"], bank["totloans_l1"] = Lf, La, Lt
bank = pd.concat([bank, Y], axis=1).reset_index()

# nhiệt và mưa footprint (cùng quy tắc: Σ trọng số tiền gửi t−1 × giá trị hạt)
hh = pd.read_parquet(TAB / "bank_year_heat.parquet", columns=["idrssd", "year", "wsum", "gdd", "p90", "single_county_main_flag"])
pp = pd.read_parquet(TAB / "bank_year_ppt.parquet", columns=["idrssd", "year", "ppt_season_z"])
hh["idrssd"] = hh["idrssd"].astype(bank["idrssd"].dtype); pp["idrssd"] = pp["idrssd"].astype(bank["idrssd"].dtype)
bank = bank.merge(hh, on=["idrssd", "year"], how="left").merge(pp, on=["idrssd", "year"], how="left")
bank = bank[bank.wsum.notna() & (bank.wsum >= 0.98)]
flow.append(("Có nhiệt footprint (tổng trọng số ≥ 0,98)", len(bank), bank.idrssd.nunique()))

# lead của nhiệt (placebo): nhiệt năm t+k (k = 1..3) của cùng ngân hàng
for k in (1, 2, 3):
    nxt = hh[["idrssd", "year", "gdd"]].copy(); nxt["year"] -= k
    bank = bank.merge(nxt.rename(columns={"gdd": f"gdd_lead{k}"}), on=["idrssd", "year"], how="left")
# thước đo nhiệt phụ cấp ngân hàng: số ngày > 32°C mùa vụ (feasibility 03) và heat excess P90 (gộp footprint từ hạt)
g32 = pd.read_parquet(FEAS / "out" / "03_bank_year_season_heat.parquet", columns=["idrssd", "year", "days_tmax_gt32_season"])
g32["idrssd"] = g32["idrssd"].astype(bank["idrssd"].dtype)
bank = bank.merge(g32.rename(columns={"days_tmax_gt32_season": "gt32"}), on=["idrssd", "year"], how="left")

# tọa độ hạt trụ sở (SOD t−1) và hạt chính của footprint
hq = pd.read_parquet(P2 / "phase2_sod_bank_year.parquet", columns=["idrssd", "analysis_year", "hq_county_fips_l1"]).rename(columns={"analysis_year": "year"})
hq["idrssd"] = hq["idrssd"].astype(bank["idrssd"].dtype)
bank = bank.merge(hq, on=["idrssd", "year"], how="left")
ct = county_centroids().rename(columns={"county_fips": "hq_county_fips_l1", "lat": "hq_lat", "lon": "hq_lon"})
bank = bank.merge(ct, on="hq_county_fips_l1", how="left")
fw = pd.read_parquet(P2 / "phase2_footprint_weights_lag1.parquet", columns=["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"]).rename(columns={"analysis_year": "year"})
fw["idrssd"] = fw["idrssd"].astype(bank["idrssd"].dtype)
fw = fw[fw.deposit_weight_l1 > 0]
cp = pd.read_parquet(OUT / "county_panel.parquet", columns=["fips", "year", "crop_kusd"]).rename(columns={"fips": "county_fips"})
m = fw.merge(cp, on=["county_fips", "year"], how="left")
m["wc"] = m.deposit_weight_l1 * m.crop_kusd
hx = pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips", "year", "total_heatexcess_p90"])
m = m.merge(hx, on=["county_fips", "year"], how="left")
m["wh"] = m.deposit_weight_l1 * m.total_heatexcess_p90
hex_ = m.groupby(["idrssd", "year"]).apply(lambda g: g.wh.sum() if g.loc[g.total_heatexcess_p90.notna(), "deposit_weight_l1"].sum() >= 0.98 * g.deposit_weight_l1.sum() else np.nan,
                                           include_groups=False).rename("hex90").reset_index()
agg = m.groupby(["idrssd", "year"]).apply(lambda g: pd.Series({
    "crop_fp_kusd": (g.wc.sum() if g.loc[g.crop_kusd.notna(), "deposit_weight_l1"].sum() >= 0.98 * g.deposit_weight_l1.sum() else np.nan),
    "fp_county": g.sort_values("deposit_weight_l1", ascending=False).county_fips.iloc[0],
    "fp_wmax": g.deposit_weight_l1.max()}), include_groups=False).reset_index()
bank = bank.merge(agg, on=["idrssd", "year"], how="left").merge(hex_, on=["idrssd", "year"], how="left")

# chia mẫu, division, thrift, nhóm nông nghiệp, vốn đệm trước kỳ
sp = state_split()
bank["division"] = bank.hq_state.map(sp["division"]); bank["half"] = bank.hq_state.map(sp["half"])
th = pd.read_parquet(TAB / "bank_thrift_flag.parquet")[["idrssd", "ots_docket_ever", "entered_2012"]]
th["idrssd"] = th["idrssd"].astype(bank["idrssd"].dtype)
bank = bank.merge(th, on="idrssd", how="left")
gp = pd.read_parquet(FEAS / "out" / "02_bank_exposure_group.parquet")[["farmshare_pre", "group_25", "group_15", "group_35"]].reset_index()
gp["idrssd"] = gp["idrssd"].astype(bank["idrssd"].dtype)
bank = bank.merge(gp, on="idrssd", how="left")
bank["ag25"] = bank.group_25.astype(str).str.startswith("ag")
bank["ag15"] = bank.group_15.astype(str).str.startswith("ag")
bank["ag35"] = bank.group_35.astype(str).str.startswith("ag")
bank["low5"] = bank.group_25.astype(str).str.startswith("low")
# vốn đệm trước kỳ: E/A trung bình 3 quan sát đầu (không dùng tier1_leverage_ratio_robust trước 2015)
ea = bank.dropna(subset=["equity_to_assets"]).sort_values(["idrssd", "year"]).groupby("idrssd").head(3).groupby("idrssd")["equity_to_assets"].agg(["mean", "count"])
ea.columns = ["cap_pre", "cap_pre_n"]
bank = bank.merge(ea, on="idrssd", how="left")
bank.loc[bank.cap_pre_n < 3, "cap_pre"] = np.nan   # cần đủ 3 quan sát

# thất bại: thất bại năm t+1 (CERT_eff = CERT.fillna(OUT_CERT); mã ngân hàng thất bại nằm ở OUT_CERT)
ev = pd.read_parquet(P5 / "fdic_institution_events.parquet", columns=["CERT", "OUT_CERT", "event_year", "failure_event_flag", "CHANGECODE_DESC"])
for c_ in ("CERT", "OUT_CERT"):
    ev[c_] = pd.to_numeric(ev[c_], errors="coerce")
ev["CERT_eff"] = ev.CERT.fillna(ev.OUT_CERT)
fl = ev[(ev.CHANGECODE_DESC == "Failure - Whole Institution") | (pd.to_numeric(ev.failure_event_flag, errors="coerce") == 1)]
fyear = fl.dropna(subset=["CERT_eff"]).groupby("CERT_eff").event_year.min()
bank["cert_num"] = pd.to_numeric(bank.cert, errors="coerce")
bank["fail_year"] = bank.cert_num.map(fyear)
bank["fail_t1"] = (bank.fail_year == bank.year + 1).astype(float).where(bank.year + 1 <= 2024)   # sự kiện FDIC có đến 2024

# điều kiện mẫu cơ sở
ctrl = ["log_total_assets_l1", "liquidity_ratio_l1", "loans_to_assets_l1"]
n0 = len(bank)
bank = bank.dropna(subset=ctrl + ["division", "hq_lat", "gdd", "ppt_season_z"])
flow.append(("Đủ controls t−1, division, tọa độ hạt trụ sở, nhiệt, mưa", len(bank), bank.idrssd.nunique()))
bank = bank[bank.year.between(2006, 2024)].copy()
flow.append(("Năm t 2006–2024 (cắt theo họ ở các script sau)", len(bank), bank.idrssd.nunique()))

sd_gdd, sd_p90 = float(bank.loc[bank.year.between(2006, 2023), "gdd"].std()), float(bank.loc[bank.year.between(2006, 2023), "p90"].std())
bank["heat"] = bank.gdd / sd_gdd
bank["heat_p90"] = bank.p90 / sd_p90
for k in (1, 2, 3):
    bank[f"heat_lead{k}"] = bank[f"gdd_lead{k}"] / sd_gdd
bank["heat_gt32"] = bank.gt32 / float(bank.loc[bank.year.between(2006, 2023), "gt32"].std())
bank["heat_hex90"] = bank.hex90 / float(bank.loc[bank.year.between(2006, 2023), "hex90"].std())
bank["ppt_z2"] = bank.ppt_season_z ** 2
json.dump({"sd_gdd_bank": sd_gdd, "sd_p90_bank": sd_p90}, open(OUT / "bank_scales.json", "w"))

ag = bank[bank.ag25]
flow.append(("Ngân hàng nông nghiệp (FarmShare_pre ≥ 25%)", len(ag), ag.idrssd.nunique()))
flow.append(("… một hạt (single_county_main_flag)", int(ag.single_county_main_flag.fillna(False).astype(bool).sum()), ag[ag.single_county_main_flag.fillna(False).astype(bool)].idrssd.nunique()))
for o in ("C1_h1", "C2_h1", "C3_h1", "C4_h1", "D1_h0", "LOSS_kusd_h1"):
    s = ag[ag[o].notna() & ag.year.between(2006, 2023)]
    flow.append((f"Họ nông nghiệp có {o} quan sát (t 2006–2023)", len(s), s.idrssd.nunique()))
pd.DataFrame(flow, columns=["bước", "bank-năm", "số ngân hàng"]).to_csv(OUT / "bank_sample_flow.csv", index=False)
bank.to_parquet(OUT / "bank_panel.parquet", index=False)
print(pd.DataFrame(flow, columns=["bước", "bank-năm", "số ngân hàng"]).to_string(index=False))
log_run(f"11_build_bank_panel: {len(bank):,} bank-năm, {bank.idrssd.nunique():,} ngân hàng (chỉ dựng biến, không ước lượng).")
