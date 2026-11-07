# HANDOFF cho Claude Cowork — Hướng 1: "Ai gánh tổn thất nhiệt trong nông nghiệp?"
*Cập nhật 16/10/2026. Nhóm NCKH NEU (trưởng nhóm Hdang). Ngôn ngữ làm việc: tiếng Việt. Thư mục dự án: `NCKH - NEU` (OneDrive). Tài liệu này tóm tắt toàn bộ những gì đã làm, kết quả, điểm cần thận trọng và việc còn mở.*

## 1. Bối cảnh và câu hỏi
Đề tài: tác động của nắng nóng lên ngân hàng cộng đồng Hoa Kỳ (48 bang + DC, 2005–2025). Hướng đang theo (hướng 1): nhiệt mùa vụ làm giảm doanh thu cây trồng cấp hạt, nhưng tổn thất tín dụng ở ngân hàng nông nghiệp gần như bằng 0. Tổn thất đi đâu: chuyển giao (trợ cấp, bảo hiểm), điều chỉnh danh mục, hoãn tổn thất (forbearance), hay hấp thụ bằng vốn?

Quy tắc xuyên suốt: mọi hệ số là tương quan có điều kiện ("gắn với"), không nhân quả; không impute, không điền 0 cho ô trống; seed cố định 20261015; không chọn đặc tả theo p-value.

## 2. Đã làm (theo thứ tự)
1. Feasibility → EDA (không p-value, chia bang A/B, nửa B chưa mở) → bản nháp pre-analysis plan (PAP) → `PAP_EXECUTION_BRIEF.md` (nhóm chốt 7 quyết định).
2. Xác minh dữ liệu: RC-C vay sản xuất nông nghiệp có ở 100% ngân hàng (nên H4 dùng thước đo này); BEA CAINC45 không nhắc bồi thường bảo hiểm cây trồng (nên bồi thường đo riêng từ RMA, không cộng với dòng trợ cấp 130); `fixest::vcov_conley` không có độ trễ thời gian ⇒ tự cài Conley có trễ (kiểm định khớp `fixest` ~1e-9 và phép tính vét cạn 1e-15).
3. Tải USDA RMA 2001–2022 (44 file, 178 MB, có log SHA-256) từ bản sao `www.rma.usda.gov` (chụp 3/2024) vì máy không phân giải được `pubfs-rma.fpac.usda.gov`.
4. Viết `PRE_ANALYSIS_PLAN_v1` (md + docx), code, chạy thử trên kết cục hoán vị, **đóng băng** (SHA-256) lúc 2026-10-15 21:38.
5. Chạy thật đúng kế hoạch; chạy lại toàn bộ từ đầu cho kết quả **giống hệt** (24 file kết quả, 507 dòng `specs_run.csv`); sub-agent độc lập rà soát code họ C, D, pass-through (không lỗi công thức; phát hiện SE Conley của D1_h1 do cắt trị riêng âm).
6. Phụ lục sau đóng băng (thăm dò): họ E tách theo cây; cách đọc H4/pass-through. Tmin: **không chạy** (≈37 GB, ≈26 giờ; nhóm quyết bỏ).

## 3. Bảy quyết định đã chốt
| # | Quyết định |
|---|---|
| Q1 | FE chính: ngân hàng + division×năm. SE chính: Conley 1.000 km, trễ 2 năm, tọa độ = tâm hạt trụ sở (TIGER INTPTLAT/LON). |
| Q2 | H3 dùng TOST: CI 90% trong ngưỡng kinh tế; intersection-union trên mọi outcome×horizon của họ C; không Romano–Wolf cho H3. |
| Q3 | H3 dùng farmland + vay sản xuất; H4 dùng dư nợ vay sản xuất / tổng dư nợ t−1 (farmland phụ). |
| Q4 | Thrift: giữ toàn mẫu + cờ `ots_docket_ever`; robustness (a) bỏ thrift, (b) chỉ 2012–2025. |
| Q5 | Tải và dùng RMA. |
| Q6 | Bốn họ outcome + pass-through + họ E. Họ C, D: t 2006–2023 (h ≤ 2); họ A, B, E: t 2006–2022 (BEA đến 2022). |
| Q7 | Nhiệt chính `gdd_ex29` (chỉ Tmax). Tmin: robustness định trước nhưng **đã bỏ** (15/10). |

