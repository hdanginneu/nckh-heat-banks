"""16_size_check.py — hiệu chuẩn kích cỡ kiểm định dưới H0 bằng hoán vị kết cục trong từng năm (seed cố định): tỉ lệ bác bỏ |z| > 1,96 của SE Conley
và SE cụm-bang, cho hạt (A: y_lncrop) và ngân hàng (C2_h1, D1_h0). Chỉ chạy trên kết cục HOÁN VỊ (không dùng kết cục thật). Kết quả: out/size_check.csv.
Lưu ý: hoán vị trong năm phá cả tương quan không gian của kết cục nên là cận cho trường hợp sai số độc lập; đây là kiểm tra code/kích cỡ cơ bản, không thay cho
kiểm tra khi sai số có tương quan không gian (xem DECISIONS_LOG, mục hạn chế).
"""
import sys
import os
os.environ["PAP_FAKE"] = "1"
from _pap_est import *
import _pap_est

R = 100
cdf0 = pd.read_parquet(OUT / "county_panel.parquet"); bdf0 = pd.read_parquet(OUT / "bank_panel.parquet")
rows = []
for rep in range(R):
    cd = _pap_est._permute_within_year(cdf0, ["y_lncrop"], 1000 + rep)
    s = county_frame(cd, "y_lncrop")
    rc = fit_lp(s, "y_lncrop", ["heat"] + RAIN, ["fips", "div_year"], se="conley", cty="fips")
    rs = fit_lp(s, "y_lncrop", ["heat"] + RAIN, ["fips", "div_year"], se="cluster", cluster="state")
    rows.append(dict(rep=rep, y="A", z_conley=rc["beta"][0] / rc["se"][0], z_state=rs["beta"][0] / rs["se"][0]))
    bd = _pap_est._permute_within_year(bdf0, ["C2_h1", "D1_h0"], 2000 + rep, strata=("ag25",))
    for y, h in (("C2_h1", 1), ("D1_h0", 0)):
        s = bank_frame(bd, y, h)
        X = ["heat"] + RAIN + BANK_CTRL
        rc = fit_lp(s, y, X, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
        rs = fit_lp(s, y, X, ["idrssd", "div_year"], se="cluster", cluster="hq_state")
        rows.append(dict(rep=rep, y=y, z_conley=rc["beta"][0] / rc["se"][0], z_state=rs["beta"][0] / rs["se"][0]))
D = pd.DataFrame(rows)
S = D.groupby("y").agg(size_conley=("z_conley", lambda z: float((np.abs(z) > 1.96).mean())), size_state=("z_state", lambda z: float((np.abs(z) > 1.96).mean())),
                       sd_z_conley=("z_conley", "std"), sd_z_state=("z_state", "std"), reps=("rep", "count")).reset_index()
S.to_csv(OUT / "size_check.csv", index=False)
print(S.round(3).to_string(index=False))
log_run("16_size_check: kích cỡ dưới hoán vị (100 lần/biến) → out/size_check.csv")
