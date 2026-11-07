"""21_family_C_D.py — họ C (tổn thất tín dụng nông nghiệp, kiểm định tương đương TOST) và họ D (điều chỉnh danh mục) ở ngân hàng nông nghiệp.
Đặc tả (kế hoạch mục 6.1): Y(i,t+h) − Y(i,t−1) = β_h·Nhiệt(i,t) + δ·Mưa(i,t) + γ'X(i,t−1) + α_i + τ_(division,t) + ε;
Nhiệt = gdd_ex29 footprint / SD; Mưa = z và z²; X = log tài sản, thanh khoản, dư nợ/tài sản (t−1); mẫu ag25 (FarmShare_pre ≥ 25%).
SE chính: Conley 1.000 km, trễ 2 năm, tọa độ tâm hạt trụ sở. Báo ba cột: toàn mẫu (chính), nửa A, nửa B.
Họ C: C1 farmland NPL, C2 farmland net charge-off, C3 vay sản xuất NPL, C4 vay sản xuất net charge-off; h = 1, 2. H3 đạt khi CI 90% của MỌI cặp
(outcome × horizon) nằm trong ±SESOI_y (intersection-union). SESOI_y = 100 × 0,05 × |β̂_FS,USD| / dư nợ danh mục trung vị (USD) — công thức viết trước,
số tính từ first stage USD (results/first_stage_usd.json). Ngưỡng phụ: ±0,10 SD của Y.
Họ D: D1 = Δ dư nợ vay sản xuất / tổng dư nợ t−1 (H4 chính), h = 0, 1; D2 farmland (phụ).
"""
import json
from _pap_est import *

b = load_bank()
fs = json.load(open(RES / "first_stage_usd.json"))
SESOI_USD = 0.05 * abs(fs["beta_fs_usd"])   # USD tổn thất ngân hàng chấp nhận được cho +1 SD nhiệt
PORT = {"C1": "farmland_l1", "C2": "farmland_l1", "C3": "agprod_l1", "C4": "agprod_l1"}
X = ["heat"] + RAIN + BANK_CTRL
rows, tost_rows = [], []
for o in ("C1", "C2", "C3", "C4"):
    for h in (1, 2):
        y = f"{o}_h{h}"
        s = bank_frame(b, y, h)
        med_loans_usd = float((s[PORT[o]] * 1000.0).median())
        sesoi_y = 100.0 * SESOI_USD / med_loans_usd
        for col, sub in halves(s).items():
            r = fit_lp(sub, y, X, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
            ok, lo, hi = tost(r["beta"][0], r["se"][0], sesoi_y)
            ok2, _, _ = tost(r["beta"][0], r["se"][0], 0.10 * r["sd_y"])
            rows.append(record("C", y, h, "main", col, r, extra=dict(sesoi_y=sesoi_y, sesoi_pass=ok, sesoi_sd10_pass=ok2, med_loans_usd=med_loans_usd,
                                                                     sesoi_usd=SESOI_USD, tost_ci90_lo=lo, tost_ci90_hi=hi)))
C = pd.DataFrame(rows)
full = C[C["sample"] == "full"]
iu = bool(full.sesoi_pass.all())
iu_sd = bool(full.sesoi_sd10_pass.all())
rows_d = []
for o, hs in (("D1", (0, 1)), ("D2", (0, 1))):
    for h in hs:
        y = f"{o}_h{h}"
        s = bank_frame(b, y, h)
        for col, sub in halves(s).items():
            r = fit_lp(sub, y, X, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
            rows_d.append(record("D", y, h, "main", col, r))
C.to_csv(RES / "familyC.csv", index=False)
pd.DataFrame(rows_d).to_csv(RES / "familyD.csv", index=False)
json.dump({"H3_intersection_union_sesoi": iu, "H3_intersection_union_sd10": iu_sd, "n_pairs": int(len(full)), "sesoi_usd": SESOI_USD}, open(RES / "H3_decision.json", "w"))
print("[FAKE] xong C, D" if FAKE else f"H3 IU (SESOI 5c): {iu}; IU (±0,10 SD): {iu_sd}")
log_run(f"21_family_C_D ({'FAKE' if FAKE else 'THẬT'}): {len(C)} ước lượng họ C + {len(rows_d)} họ D.")
