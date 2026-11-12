"""build_drought.py — biến hạn hán cấp hạt × năm từ USDM (đã tải bằng fetch_usdm.py).
Định nghĩa (khung v3, mục 3.1; bảng quyết định, nhóm D):
  dr_d2_wk(c,t) = Σ_tuần (% diện tích hạt c ở D2 trở lên)/100, các tuần có MapDate trong tháng 4–9 của năm t
                  = số tuần D2+ có trọng số diện tích (0..~26). Không đặt ngưỡng.
  dr_d3_wk(c,t) = như trên với D3+ (biến phụ).
Cùng mùa 4–9 với Heat (GDD>29). Brei et al. (2026) dùng tuần ≥D2/≥D3 tháng 5–10: khác mùa, ghi trong hạn chế.
Đầu ra: ~/mnt/NCKH - NEU/data_external/usdm/county_year_drought.parquet"""
import os, glob
import pandas as pd
ROOT = os.path.expanduser("~/mnt/NCKH - NEU"); RAW = f"{ROOT}/data_external/usdm/raw"
fs = sorted(glob.glob(f"{RAW}/*.csv"))
d = pd.concat([pd.read_csv(f, dtype={"FIPS": str}) for f in fs], ignore_index=True)
d["MapDate"] = pd.to_datetime(d.MapDate.astype(str), format="%Y%m%d")
d = d[d.MapDate.dt.month.between(4, 9)].drop_duplicates(["FIPS", "MapDate"])
d["year"] = d.MapDate.dt.year
# Kiểm dạng cộng dồn (D0 ≥ D1 ≥ … ≥ D4). Dòng vi phạm được GIỮ NGUYÊN (không tự sửa nguồn) và ghi ra để báo cáo QA.
bad = d[(d.D1 > d.D0 + 1e-6) | (d.D2 > d.D1 + 1e-6) | (d.D3 > d.D2 + 1e-6) | (d.D4 > d.D3 + 1e-6)]
bad.to_csv(f"{ROOT}/data_external/usdm/usdm_inconsistent_rows.csv", index=False)
print("dòng USDM vi phạm thứ tự cộng dồn (giữ nguyên):", len(bad))
assert len(bad) < 10, "quá nhiều dòng sai dạng cộng dồn: kiểm lại statisticsType"
g = d.groupby(["FIPS", "year"])
out = pd.DataFrame({"dr_d2_wk": g.D2.sum() / 100, "dr_d3_wk": g.D3.sum() / 100, "n_weeks": g.MapDate.nunique()}).reset_index()
out = out.rename(columns={"FIPS": "county_fips"})
out.to_parquet(f"{ROOT}/data_external/usdm/county_year_drought.parquet", index=False)
print(out.shape, out.county_fips.nunique(), out.year.min(), out.year.max())
print(out.groupby("year")[["dr_d2_wk", "dr_d3_wk"]].mean().round(2).T.to_string())