## 4. Giả thuyết và thiết kế (tóm tắt)
- **H1** (họ A): +1 SD nhiệt ⇒ ln doanh thu cây trồng (BEA dòng 60) giảm (β < 0). **H2** (họ B): trợ cấp trực tiếp (dòng 130) / doanh thu tiền mặt baseline tăng. **H6** (họ E): bồi thường RMA do Drought/Heat/Hot Wind (mã 11, 12, 62) / doanh thu cây trồng baseline tăng. **H3** (họ C): tổn thất farmland và vay sản xuất ở ngân hàng nông nghiệp tương đương 0 (TOST; C1–C4 × h = 1, 2). **H4** (họ D): dư nợ vay sản xuất / tổng dư nợ t−1 giảm ở h = 0, phục hồi một phần ở h = 1. **H5** (thứ cấp): Nhiệt × vốn đệm trước kỳ âm với tổn thất h = 1 và dương với Δ dư nợ vay sản xuất h = 0.
- **Đặc tả:** nhiệt chuẩn hóa theo SD; kiểm soát mưa (z và z²); ngân hàng: Y(t+h) − Y(t−1) hoặc tích lũy dòng chảy, controls t−1 (log tài sản, thanh khoản, dư nợ/tài sản). Ngân hàng nông nghiệp = FarmShare_pre ≥ 25%.
- **SESOI:** 5 cent tổn thất ngân hàng trên mỗi USD doanh thu cây trồng mất; SESOI_y = 100 × 0,05 × |β̂ first stage USD| / dư nợ danh mục trung vị. Ngưỡng phụ ±0,10 SD.
- **Pass-through:** PT_h = ảnh hưởng của nhiệt lên tổn thất tín dụng nông nghiệp (USD, tích lũy đến h) / [−ảnh hưởng lên doanh thu cây trồng footprint (USD)]; mẫu chính ngân hàng nông nghiệp một hạt; bootstrap theo cụm bang 999 lần.
- **Đa so sánh:** Romano–Wolf (2.000 lần, cụm bang) trong từng họ A, B, D, E.
- **Mẫu:** hạt A/B/E 51.139 / 51.153 / 44.416 hạt-năm; ngân hàng nông nghiệp 25.403 bank-năm (1.674 ngân hàng), một hạt 13.502 (1.105).

## 5. Kết quả (toàn mẫu là chính)
| Giả thuyết | Kết quả | Kết luận |
|---|---|---|
| H1 (A) | β = −0.1246 (CI95 [−0.1637; −0.0855]), ≈ −11.7%; nửa A −0.093, nửa B −0.132; 24/26 đặc tả loại 0 | **Đạt** |
| H2 (B) | β = 0.0007 (CI95 [−0.0114; 0.0128]), p_RW = 0.858; placebo lệch 0 (−0.010) | Không đạt, họ B yếu |
| H6 (E1/E2) | E1 0.2167 (CI95 [0.1340; 0.2994]); E2 0.0266 ([0.0166; 0.0365]); p_RW 0.001 / 0.002 | **Đạt rất mạnh**, độ lớn đáng ngờ (xem 6) |
| H3 (C) | 8/8 cặp có CI90 trong ±SESOI_y (≈ 8.7–10.0 điểm %); chỉ 2/8 trong ±0.10 SD | Đạt theo ngưỡng đã đăng ký, **ngưỡng rất rộng** |
| Pass-through | h = 1: 0.003 cent/USD (CI95 [−0.671; 0.265]); h = 2: −0.036 ([−1.184; 0.489]) (mẫu chính) | Gần 0; bằng chứng chính cho "ngân hàng gánh rất ít" |
| H4 (D1) | h = 0: −1.193 điểm % (SE cụm-bang 0.245, CI95 [−1.692; −0.694], p_RW = 0.001); h = 1: −0.444 (SE cụm-bang 0.449, CI95 [−1.357; 0.470]) | Đạt ở h = 0 (mạnh vừa phải); "phục hồi ở h = 1" không được ủng hộ |
| H5 | tương tác với tổn thất h = 1: 0.002 ([−0.071; 0.076]); với D1_h0: −0.162 ([−0.288; −0.037]) (dự đoán dương) | Không đạt (ngược dấu) |
| Thất bại (mô tả) | OR mỗi +1 SD nhiệt 1.334 ([1.123; 1.583]; 432 sự kiện); 1.369 ([1.109; 1.690]; 85 sự kiện khi bỏ 2009–2012) | Mô tả, không đủ lực |

