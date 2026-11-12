"""build_v3.py — panel RQ3 v3 (bước S2). CHỈ dựng biến; KHÔNG ước lượng hệ số nhiệt.
Nguyên tắc:
  1. Giữ NGUYÊN mọi cột của panel v2: gọi build() của _v2_build.py (đã đóng băng, không sửa) rồi chỉ THÊM cột.
     Nghiệm thu S2 = mọi cột v2 trong panel_v3 trùng khớp tuyệt đối với rq3_v2/out/panel_v2.parquet (qa_v3.py kiểm).
  2. Outcome cộng dồn từ t−1 đến t+h, h = 0..6, theo quy ước at() của 11_build_bank_panel.py (v1):
     giá trị tại năm t+k lấy theo đúng năm (idrssd, t+k); thiếu bất kỳ năm nào trong [t, t+h] → NaN (cờ alive_h).
     Mẫu số cố định tại t−1 (totloans_l1, farmland_l1, agprod_l1 của bank_panel v1; ≤ 0 → NaN). Không dùng thông tin
     sau t cho biến giải thích; outcome dùng t..t+h theo đúng định nghĩa LP.
  3. Hạn hán cấp ngân hàng = Σ_c w_{b,t,c} · dr(c,t), với cùng trọng số tiền gửi footprint t−1 (phase2_footprint_weights_lag1)
     như nhiệt v2 (_v2_ri.build_W). Kiểm bằng cách dựng lại `heat` từ cùng ma trận W (qa_v3.py).
Đầu ra: ~/mnt/NCKH - NEU/_claude_pap/rq3_v3/out/panel_v3.parquet (không commit)."""
import os, sys
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
for p in (f"{ROOT}/_claude_pap/rq3_v2", f"{ROOT}/_claude_pap/scripts"):
    sys.path.insert(0, p)
from _v2_build import build, P1      # noqa: E402  (code v2 đã đóng băng)
import numpy as np, pandas as pd, scipy.sparse as sp   # noqa: E402

H = list(range(0, 7))
OUTD = f"{ROOT}/_claude_pap/rq3_v3/out"
AG = f"{ROOT}/_claude_feasibility/out/07_ffiec_ag_bank_year.parquet"
FW = f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet"
DR = f"{ROOT}/data_external/usdm/county_year_drought.parquet"
P1COLS = ["idrssd", "year", "chargeoffs_ytd_kusd", "recoveries_ytd_kusd", "allowance_legacy_kusd", "allowance_cecl_kusd",
          "farmland_loans_kusd", "ag_production_loans_kusd", "total_loans_kusd", "liquidity_ratio"]


def lookup(dtype):
    """Bảng (idrssd, năm) 2005–2025 chứa các biến gốc dùng cho outcome v3."""
    p = pd.read_parquet(P1, columns=P1COLS).drop_duplicates(["idrssd", "year"])
    f = pd.read_parquet(AG); f["idrssd"] = f.idrssd.astype(p.idrssd.dtype)
    p = p.merge(f, on=["idrssd", "year"], how="left")
    p["nco_tot"] = p.chargeoffs_ytd_kusd - p.recoveries_ytd_kusd
    p["nco_fl"] = p.farmland_chargeoff - p.farmland_recovery
    p["nco_ag"] = p.nco_fl + (p.farm_chargeoff - p.farm_recovery)          # NaN khi vay sản xuất NN không được báo
    p["pdna_fl"] = p.farmland_pd30_89 + p.farmland_nonaccrual
    p["pdna_ag"] = p.pdna_fl + p.farm_pd30_89 + p.farm_nonaccrual          # bản Thịnh (farmland + vay sản xuất NN)
    p["ag_loans"] = p.farmland_loans_kusd + p.ag_production_loans_kusd
    p["present"] = p.total_loans_kusd.notna().astype(float)
    p["idrssd"] = p.idrssd.astype(dtype)
    return p.set_index(["idrssd", "year"]).sort_index()


