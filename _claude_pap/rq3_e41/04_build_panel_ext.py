"""04_build_panel_ext.py — panel mở rộng E41: ngân hàng cộng đồng, năm sốc t = 1995–2006, cùng định nghĩa biến với panel_v3.
Chỉ dựng biến; KHÔNG ước lượng hệ số nhiệt.
  Mẫu: cờ CB = 1 của FDIC tại Q4 năm t (1994–2004); từ 2005 dùng tập Phase 1 (đã là ngân hàng cộng đồng; 02_check_seam (c) cho thấy
       Phase 1 2005 gần trùng CB = 1). Trụ sở ở 48 bang liền kề + DC.
  Bảng tra (idrssd, năm): 1994–2004 từ 01_extract_cr (chỉ bank-năm CB = 1, để "còn trong mẫu" cùng nghĩa với Phase 1); 2005–2025 từ Phase 1 + 07.
  Biến kiểm soát t−1: log tài sản, thanh khoản = (tiền mặt + bán vốn LNH + HTM + AFS)/tài sản, dư nợ/tài sản (khớp Phase 1, 02_check_seam (a)).
  Nhiệt: Σ_c w(b,t,c)·gdd_ex29(c,t) / sd_gdd_bank của MẪU CHÍNH (cùng đơn vị với bài); w từ 03_sod_weights (SOD t−1, mã hạt khai báo).
       Giữ hàng có tổng trọng số trên hạt có nhiệt ≥ 0,98 (như 11_build_bank_panel). Mưa: trung bình có trọng số ppt_season_z; ppt_z2 = bình phương.
  FarmShare_pre: trung bình FarmShare của 3 quan sát CB đầu tiên kể từ 1994 (cùng quy tắc 02_exposure); ag25 = FarmShare_pre ≥ 0,25.
  Z: z_size, z_liq = trung bình 3 hàng đầu của biến kiểm soát t−1; z_lat = vĩ độ tâm hạt trụ sở t−1; chuẩn hoá trên tập ngân hàng của panel mở rộng
     (cùng cách _v2_build, nhưng trên mẫu mới).
  Outcome: đúng công thức add_outcomes của build_v3 (C1 NCOc, C2 ALLOW, C3 PDNAflt, C4 LIQ, C5 AGLt, h = 0..6; mẫu số t−1).
     C3 cần quá hạn 30–89 ngày của đất NN, chỉ có từ Call Report 2001 (cr_coverage.csv) → C3 chỉ có cho t ≥ 2002.
  FS10_l1 = 10 × FarmShare tại t−1 (độ nhạy kiểu R8).
Đầu ra: OUT/panel_e41.parquet, OUT/panel_e41_flow.csv, OUT/W_e41.npz (ma trận trọng số cho hoán vị)."""
import json, sys, os
import numpy as np, pandas as pd, scipy.sparse as sp
from e41_common import ROOT, EXT, OUT, P1F, AG07, TAB, CR_YEARS, T_EXT, CONUS_DC

H = range(0, 7)

def cb_flags():
    F = []
    for y in CR_YEARS:
        f = pd.read_parquet(f"{EXT}/fdic_cb/cb_{y}.parquet"); f = f[f.CB == "1"]
        F.append(pd.DataFrame({"idrssd": pd.to_numeric(f.RSSDID).astype("int64"), "year": y}))
    return pd.concat(F).drop_duplicates()