Họ E theo cây (thăm dò sau đóng băng): ngô 0.069, bông 0.069, lúa mì 0.033, đậu tương 0.022, cây khác 0.023 (tổng 0.217).

**Áp tiêu chí diễn giải (mục 10 của kế hoạch):** nhánh "câu đố có cơ sở" — doanh thu cây trồng giảm nhưng tổn thất ngân hàng ước lượng gần 0; kênh gợi ý: bồi thường bảo hiểm (H6) và điều chỉnh danh mục (H4 ở h = 0); trợ cấp trực tiếp (H2) và vốn đệm (H5) không được ủng hộ. Dữ liệu hiện có không phân tách được vai trò từng kênh.

## 6. Điểm cần thận trọng (hạn chế quan trọng)
1. **SESOI quá rộng:** 5 cent × |first stage ≈ 19.96 triệu USD| ≈ 1 triệu USD mỗi +1 SD, trong khi dư nợ nông nghiệp trung vị của ngân hàng ≈ 10 triệu USD ⇒ ngân hàng có thể mất ≈ 10% danh mục mà vẫn "tương đương". Vì vậy dùng pass-through làm bằng chứng chính.
2. **Họ E bất thường:** bồi thường tăng 0.217 lần doanh thu baseline, lớn hơn mức doanh thu mất (≈ 0.117 lần). Chưa rõ nguyên nhân (bảo hiểm gồm cây ngoài BEA "cash receipts: crops"; hạn lan rộng; định nghĩa). Chưa nên công bố con số này.
3. **Họ B** khác kết quả feasibility (FE division×năm + mưa); placebo lệch 0.
4. **SE Conley:** dưới hoán vị, tỷ lệ bác bỏ giả thuyết sai 8% (A), 7% (C2_h1), 14% (D1_h0) thay vì 5%; SE Conley của D1_h1 (0.083) là sản phẩm cắt trị riêng âm so với SE cụm 0.36–0.45 ⇒ đọc H4 theo SE cụm/p_RW.
5. **H4 h = 0 không đồng đều:** nửa A không có hiệu ứng (−0.37), nửa B −1.42; bỏ division West North Central cho −0.62 (CI [−1.42; 0.17]); nhiệt P90 và > 32°C cho CI chứa 0.
6. **Dữ liệu:** chỉ Tmax; BEA đến 2022; RMA từ bản chụp 3/2024 (không có 2023–2025); bố cục cột `sobcov` suy ra từ dữ liệu; thrift trước 2012; vay sản xuất bị cắt theo ngưỡng báo cáo; ngân hàng chỉ nắm một phần nợ nông nghiệp của hạt ⇒ PT là cận dưới.
7. Công cụ đối chiếu số trong báo cáo (`61_check_report_numbers.py`) yếu (tập giá trị quá dày); 9 cảnh báo đều là sai khác làm tròn/seed, đã kiểm tay.
8. Báo cáo `.docx` tạo bằng `docxlite.py` (không có LibreOffice/pandoc) nên chưa kiểm tra hiển thị bằng mắt.