def add_outcomes(b, P):
    idx0 = pd.MultiIndex.from_arrays([b.idrssd.to_numpy(), b.year.to_numpy()])

    def at(col, k):
        idx = pd.MultiIndex.from_arrays([idx0.get_level_values(0), idx0.get_level_values(1) + k])
        return pd.Series(P[col].reindex(idx).to_numpy(), index=b.index)

    pos = lambda s: s.where(s > 0)
    Lt, Lf = pos(b.totloans_l1), pos(b.farmland_l1)
    Lag = pos(at("ag_loans", -1))
    new = {}
    alive = pd.Series(1.0, index=b.index)
    flows = {c: 0.0 for c in ("nco_tot", "nco_fl", "nco_ag")}
    for h in H:
        alive = alive * at("present", h).where(lambda s: s == 1)          # NaN nếu thiếu năm t+h (hoặc năm nào trước đó)
        new[f"alive_h{h}"] = alive.fillna(0.0)
        a = alive                                                         # 1 hoặc NaN
        for c in flows: flows[c] = flows[c] + at(c, h)                    # tổng t..t+h; NaN nếu thiếu năm nào
        new[f"NCOc_h{h}"] = a * 100 * flows["nco_tot"] / Lt              # C1 (tên khác NCO_h0 của v2)
        new[f"NCOfl_h{h}"] = a * 100 * flows["nco_fl"] / Lf              # phụ: NCO nợ bảo đảm bằng đất NN
        new[f"NCOag_h{h}"] = a * 100 * flows["nco_ag"] / Lag             # phụ: NCO NN (thiếu theo FarmShare)
        new[f"ALLOW_h{h}"] = a * 100 * (at("allowance_legacy_kusd", h) - at("allowance_legacy_kusd", -1)) / Lt   # C2
        new[f"PDNAfl_h{h}"] = a * 100 * (at("pdna_fl", h) - at("pdna_fl", -1)) / Lf                             # C3 (farmland)
        new[f"PDNAflt_h{h}"] = a * 100 * (at("pdna_fl", h) - at("pdna_fl", -1)) / Lt                            # C3, mẫu số tổng dư nợ
        new[f"PDNAag_h{h}"] = a * 100 * (at("pdna_ag", h) - at("pdna_ag", -1)) / Lag                             # C3 bản Thịnh
        new[f"LIQ_h{h}"] = a * 100 * (at("liquidity_ratio", h) - at("liquidity_ratio", -1))                     # C4
        new[f"AGL_h{h}"] = a * 100 * (at("ag_loans", h) - at("ag_loans", -1)) / Lag                             # C5 (% dư nợ NN t−1)
        new[f"AGLt_h{h}"] = a * 100 * (at("ag_loans", h) - at("ag_loans", -1)) / Lt                            # C5, mẫu số tổng dư nợ
    # Placebo theo thời gian (Thịnh §8.3): outcome TRƯỚC cú sốc, m = 2, 3; dùng y ở t−m..t−1, đều là quá khứ
    for m in (2, 3):
        pre = sum(at("present", -k) for k in range(1, m + 1)).where(lambda s: s == m)          # đủ các năm t−m..t−1
        okp = pre / m
        new[f"PRE_NCOc_m{m}"] = okp * 100 * sum(at("nco_tot", -k) for k in range(2, m + 1)) / Lt
        for nm, col, den in (("ALLOW", "allowance_legacy_kusd", Lt), ("PDNAflt", "pdna_fl", Lt), ("PDNAfl", "pdna_fl", Lf), ("AGL", "ag_loans", Lag), ("AGLt", "ag_loans", Lt)):
            new[f"PRE_{nm}_m{m}"] = okp * 100 * (at(col, -m) - at(col, -1)) / den
        new[f"PRE_LIQ_m{m}"] = okp * 100 * (at("liquidity_ratio", -m) - at("liquidity_ratio", -1))
    for h in range(1, 7):
        new[f"EXIT_h{h}"] = (1 - new[f"alive_h{h}"]).where(new["alive_h0"] == 1)            # attrition (Thịnh §8.4)
    N = pd.DataFrame(new, index=b.index).replace([np.inf, -np.inf], np.nan)
    N["ag_loans_l1"] = Lag
    return N


def add_drought(b):
    fw = pd.read_parquet(FW, columns=["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"])
    fw = fw[(fw.deposit_weight_l1 > 0) & fw.analysis_year.between(2006, 2024)].copy()
    fw["idrssd"] = fw.idrssd.astype(b.idrssd.dtype)
    dr = pd.read_parquet(DR)
    k = b[["idrssd", "year"]].reset_index(drop=True); k["row"] = np.arange(len(k))
    m = fw.merge(k, left_on=["idrssd", "analysis_year"], right_on=["idrssd", "year"], how="inner")
    m = m.merge(dr, left_on=["county_fips", "year"], right_on=["county_fips", "year"], how="left")
    out = {}
    for c in ("dr_d2_wk", "dr_d3_wk"):
        v = np.bincount(m.row, weights=m.deposit_weight_l1 * m[c].fillna(0), minlength=len(k))
        wcov = np.bincount(m.row, weights=m.deposit_weight_l1 * m[c].notna(), minlength=len(k))
        wsum = np.bincount(m.row, weights=m.deposit_weight_l1, minlength=len(k))
        out[{"dr_d2_wk": "Dr", "dr_d3_wk": "Dr3"}[c]] = np.where(wsum > 0, v, np.nan)
        out["Dr_wcov"] = np.where(wsum > 0, wcov / np.where(wsum > 0, wsum, 1), np.nan)
    return pd.DataFrame(out, index=b.index)


def main():
    b = build()                                   # panel v2, không đổi
    v2cols = list(b.columns)
    P = lookup(b.idrssd.dtype)
    N = add_outcomes(b, P)
    D = add_drought(b)
    first = b[b.allowance_cecl_kusd.notna()].groupby("idrssd").year.min()
    C = pd.DataFrame({"cecl_first": b.idrssd.map(first)}, index=b.index)
    C["cecl_early"] = (C.cecl_first <= 2022).astype(float)
    assert not set(N.columns) & set(v2cols), "trùng tên cột v2"
    v3 = pd.concat([b, N, D, C], axis=1)
    assert list(v3.columns[:len(v2cols)]) == v2cols
    os.makedirs(OUTD, exist_ok=True)
    v3.to_parquet(f"{OUTD}/panel_v3.parquet", index=False)
    pd.Series(v2cols).to_csv(f"{OUTD}/v2_columns.csv", index=False, header=["col"])
    print("panel_v3", v3.shape, "ngân hàng", v3.idrssd.nunique(), "năm", v3.year.min(), v3.year.max(), "| cột mới:", v3.shape[1] - len(v2cols))


if __name__ == "__main__":
    main()