def lookup():
    cr = pd.read_parquet(f"{OUT}/cr_1994_2004.parquet"); cr["idrssd"] = cr.idrssd.astype("int64")
    cr = cr.merge(cb_flags().assign(cb=1), on=["idrssd", "year"], how="left")
    cr["is_cb"] = cr.cb.fillna(0).astype(bool)
    TA = cr.total_assets_kusd.where(cr.total_assets_kusd > 0)
    cr["liquidity_ratio"] = (cr.cash_and_due_kusd + cr.fed_funds_sold_kusd + cr.htm_securities_kusd + cr.afs_securities_kusd) / TA
    cr["loans_to_assets"] = cr.total_loans_kusd / TA; cr["log_total_assets"] = np.log(TA)
    keep = ["idrssd", "year", "hq_state", "chargeoffs_ytd_kusd", "recoveries_ytd_kusd", "allowance_legacy_kusd", "farmland_loans_kusd",
            "ag_production_loans_kusd", "total_loans_kusd", "liquidity_ratio", "loans_to_assets", "log_total_assets", "is_cb",
            "farmland_pd30_89", "farmland_nonaccrual", "farmland_chargeoff", "farmland_recovery", "farm_chargeoff", "farm_recovery",
            "farm_pd30_89", "farm_nonaccrual"]
    a = cr[keep]
    p = pd.read_parquet(P1F, columns=["idrssd", "year", "hq_state", "chargeoffs_ytd_kusd", "recoveries_ytd_kusd", "allowance_legacy_kusd",
                                      "farmland_loans_kusd", "ag_production_loans_kusd", "total_loans_kusd", "liquidity_ratio", "loans_to_assets",
                                      "log_total_assets"]).drop_duplicates(["idrssd", "year"])
    p["idrssd"] = pd.to_numeric(p.idrssd).astype("int64"); p["hq_state"] = p.hq_state.astype(str); p["is_cb"] = True
    f = pd.read_parquet(AG07); f["idrssd"] = pd.to_numeric(f.idrssd).astype("int64")
    p = p.merge(f, on=["idrssd", "year"], how="left")
    P = pd.concat([a, p[keep]], ignore_index=True)
    assert not P.duplicated(["idrssd", "year"]).any()
    P["nco_tot"] = P.chargeoffs_ytd_kusd - P.recoveries_ytd_kusd
    P["pdna_fl"] = P.farmland_pd30_89 + P.farmland_nonaccrual
    P["ag_loans"] = P.farmland_loans_kusd + P.ag_production_loans_kusd
    P["fs"] = P.ag_loans / P.total_loans_kusd.where(P.total_loans_kusd > 0)
    P["present"] = (P.total_loans_kusd.notna() & P.is_cb).astype(float)       # outcome chỉ tính trên bank-năm còn là ngân hàng cộng đồng
    return P.set_index(["idrssd", "year"]).sort_index()

def county_mat(path, col, cty, yrs):
    d = pd.read_parquet(path, columns=["county_fips", "year", col]); d["county_fips"] = pd.to_numeric(d.county_fips).astype(int)
    return d.pivot_table(index="county_fips", columns="year", values=col).reindex(index=cty, columns=yrs).to_numpy()