## 7. Việc còn mở / câu hỏi cho nhóm
- Tiếp tục điều tra độ lớn họ E (đối chiếu RMA với BEA ở vài hạt lớn, tách theo cây/cause) hay để sau?
- Có thay SESOI bằng ngưỡng chặt hơn (ví dụ trần theo % dư nợ danh mục) trong một phân tích sau đóng băng được gắn nhãn thăm dò?
- Wild bootstrap theo bang cho H4 và họ C (thay Conley) nếu cần suy luận chặt hơn.
- Tmin (không bắt buộc): chỉ làm nếu nhóm đồng ý tải ≈ 37 GB / ≈ 26 giờ.
- Việc đã hoãn theo yêu cầu của Hdang: dọn OneDrive (zip gốc ≈ 5.6 GB, `_drive_latest`, `external/prism_ppt`, `PRISM_Phase3` 37 GB) — **chưa động tới**.

## 8. Bản đồ file (đường dẫn tương đối từ `NCKH - NEU/`)
- Kế hoạch đóng băng: `_claude_eda/PRE_ANALYSIS_PLAN_v1.md/.docx`; hash: `_claude_pap/FREEZE_NOTE.md`, `hashes_frozen.json`.
- Báo cáo kết quả: `_claude_pap/RESULTS_REPORT.md/.docx`; phụ lục sau đóng băng: `_claude_pap/POST_FREEZE_ADDENDUM.md`.
- Nhật ký quyết định: `_claude_eda/DECISIONS_LOG.md`; nhật ký chạy: `_claude_pap/run_log.md`; mọi đặc tả đã chạy: `_claude_pap/specs_run.csv`.
- Kết quả: `_claude_pap/out/results/` (csv, `tables/`, `figs/`), bản chạy lần 1 để so sánh: `out/results_run1/`; kết quả thử trên dữ liệu hoán vị: `out/results_fake/`; thăm dò sau đóng băng: `out/results_post_freeze/`; MDE: `out/mde_table.csv`; kiểm tra kích cỡ: `out/size_check.csv`.
- Code: `_claude_pap/scripts/` (`run_all.py` chạy toàn bộ: `python3 run_all.py` thật, `--fake` kết cục hoán vị; `_pap_common.py` Conley + FE; `_pap_est.py` động cơ ước lượng; `10_*`/`11_*` dựng panel; `20`–`24` ước lượng; `30` robustness; `40` Romano–Wolf; `50` bảng/hình; `15_mde`, `16_size_check`, `02_conley_validate`).
- Dữ liệu tải mới (ngoài OneDrive): `~/Projects/nckh_data/external/rma/` (zip + `download_log.csv` + `docs/`).
- Tài liệu nền: `_claude_feasibility/FEASIBILITY_REPORT.md`, `_claude_eda/ATLAS.md`, `CANDIDATE_DIRECTIONS.md`, `HANDOFF.md`, `BAO_CAO_PHAN_TICH_CHI_TIET.docx`; brief: `FEASIBILITY_BRIEF.md`, `EDA_BRIEF.md`, `PAP_EXECUTION_BRIEF.md`.
- Chia bang A/B: `_claude_eda/out/tab/state_split.csv` (SHA-256 `378528d83f0ed57ecaa9b3daef5b7e2efd01530f2f130df4ee49057f7458687a`, seed 20261015).

## 9. Cách chạy lại và môi trường
- Python 3.13 (pandas, pyarrow, scipy, statsmodels, matplotlib), R 4.5.1 với `fixest` (chỉ dùng để kiểm định Conley). Chạy từ `_claude_pap/scripts/`: `python3 run_all.py` (≈ 45 phút CPU; Romano–Wolf chiếm khoảng 22 phút; máy ngủ làm chậm). Kết quả chạy lại phải giống hệt bản đã ghi.
- Ghi nguồn khi công bố: PRISM Group, Oregon State University, https://prism.oregonstate.edu, accessed 15 Oct 2026; BEA; USDA RMA; FFIEC; FDIC.
- Không sửa kế hoạch hay script giai đoạn 2 sau đóng băng; mọi sửa phải ghi vào `DEVIATIONS.md` (chưa có file này vì chưa có sai khác).
