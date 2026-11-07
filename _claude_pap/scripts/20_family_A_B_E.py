"""20_family_A_B_E.py — họ A (first stage), B (trợ cấp), E (bồi thường RMA) cấp hạt-năm; sau đó first stage USD theo footprint (SESOI).
Đặc tả (kế hoạch mục 6.2): y(c,t) = β·Nhiệt(c,t) + δ1·z_mưa + δ2·z_mưa² + α_c + τ_(division,t); Nhiệt = gdd_ex29/SD (hạt-năm 2006–2022).
SE chính: Conley 1.000 km, trễ 2 năm, tọa độ tâm hạt. Báo ba cột: toàn mẫu (chính), nửa A, nửa B.
Kết quả: results/familyABE.csv, results/first_stage_usd.json. Giả thuyết/dấu: H1 β<0 (A), H2 β>0 (B), H6 β>0 (E).
"""
import json
from _pap_est import *

d = load_county()
FAM = [("A", "y_lncrop", "H1: ln doanh thu cây trồng"), ("B", "y_govpay", "H2: trợ cấp CP / doanh thu tiền mặt baseline"),
       ("E1", "y_indem_hd", "H6: bồi thường RMA (hạn+nhiệt+gió nóng) / doanh thu cây trồng baseline"),
       ("E2", "y_indem_heat", "H6 phụ: bồi thường RMA (nhiệt+gió nóng) / doanh thu cây trồng baseline")]
rows = []
for fam, y, label in FAM:
    s = county_frame(d, y)
    for col, sub in halves(s).items():
        r = fit_lp(sub, y, ["heat"] + RAIN, ["fips", "div_year"], se="conley", cty="fips")
        rows.append(record(fam, y, 0, "main", col, r, extra=dict(label=label)))
pd.DataFrame(rows).to_csv(RES / "familyABE.csv", index=False)

# ---- first stage USD theo footprint cho SESOI và mẫu số pass-through (ngân hàng nông nghiệp MỘT HẠT, t 2006–2022)
b = load_bank()
s = b[b.ag25 & b.single_county_main_flag.fillna(False).astype(bool) & b.year.between(2006, 2022)].dropna(subset=["crop_fp_kusd", "heat", "ppt_season_z"] + BANK_CTRL).copy()
s["div_year"] = s.division + "_" + s.year.astype(str)
s["crop_fp_usd"] = s.crop_fp_kusd * 1000.0
r = fit_lp(s, "crop_fp_usd", ["heat"] + RAIN + BANK_CTRL, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
row = record("FS_USD", "crop_fp_usd", 0, "main", "full", r)
json.dump({"beta_fs_usd": float(r["beta"][0]), "se": float(r["se"][0]), "n": int(r["n"]), "sample": "ag25 một hạt, t 2006–2022"}, open(RES / "first_stage_usd.json", "w"))
print(pd.DataFrame(rows)[["family", "sample", "beta", "se", "ci95_lo", "ci95_hi", "n", "n_units"]].round(4).to_string(index=False) if not FAKE else "[FAKE] chạy xong A,B,E, first stage USD")
log_run(f"20_family_A_B_E ({'FAKE' if FAKE else 'THẬT'}): {len(rows)} ước lượng A/B/E + first stage USD.")
