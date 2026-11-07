"""23_H5.py — H5 (thứ cấp, dấu viết trước): ngân hàng có vốn đệm trước kỳ cao hơn có khả năng forbearance lớn hơn.
 (i)  Nhiệt × Vốn đệm ÂM với tổn thất tín dụng nông nghiệp ghi nhận ở h = 1 (LOSS_pct_h1: net charge-off tích lũy + Δ(90+ & nonaccrual), farmland + vay sản xuất, % dư nợ t−1);
 (ii) Nhiệt × Vốn đệm DƯƠNG với Δ dư nợ vay sản xuất / tổng dư nợ t−1 ở h = 0 (D1_h0).
Vốn đệm trước kỳ = E/A trung bình 3 quan sát đầu (cần đủ 3), chuẩn hóa z trong mẫu hồi quy; không dùng tier1_leverage_ratio_robust trước 2015.
Đặc tả = họ C (FE ngân hàng + division×năm, mưa z, z², controls t−1) + Nhiệt×Vốn đệm; SE Conley. Thứ cấp: không điều chỉnh đa so sánh.
"""
from _pap_est import *

b = load_bank()
X0 = ["heat"] + RAIN + BANK_CTRL
rows = []
for y, h, sign in (("LOSS_pct_h1", 1, "âm"), ("D1_h0", 0, "dương")):
    s = bank_frame(b, y, h, extra_dropna=("cap_pre",)).copy()
    s["cap_z"] = (s.cap_pre - s.cap_pre.mean()) / s.cap_pre.std()
    s["heat_x_cap"] = s.heat * s.cap_z
    for col, sub in halves(s).items():
        r = fit_lp(sub, y, ["heat", "heat_x_cap"] + RAIN + BANK_CTRL, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
        rows.append(record("H5", y, h, "heat_x_capital", col, r, j=1, extra=dict(predicted_sign=sign, beta_heat=float(r["beta"][0]), se_heat=float(r["se"][0]))))
pd.DataFrame(rows).to_csv(RES / "H5.csv", index=False)
print("[FAKE] xong H5" if FAKE else pd.DataFrame(rows)[["outcome", "sample", "beta", "se", "ci95_lo", "ci95_hi", "predicted_sign", "n"]].round(4).to_string(index=False))
log_run(f"23_H5 ({'FAKE' if FAKE else 'THẬT'}): {len(rows)} ước lượng.")