def main():
    flow = []
    P = lookup()
    cb = P[P.is_cb].reset_index()[["idrssd", "year", "hq_state"]]
    b = cb[cb.year.between(T_EXT[0], T_EXT[1])].copy()
    flow.append(("Ngân hàng cộng đồng, t 1995–2006", len(b), b.idrssd.nunique()))
    b = b[b.hq_state.isin(CONUS_DC)].reset_index(drop=True); flow.append(("Trụ sở 48 bang + DC", len(b), b.idrssd.nunique()))
    ids, yrs = b.idrssd.to_numpy(), b.year.to_numpy()
    at = lambda col, k: P[col].reindex(pd.MultiIndex.from_arrays([ids, yrs + k])).to_numpy()
    for c in ("log_total_assets", "liquidity_ratio", "loans_to_assets"): b[c + "_l1"] = at(c, -1)
    pos = lambda a: np.where(a > 0, a, np.nan)
    b["totloans_l1"], b["farmland_l1"] = pos(at("total_loans_kusd", -1)), pos(at("farmland_loans_kusd", -1))
    b["FS10_l1"] = 10 * at("fs", -1)
    # nhiệt và mưa
    h = pd.read_parquet(f"{TAB}/heat_county_year.parquet", columns=["county_fips"])
    cty = np.sort(pd.to_numeric(h.county_fips.unique()).astype(int)); gy = np.arange(1981, 2026)
    G = county_mat(f"{TAB}/heat_county_year.parquet", "gdd_ex29", cty, gy); Gp = county_mat(f"{TAB}/ppt_county_year.parquet", "ppt_season_z", cty, gy)
    fw = pd.read_parquet(f"{OUT}/fw_1995_2006.parquet")
    k = b[["idrssd", "year"]].copy(); k["row"] = np.arange(len(k))
    m = fw.merge(k, left_on=["idrssd", "analysis_year"], right_on=["idrssd", "year"], how="inner")
    ci = np.searchsorted(cty, m.county_fips.to_numpy()); ok = (ci < len(cty)) & (cty[np.minimum(ci, len(cty) - 1)] == m.county_fips.to_numpy())
    m = m[ok]; ci = ci[ok]
    W = sp.csr_matrix((m.deposit_weight_l1.to_numpy(float), (m.row.to_numpy(), ci)), shape=(len(b), len(cty)))
    sd = json.load(open(f"{ROOT}/_claude_pap/out/bank_scales.json"))["sd_gdd_bank"]
    heat, wsum, rain = np.full(len(b), np.nan), np.zeros(len(b)), np.full(len(b), np.nan)
    for t in np.unique(yrs):
        r = np.where(yrs == t)[0]; g = G[:, t - 1981]; gp = Gp[:, t - 1981]
        av = ~np.isnan(g); wsum[r] = W[r] @ av.astype(float); heat[r] = (W[r] @ np.where(av, g, 0.0)) / sd
        ap = ~np.isnan(gp); den = W[r] @ ap.astype(float); rain[r] = np.where(den > 0, (W[r] @ np.where(ap, gp, 0.0)) / np.where(den > 0, den, 1), np.nan)
    b["heat"], b["wsum"], b["ppt_season_z"] = np.where(wsum > 0, heat, np.nan), wsum, rain; b["ppt_z2"] = b.ppt_season_z ** 2
    # trụ sở t−1, division
    hq = pd.read_parquet(f"{OUT}/hq_1995_2006.parquet"); b = b.merge(hq, on=["idrssd", "year"], how="left")
    sys.path.insert(0, f"{ROOT}/_claude_pap/scripts"); from _pap_common import county_centroids, state_split
    ct = county_centroids(); ct["county_fips"] = pd.to_numeric(ct.county_fips).astype(int)
    b = b.merge(ct.rename(columns={"county_fips": "hq_county_fips_l1", "lat": "hq_lat", "lon": "hq_lon"}), on="hq_county_fips_l1", how="left")
    b["division"] = b.hq_state.map(state_split()["division"])
    # FarmShare_pre: 3 quan sát CB đầu tiên kể từ 1994
    fsd = P[P.is_cb & P.fs.notna()].reset_index()[["idrssd", "year", "fs"]].sort_values(["idrssd", "year"])
    pre = fsd.groupby("idrssd").head(3).groupby("idrssd").agg(farmshare_pre=("fs", "mean"), pre_last_year=("year", "max"))
    b = b.merge(pre, left_on="idrssd", right_index=True, how="left")
    b["FS10"] = 10 * b.farmshare_pre; b["ag25"] = b.farmshare_pre >= 0.25
    # outcome (build_v3.add_outcomes)
    Lt, Lf = b.totloans_l1.to_numpy(), b.farmland_l1.to_numpy(); ids, yrs = b.idrssd.to_numpy(), b.year.to_numpy()
    at = lambda col, k: P[col].reindex(pd.MultiIndex.from_arrays([ids, yrs + k])).to_numpy()
    alive = np.ones(len(b)); flow_nco = 0.0; new = {}
    for hh in H:
        alive = alive * np.where(at("present", hh) == 1, 1.0, np.nan); flow_nco = flow_nco + at("nco_tot", hh)
        new[f"alive_h{hh}"] = np.nan_to_num(alive)
        new[f"NCOc_h{hh}"] = alive * 100 * flow_nco / Lt
        new[f"ALLOW_h{hh}"] = alive * 100 * (at("allowance_legacy_kusd", hh) - at("allowance_legacy_kusd", -1)) / Lt
        new[f"PDNAflt_h{hh}"] = alive * 100 * (at("pdna_fl", hh) - at("pdna_fl", -1)) / Lt
        new[f"LIQ_h{hh}"] = alive * 100 * (at("liquidity_ratio", hh) - at("liquidity_ratio", -1))
        new[f"AGLt_h{hh}"] = alive * 100 * (at("ag_loans", hh) - at("ag_loans", -1)) / Lt
    b = pd.concat([b, pd.DataFrame(new, index=b.index).replace([np.inf, -np.inf], np.nan)], axis=1)
    b["cecl_first"] = np.nan; b["Dr"] = np.nan
    # lọc mẫu cơ sở (như 11_build_bank_panel)
    ctrl = ["log_total_assets_l1", "liquidity_ratio_l1", "loans_to_assets_l1"]
    keep = b.wsum >= 0.98; flow.append(("Có nhiệt footprint (tổng trọng số ≥ 0,98)", int(keep.sum()), b[keep].idrssd.nunique()))
    keep &= b[ctrl + ["division", "hq_lat", "heat", "ppt_season_z"]].notna().all(axis=1)
    flow.append(("Đủ controls t−1, division, toạ độ trụ sở, nhiệt, mưa", int(keep.sum()), b[keep].idrssd.nunique()))
    b = b[keep].sort_values(["idrssd", "year"]).reset_index(drop=True)
    # Z (như _v2_build: 3 hàng đầu của ngân hàng trong panel; chuẩn hoá trên tập ngân hàng duy nhất)
    g = b.groupby("idrssd")
    for c, nm in (("log_total_assets_l1", "z_size"), ("liquidity_ratio_l1", "z_liq"), ("loans_to_assets_l1", "z_loans")):
        b[nm + "_raw"] = g[c].transform(lambda s: s.iloc[:3].mean())
    b["z_lat_raw"] = b.hq_lat; u = b.drop_duplicates("idrssd")
    for nm in ("z_size", "z_liq", "z_loans", "z_lat"):
        b[nm] = (b[nm + "_raw"] - u[nm + "_raw"].mean()) / u[nm + "_raw"].std()
    b["div_year"] = b.division + "_" + b.year.astype(str)
    flow.append(("Có FarmShare_pre", int(b.FS10.notna().sum()), b[b.FS10.notna()].idrssd.nunique()))
    flow.append(("… ngân hàng nông nghiệp (FarmShare_pre ≥ 25%)", int(b.ag25.sum()), b[b.ag25].idrssd.nunique()))
    for C, y in (("C1", "NCOc_h6"), ("C2", "ALLOW_h6"), ("C3", "PDNAflt_h1"), ("C4", "LIQ_h0"), ("C5", "AGLt_h2")):
        s = b[b[y].notna() & b.FS10.notna()]; flow.append((f"{C}: có {y}", len(s), s.idrssd.nunique()))
    # ma trận W theo đúng thứ tự hàng cuối cùng (cho hoán vị năm thời tiết)
    k = b[["idrssd", "year"]].copy(); k["row"] = np.arange(len(k))
    m = fw.merge(k, left_on=["idrssd", "analysis_year"], right_on=["idrssd", "year"], how="inner")
    ci = np.searchsorted(cty, m.county_fips.to_numpy()); ok = (ci < len(cty)) & (cty[np.minimum(ci, len(cty) - 1)] == m.county_fips.to_numpy())
    m = m[ok]; W = sp.csr_matrix((m.deposit_weight_l1.to_numpy(float), (m.row.to_numpy(), ci[ok])), shape=(len(b), len(cty)))
    hchk = np.array([(W[[i]] @ np.nan_to_num(G[:, t - 1981]))[0] / sd for i, t in zip(range(0, len(b), max(1, len(b) // 500)), b.year.to_numpy()[::max(1, len(b) // 500)])])
    dev = np.nanmax(np.abs(hchk - b.heat.to_numpy()[::max(1, len(b) // 500)]))
    flow.append((f"Kiểm: |nhiệt dựng lại từ W − nhiệt trong panel| lớn nhất (mẫu 500 hàng) = {dev:.2e}", 0, 0))
    sp.save_npz(f"{OUT}/W_e41.npz", W); np.savez(f"{OUT}/G_e41.npz", G=G, Gp=Gp, cty=cty, gy=gy, sd=sd)
    b["idrssd"] = b.idrssd.astype(str)
    b.to_parquet(f"{OUT}/panel_e41.parquet", index=False)
    F = pd.DataFrame(flow, columns=["bước", "bank-năm", "số ngân hàng"]); F.to_csv(f"{OUT}/panel_e41_flow.csv", index=False)
    pd.set_option("display.width", 200); print(F.to_string(index=False))
    print(b.groupby("year").agg(n=("idrssd", "size"), ag25=("ag25", "mean"), heat=("heat", "mean"), LIQ0=("LIQ_h0", "mean"), PDNA1=("PDNAflt_h1", lambda s: s.notna().mean())).round(3).to_string())

if __name__ == "__main__":
    main()
