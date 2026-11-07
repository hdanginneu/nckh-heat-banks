# run_log — PAP execution

## 2026-10-15 12:46
- Mục 0: đọc brief và tài liệu; tạo `_claude_pap/`; ghi DECISIONS_LOG.

## 2026-10-15 13:05
- 02_conley_validate: FAIL (max rel diff SE = 2.77e-02) — `out/02_conley_validation.csv`

## 2026-10-15 13:05
- 02_conley_validate: FAIL (max rel diff SE = 2.77e-02) — `out/02_conley_validation.csv`

## 2026-10-15 13:05
- 02_conley_validate: FAIL (max rel diff SE = 2.77e-02) — `out/02_conley_validation.csv`

## 2026-10-15 13:07
- 02_conley_validate: PASS (max rel diff SE = 4.37e-09) — `out/02_conley_validation.csv`

## 2026-10-15 13:10
- 10_process_rma: xong; panel hạt-năm RMA 2001-2022, bảng mã nguyên nhân, kiểm tra chéo COL vs SOB, tỉ lệ bao phủ 2001-05 (`out/rma_*.csv|parquet`).

## 2026-10-15 13:11
- 10_process_rma: xong; panel hạt-năm RMA 2001-2022, bảng mã nguyên nhân, kiểm tra chéo COL vs SOB, tỉ lệ bao phủ 2001-05 (`out/rma_*.csv|parquet`).

## 2026-10-15 14:10 (3.1–3.2)
- Ghi kết quả 3.1 vào DECISIONS_LOG (RC-C đủ; BEA không nhắc bồi thường bảo hiểm; fixest thiếu trễ thời gian).
- `02_conley_validate.py`: PASS (khớp fixest ~1e-9; khớp vét cạn 1e-15). `_pap_common.py`: `conley_vcov`.
- `03_download_rma.py` (44 file, 178 MB, log SHA-256) và `10_process_rma.py` (panel hạt-năm, mã nguyên nhân, kiểm tra chéo, tỉ lệ bao phủ).

## 2026-10-15 13:14
- 10_build_county_panel: 51,833 hạt-năm, 3,049 hạt (không ước lượng gì).

## 2026-10-15 13:16
- 11_build_bank_panel: 107,502 bank-năm, 8,254 ngân hàng (chỉ dựng biến, không ước lượng).

## 2026-10-15 13:16
- 02_conley_validate: PASS (max rel diff SE = 4.37e-09) — `out/02_conley_validation.csv`

## 2026-10-15 13:18
- 20_family_A_B_E (FAKE): 12 ước lượng A/B/E + first stage USD.

## 2026-10-15 13:18
- 20_family_A_B_E (FAKE): 12 ước lượng A/B/E + first stage USD.

## 2026-10-15 13:18
- 21_family_C_D (FAKE): 24 ước lượng họ C + 12 họ D.

## 2026-10-15 13:19
- 21_family_C_D (FAKE): 24 ước lượng họ C + 12 họ D.

## 2026-10-15 13:25
- 22_pass_through (FAKE): 12 ước lượng pass-through, B=999.

## 2026-10-15 13:26
- 20_family_A_B_E (FAKE): 12 ước lượng A/B/E + first stage USD.

## 2026-10-15 13:26
- 21_family_C_D (FAKE): 24 ước lượng họ C + 12 họ D.

## 2026-10-15 13:26
- 23_H5 (FAKE): 6 ước lượng.

## 2026-10-15 13:26
- 24_failures (FAKE): 2 logit, sự kiện [432, 85].

## 2026-10-15 13:27
- 10_build_county_panel: 51,833 hạt-năm, 3,049 hạt (không ước lượng gì).

## 2026-10-15 13:28
- 11_build_bank_panel: 107,502 bank-năm, 8,254 ngân hàng (chỉ dựng biến, không ước lượng).

## 2026-10-15 13:33
- 30_robustness (FAKE): 408 dòng đặc tả.

## 2026-10-15 13:44
- 15_mde: bảng MDE theo họ (SE0 Conley, không ước lượng β) → out/mde_table.csv

## 2026-10-15 13:45
- 15_mde: bảng MDE theo họ (SE0 Conley, không ước lượng β) → out/mde_table.csv

## 2026-10-15 13:52
- 22_pass_through (FAKE): 12 ước lượng pass-through, B=999.

## 2026-10-15 13:52
- 50_tables_figures (FAKE): 12 bảng, 4 hình.

## 2026-10-15 (dừng do hết hạn mức sử dụng) — TRẠNG THÁI
- XONG: 3.1 (RC-C, BEA, Conley), 3.2 (RMA 2001–2022), panel hạt/ngân hàng (10, 11), engine (_pap_est.py), 15_mde, 20–24, 30_robustness, 40_multiple_testing, 50_tables_figures; tất cả đã chạy thử TRÊN KẾT CỤC HOÁN VỊ (results_fake). 40 (Romano–Wolf) và 16_size_check có thể còn đang chạy nền / chưa có output cuối — kiểm tra lại.
- CHƯA LÀM: PAP_v1 (.md/.docx), script Tmin (31–33; tải ~37 GB, ước >4 giờ nên cần hỏi Hdang), run_all, đóng băng (SHA-256), FREEZE_NOTE, giai đoạn 2 và 3 (chạy thật, RESULTS_REPORT, đối chiếu số, review sub-agent).
- CHƯA có ước lượng thật nào được xem; mốc đóng băng chưa đặt.
- Lưu ý: bản MDE đầu (null_se) bị thổi phồng bởi tín hiệu → đã thay bằng SE placebo-lead; ghi vào DECISIONS_LOG khi viết PAP.

