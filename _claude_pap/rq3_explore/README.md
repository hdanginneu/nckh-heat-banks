# rq3_explore — thăm dò cho RQ3 (SAU đóng băng PAP v1; không sửa gì trong scripts/ hay out/ đã đóng băng)
Quy tắc: chỉ tính SE dưới H0 (heat placebo = nhiệt năm t+h+1), KHÔNG ước lượng/ghi hệ số nhiệt thật cho outcome mới, để giữ tính xác nhận cho PAP v2.
- G1_mde_rq3.py / G1_mde_rq3.csv (2026-11-05): MDE80 cho provision, Δ thanh khoản, tăng trưởng tín dụng; FE div×năm vs state×năm; mẫu ag25 vs toàn mẫu.
- G3_allowance_mde.py / G3_allowance_mde.csv (2026-11-05): dựng dALLOW (Δ allowance/dư nợ t−1, từ allowance_legacy_kusd) + provision có điều kiện (control NCO, ΔNPL, allowance trễ); MDE80 theo cùng quy trình. Cũng không ước lượng hệ số nhiệt.
## LỖI DỮ LIỆU PHASE 1 (phát hiện 2026-11-05)
`allowance_to_loans` và `allowance_loans_kusd` bằng ~0 với ngân hàng đã dùng CECL (năm 2023–24 trung bình 0,005 thay vì ~0,013; ngân hàng có allowance_cecl_kusd có trung bình ≈ 0). Trong khi `allowance_legacy_kusd`/dư nợ liên tục (~0,012 ở cả nhóm CECL và không CECL, 2022→2023). Đề xuất: dùng allowance_legacy_kusd làm allowance trên dư nợ; KHÔNG dùng allowance_to_loans cho 2020+. Cần đối chiếu mô tả MDRM trước khi đóng băng.
- G2_E1_decomposition.py / .csv (2026-11-05, THĂM DÒ sau đóng băng): phân rã E1. Cùng mẫu E (44.416 hạt-năm), cùng đặc tả PAP (FE hạt + div×năm, mưa, Conley).
  Kết quả (β cho +1 SD nhiệt, theo baseline doanh thu 2001–05): doanh thu mức −0,237 [−0,346; −0,128]; ln doanh thu −0,134 [−0,173; −0,095];
  E1 (mã 11+12+62) 0,217 [0,134; 0,299]; E2 (mã 12+62) 0,027 [0,017; 0,036]; Drought thuần (mã 11) 0,190 [0,116; 0,264]; tổng mọi nguyên nhân 0,406 [0,209; 0,604].
  Kết luận: "E1 > mất doanh thu" là do so sánh log (−0,125) với tỷ lệ mức; cùng thang mức thì 0,217 vs 0,237 (CI chồng nhau rộng). ~88% E1 là mã Drought; mã nhiệt thuần chỉ ~12%.
  Chưa tính: CI của tỷ lệ bồi thường/mất doanh thu; hiệu ứng giá (BEA là giá×lượng).
- G2b_ratio_bootstrap.py / _output.txt (2026-11-05, THĂM DÒ): bootstrap theo bang (47 cụm, B=500, seed 20261105) cho tỷ lệ bồi thường / |mất doanh thu mức|. E1/loss = 0,914, CI bootstrap [0,562; 1,729]; E2/loss (mã nhiệt thuần) = 0,112 [0,074; 0,183]; P(E1/loss > 0,5) = 0,99; P(>1) = 0,38.
- G4_shock_baseline.py / _output.txt (2026-11-05): dựng lại Shock từ dị thường cấp hạt với CÙNG trọng số t−1 (fixed 1981–2005, roll10, roll20, expand). Chỉ biến nhiệt, không đụng outcome.
  Kết quả: gdd dựng lại = gdd hiện có (corr 1,0000). gdd_anom hiện có ≈ S_fixed nhất quán (corr 0,9998; sd hiệu 2,07 so với sd 93,4) → lỗi trọng số t−1/t−2 có thật (gdd_base không cố định theo ngân hàng: median 4 giá trị, max 18) nhưng nhỏ.
  Không có xu hướng ấm trong 2006–2023 (TB theo năm: −0,14/năm, p=0,95 cho S_fixed). Sau FE bank+div×năm các baseline tương quan 0,98–0,998 với nhau và 0,95–0,97 với gdd mức → chọn baseline không đổi kết quả thực tế.
- G5_coverage_and_interactions.py / G5_output.txt / G5_interaction_mde.csv / bank_coverage_pre.parquet (2026-11-05): biến bao phủ bảo hiểm cấp ngân hàng, tiền xác định (liability/doanh thu cây trồng 2001–05; trọng số tiền gửi của năm phân tích đầu tiên của ngân hàng; cột cov_dep, cov_crop). 7.655/8.254 ngân hàng có giá trị. Chỉ diagnostics + MDE dưới H0; không ước lượng hệ số thật.
