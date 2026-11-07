"""15_mde.py — công suất / MDE cho từng họ, TRƯỚC mốc đóng băng, không ước lượng hệ số nhiệt thật.
SE dưới H0 (β = 0): SE Conley (1.000 km, trễ 2 năm) của hệ số trên một biến nhiệt "giả" có cùng cấu trúc không gian–thời gian với nhiệt thật nhưng
 nằm sau cửa sổ kết cục (nhiệt năm t+h+1, như placebo ở mục 9): đặc tả y hệt đặc tả chính, chỉ đổi biến nhiệt; chỉ ghi lại SE, không ghi/ in hệ số.
 (Phiên bản đầu dùng phần dư của y bỏ nhiệt làm SE0 bị thổi phồng nếu có tín hiệu thật — D1_h0; đã thay bằng placebo-lead trước khi đóng băng. Xem DECISIONS_LOG.)
 MDE 80% (hai phía, 5%) = (1,96 + 0,84) × SE0.  Với họ C (TOST, CI 90%): biên tương đương nhỏ nhất có thể chứng minh khi β = 0 là 1,645 × SE0;
 quy đổi sang USD dư nợ danh mục trung vị để so với SESOI (5 cent × |first stage USD|) sau khi có first stage thật.
Kết quả: out/mde_table.csv. Chỉ đọc kết cục để tính phương sai, không in hệ số.
"""
from _pap_est import *
assert not FAKE, "Chạy MDE trên dữ liệu thật (phương sai thật); không in hệ số."

cdf, b = load_county(), load_bank()
rows = []
for fam, y, label in (("A", "y_lncrop", "ln doanh thu cây trồng"), ("B", "y_govpay", "trợ cấp / doanh thu tiền mặt baseline"),
                      ("E1", "y_indem_hd", "bồi thường RMA nhiệt-hạn / doanh thu cây trồng baseline"), ("E2", "y_indem_heat", "bồi thường RMA nhiệt+gió nóng / baseline")):
    s = county_frame(cdf, y)
    s = s.dropna(subset=["heat_lead1"])
    r = fit_lp(s, y, ["heat_lead1"] + RAIN, ["fips", "div_year"], se="conley", cty="fips"); se0, n = float(r["se"][0]), r["n"]
    rows.append(dict(family=fam, outcome=y, h=0, label=label, n=n, sd_y=float(s[y].std()), se0=se0, mde80=2.8016 * se0, mde80_in_sd_y=2.8016 * se0 / float(s[y].std()),
                     equiv_margin_min=Z90 * se0, equiv_margin_min_in_sd_y=Z90 * se0 / float(s[y].std())))
X = ["heat"] + RAIN + BANK_CTRL
for o, hs, port in (("C1", (1, 2), "farmland_l1"), ("C2", (1, 2), "farmland_l1"), ("C3", (1, 2), "agprod_l1"), ("C4", (1, 2), "agprod_l1"), ("D1", (0, 1), "totloans_l1")):
    for h in hs:
        y = f"{o}_h{h}"
        s = bank_frame(b, y, h)
        lead = f"heat_lead{h + 1}"
        s = s.dropna(subset=[lead])
        r = fit_lp(s, y, [lead] + RAIN + BANK_CTRL, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon"); se0, n = float(r["se"][0]), r["n"]
        med = float((s[port] * 1000.0).median())
        rows.append(dict(family=o[0], outcome=y, h=h, label=f"{y} (điểm % dư nợ danh mục t−1)", n=n, sd_y=float(s[y].std()), se0=se0, mde80=2.8016 * se0,
                         mde80_in_sd_y=2.8016 * se0 / float(s[y].std()), equiv_margin_min=Z90 * se0, equiv_margin_min_in_sd_y=Z90 * se0 / float(s[y].std()),
                         median_portfolio_usd=med, equiv_margin_min_usd_per_sd_heat=Z90 * se0 / 100.0 * med))
M = pd.DataFrame(rows)
M["min_first_stage_usd_for_equivalence"] = M["equiv_margin_min_usd_per_sd_heat"] / 0.05   # |β_FS| tối thiểu để SESOI (5 cent) ≥ biên tối thiểu
M.to_csv(OUT / "mde_table.csv", index=False)
print(M[["family", "outcome", "n", "sd_y", "se0", "mde80", "mde80_in_sd_y", "equiv_margin_min", "equiv_margin_min_in_sd_y"]].round(4).to_string(index=False))
log_run("15_mde: bảng MDE theo họ (SE0 Conley, không ước lượng β) → out/mde_table.csv")