## 2026-10-15 13:55
- 16_size_check: kích cỡ dưới hoán vị (100 lần/biến) → out/size_check.csv

## 2026-10-15 13:56
- 40_multiple_testing (FAKE): Romano–Wolf B=2000 cho 6 giả thuyết.

## 2026-10-15 21:16
- 10_process_rma: xong; panel hạt-năm RMA 2001-2022, bảng mã nguyên nhân, kiểm tra chéo COL vs SOB, tỉ lệ bao phủ 2001-05 (`out/rma_*.csv|parquet`).

## 2026-10-15 21:16
- 10_build_county_panel: 51,833 hạt-năm, 3,049 hạt (không ước lượng gì).

## 2026-10-15 21:17
- 11_build_bank_panel: 107,502 bank-năm, 8,254 ngân hàng (chỉ dựng biến, không ước lượng).

## 2026-10-15 21:17
- 20_family_A_B_E (FAKE): 12 ước lượng A/B/E + first stage USD.

## 2026-10-15 21:17
- 21_family_C_D (FAKE): 24 ước lượng họ C + 12 họ D.

## 2026-10-15 21:21
- 22_pass_through (FAKE): 12 ước lượng pass-through, B=999.

## 2026-10-15 21:21
- 23_H5 (FAKE): 6 ước lượng.

## 2026-10-15 21:21
- 24_failures (FAKE): 2 logit, sự kiện [432, 85].

## 2026-10-15 21:22
- 30_robustness (FAKE): 408 dòng đặc tả.

## 2026-10-15 21:37
- 40_multiple_testing (FAKE): Romano–Wolf B=2000 cho 6 giả thuyết.

## 2026-10-15 21:37
- 50_tables_figures (FAKE): 13 bảng, 4 hình.

## 2026-10-15 21:37

## 2026-10-15 21:38
- 10_process_rma: xong; panel hạt-năm RMA 2001-2022, bảng mã nguyên nhân, kiểm tra chéo COL vs SOB, tỉ lệ bao phủ 2001-05 (`out/rma_*.csv|parquet`).

## 2026-10-15 21:38
- 10_build_county_panel: 51,833 hạt-năm, 3,049 hạt (không ước lượng gì).

## 2026-10-15 21:39
- 11_build_bank_panel: 107,502 bank-năm, 8,254 ngân hàng (chỉ dựng biến, không ước lượng).

## 2026-10-15 21:39
- 20_family_A_B_E (THẬT): 12 ước lượng A/B/E + first stage USD.

## 2026-10-15 21:40
- 21_family_C_D (THẬT): 24 ước lượng họ C + 12 họ D.

## 2026-10-15 21:45
- 22_pass_through (THẬT): 12 ước lượng pass-through, B=999.

## 2026-10-15 21:45
- 23_H5 (THẬT): 6 ước lượng.

## 2026-10-15 21:45
- 24_failures (THẬT): 2 logit, sự kiện [432, 85].

## 2026-10-15 21:47
- 30_robustness (THẬT): 408 dòng đặc tả.

## 2026-10-15 22:09
- 40_multiple_testing (THẬT): Romano–Wolf B=2000 cho 6 giả thuyết.

## 2026-10-15 22:10
- 50_tables_figures (THẬT): 13 bảng, 4 hình.

## 2026-10-15 22:11
- 10_process_rma: xong; panel hạt-năm RMA 2001-2022, bảng mã nguyên nhân, kiểm tra chéo COL vs SOB, tỉ lệ bao phủ 2001-05 (`out/rma_*.csv|parquet`).

## 2026-10-15 22:11
- 10_build_county_panel: 51,833 hạt-năm, 3,049 hạt (không ước lượng gì).

## 2026-10-15 22:12
- 11_build_bank_panel: 107,502 bank-năm, 8,254 ngân hàng (chỉ dựng biến, không ước lượng).

## 2026-10-15 22:12
- 20_family_A_B_E (THẬT): 12 ước lượng A/B/E + first stage USD.

## 2026-10-15 22:12
- 21_family_C_D (THẬT): 24 ước lượng họ C + 12 họ D.

## 2026-10-15 — Review sub-agent (họ C, D, pass-through)
- Không thấy lỗi dựng biến/công thức; phát hiện SE Conley của D1_h1 do cắt trị riêng âm; sửa RESULTS_REPORT (không đổi code, không có sai khác với kế hoạch).

## 2026-10-15 22:18
- 22_pass_through (THẬT): 12 ước lượng pass-through, B=999.

## 2026-10-15 22:18
- 23_H5 (THẬT): 6 ước lượng.

## 2026-10-15 22:18
- 24_failures (THẬT): 2 logit, sự kiện [432, 85].

## 2026-10-15 22:20
- 30_robustness (THẬT): 408 dòng đặc tả.

## 2026-10-16 01:16
- 40_multiple_testing (THẬT): Romano–Wolf B=2000 cho 6 giả thuyết.

## 2026-10-16 01:16
- 50_tables_figures (THẬT): 13 bảng, 4 hình.

## 2026-10-16 01:16
- 61_check_report_numbers: 9 số không khớp.

## 2026-10-16 — Hoàn tất
- Chạy lại toàn bộ giống hệt lần 1; báo cáo `RESULTS_REPORT.md/.docx`; 61_check_report_numbers: 9 số "không khớp" đều là sai khác làm tròn/seed (đã kiểm tay).

## 2026-10-16 10:02
- 70_post_freeze_E_by_crop (THĂM DÒ, sau đóng băng): họ E tách theo cây.

## 2026-10-16 10:02
- 70_post_freeze_E_by_crop (THĂM DÒ, sau đóng băng): họ E tách theo cây.
