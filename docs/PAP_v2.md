# PAP v2 — RQ3: phản ứng của ngân hàng cộng đồng Mỹ trước cú sốc nhiệt (thiết kế liều–đáp theo FarmShare)
Phiên bản: 2026-11-06 (soạn trước khi chạy hệ số nhiệt thật cho outcome RQ3). Phạm vi: CHỈ RQ3. PAP v1 (hashes_frozen.json) giữ nguyên, không sửa.
Nhãn: [F] sự thật đã kiểm; [I] suy luận; [H] giả thuyết; [P] đề xuất đã quyết trong tài liệu này; [?] chưa biết/chưa kiểm được.
Trạng thái duyệt: nhóm trưởng (Hdang) cho phép chạy ngay (05–06/11/2026) và chưa có duyệt nhóm đầy đủ → mọi mục [P] là lựa chọn của người soạn, tính "xác nhận" chỉ có nghĩa là đã khoá trước khi chạy.

## 1. Câu hỏi và estimand
RQ3: Khi nhiệt mùa vụ cao bất thường, ngân hàng cộng đồng có tiếp xúc nông nghiệp cao hơn có điều chỉnh bảng cân đối khác với ngân hàng ít tiếp xúc (trong cùng division, cùng năm) không — qua dự phòng/ allowance (kênh trích lập "trước khi lỗ") và thanh khoản?
Estimand: β2 = chênh lệch phản ứng (đơn vị outcome) với +1 SD nhiệt giữa hai ngân hàng chênh +10 điểm % FarmShare_pre, giữ nguyên các gradient theo năm của quy mô, thanh khoản, vĩ độ. Hiệu ứng của ngân hàng FS = 25% so với FS = 0 là 2,5·β2. Đây là tương quan có điều kiện trong thiết kế nhiệt "như-ngẫu-nhiên theo năm"; không phải hiệu ứng nhân quả của FarmShare (FS không ngẫu nhiên).
Giả thuyết định hướng (không dùng làm quy tắc quyết định): [H] β2(dALLOW|cond) > 0 (trích lập vượt tổn thất đã xảy ra); β2(dLIQ) chưa có dấu tiên nghiệm [?].

## 2. Dữ liệu và mẫu [F nguồn; P quy tắc]
- Panel bank_panel.parquet (PAP v1; 107.502 bank-năm, 8.254 ngân hàng; 2006–2024) nối Phase 1 (allowance_legacy_kusd, allowance_cecl_kusd, provision/chargeoffs/recoveries YTD, liquidity_ratio). Heat = Σ trọng số tiền gửi t−1 × GDD hạt (gdd_ex29, PRISM Tmax) / SD; dựng lại khớp tuyệt đối (T5).
- Mẫu chính: community banks, năm t = 2007–2022, toàn bộ ngân hàng (không lọc ag25), đủ các biến trong §3. N ≈ 88.287 bank-năm (7.650 ngân hàng) cho outcome allowance.
- Mở rộng 2007–2024 chỉ ở mục robustness (kèm cecl_post).
- Winsorize 1%/99% TRONG mẫu cho outcome và các control điều kiện (NCO, ΔNPL, allowance trễ). Cov cắt ở p99 theo ngân hàng rồi chuẩn hoá.

## 3. Biến
- Outcome (đều tại h0, % dư nợ cuối t−1 trừ dLIQ):
  * dALLOW_h0 = 100·(allowance_legacy_t − allowance_legacy_{t−1}) / dư nợ_{t−1}.  KHÔNG dùng allowance_to_loans (lỗi dữ liệu CECL, xem README rq3_explore).
  * prov_h0 = S_prov_cum_h0 = 100·provision YTD_t / dư nợ_{t−1}.
  * dLIQ_h0 = 100·(liquidity_ratio_t − liquidity_ratio_{t−1}) (điểm % tài sản). liquidity_ratio ≈ (tiền + HTM + AFS)/tài sản, tương quan 0,968 nhưng KHÔNG khớp tuyệt đối (T0) → định nghĩa chính xác [?].
- Tiếp xúc: FS10 = FarmShare_pre × 10 (trung bình 3 quan sát đầu; +1 đơn vị = +10 điểm %).
- Z (chuẩn hoá cấp ngân hàng, trung bình 3 quan sát đầu; vĩ độ cố định): z_size (log tài sản), z_liq (thanh khoản), z_lat (vĩ độ trụ sở). z_loans loại vì tương quan −0,984 với z_liq (T0). Hạn chế: Z tính từ 3 quan sát đầu (2006–2008) nên 2007–2008 có "nhìn tương lai" nhẹ → robustness bỏ 2007–2008.
- Control thời gian: mưa (ppt_season_z, ppt_z2), log tài sản/thanh khoản/vay trên tài sản trễ 1 kỳ (như v1); dummy năm bắt đầu CECL (cecl_adopt_year; 130 ngân hàng áp dụng sớm 2019–2022; 2.397 ngân hàng áp dụng 2023 nằm ngoài mẫu chính).
- Điều kiện hoá ("cond"): thêm NCO_h0 (net charge-off/dư nợ), ΔNPL (S_npl_total_h0), allowance trễ/dư nợ. KHAI BÁO: NCO và ΔNPL là biến đồng thời có thể chịu tác động của nhiệt (bad control); hệ số cond đọc là "dự phòng vượt tổn thất đã ghi nhận", không phải tổng phản ứng. Báo cả bản không điều kiện (raw).
- Bao phủ bảo hiểm Cov (chỉ phụ): liability RMA / doanh thu cây trồng BEA 2001–05, trọng số tiền gửi năm phân tích đầu của ngân hàng (rq3_explore/bank_coverage_pre.parquet); 599/8.254 ngân hàng thiếu.

## 4. Đặc tả chính (V2) [P]
y_{b,t} = β2·(Heat_{b,t}×FS10_b) + β1·Heat_{b,t} + Σ_Z γ_Z·(Heat×Z_b) + δ'X_{b,t} + α_b + τ_{division×năm} + Σ_t φ_t·FS10_b + Σ_t ψ_{Z,t}·Z_b + ε
- FE ngân hàng + division×năm; thêm dummy năm × {FS10, z_size, z_liq, z_lat} (hấp thụ gradient theo năm của các đặc điểm ngân hàng). Lý do chọn V2: không dựa trên hệ số nhiệt thật mà trên phân phối β2 dưới hoán vị năm (T6): sd(β2) = 0,00475 (V0, không năm×gradient), 0,00325 (V1: +năm×FS10), 0,00255 (V2) cho dALLOW|cond — V2 loại phương sai do cú sốc năm×gradient chung và được bảo vệ tốt hơn trước "chu kỳ giá nông sản trùng năm nóng". Hệ quả: β2 chỉ nhận dạng từ biến thiên nhiệt TRONG năm (chéo không gian), không từ chuỗi nhiệt toàn quốc theo thời gian.
- V0 và V1 chạy như độ nhạy.
- Họ chính (F1, xác nhận): dALLOW|cond, prov|cond, dLIQ (tất cả h0). dALLOW và prov điều kiện hoá gần như cùng một đối tượng (dALLOW ≈ prov − NCO: hệ số hồi quy 0,978, tương quan 0,915–0,919; T0) → bằng chứng của chúng KHÔNG độc lập; vẫn giữ cả hai trong họ để Westfall–Young tính tương quan.
- Đã "thấy" trước PAP (khai báo đầy đủ): (i) feasibility 2026-10-15 (_claude_feasibility/specs_tried.csv) đã ước lượng Heat×FarmShare_pre/10pp trên toàn mẫu cho prov_cum (không điều kiện; hệ số ≈ −7e-5 ± 7e-5 theo bank+year; ≈ −2e-5 ± 4e-5 theo bank+state-year), cùng npl (+), roa (−), eq_assets (−), loan_growth, d_farm, d_farmland, d_agprod, netco_cum, asinh_z → prov|raw là "đã thấy" và prov|cond chỉ xác nhận một phần; dALLOW và dLIQ chưa từng được chạy với nhiệt thật [F, đối chiếu specs_tried.csv]. (ii) PAP v1 + thăm dò sau đóng băng (H4 mong manh; G2/G2b). (iii) Trước đóng băng v2 chỉ chạy các chẩn đoán T0–T6 (§9) với nhiệt placebo/hoán vị.

## 5. Suy luận (quyết định trước) [P]
1. Suy luận chính = randomization inference (RI) bằng hoán vị năm thời tiết: gdd_perm(b,t) = Σ_c w_{b,t,c}·GDD(c, π(t)) / SD, π là hoán vị không điểm cố định của 2006–2024 dùng chung mọi ngân hàng; giữ nguyên outcome, FE, mưa, trọng số footprint năm t. R = 600 (V2), 100 (V0, V1). p_RI = (1 + #{|β*| ≥ |β̂|})/(1+R), hai phía. Lý do: T3 cho thấy Conley (1.000 km, lag 2) lệch kích cỡ (10–19% tại mức 5%; R chỉ 16–40 nên thô) và SE cụm-bang lệch mạnh hơn (31–45%) khi nhận dạng dựa trên tương tác nhiệt×FS với chỉ ~17 năm; v1 cũng đã ghi nhận kích cỡ 14–16% cho D1. Conley và cụm-bang vẫn được báo như mô tả.
2. Đa kiểm định: Westfall–Young step-down (max-|t|) trên họ F1 với cùng π; |t| = |β̂|/sd(β* hoán vị). "Phát hiện" (detected) ⇔ p_RI,WY < 0,05 cho β2.
3. Tương đương: CI 90% = β̂ ± 1,645·sd(β* hoán vị) (xấp xỉ chuẩn; giả định hiệu ứng hằng) so với ±SESOI_β2. SESOI_β2 (dALLOW, prov) = 0,05 × trung vị(allowance trễ/dư nợ trong mẫu) / 2,5 ≈ 0,026 pp (nghĩa: khác biệt phản ứng giữa FS = 25% và FS = 0 không vượt 5% quỹ dự phòng khi nhiệt +1 SD). SESOI_β2 (dLIQ) = 0,10 × SD_y / 2,5. [P, đề xuất của người soạn; cần nhóm duyệt về mặt kinh tế.]
4. MDE80 = 2,8016 × sd(β* hoán vị); báo mde/SESOI. Ex-ante (T6, V2, R=60): dALLOW|cond sd(β2) 0,00255 → MDE80 0,0071 (≈ 0,018 SD_y; ≈ 27% SESOI); dLIQ sd 0,0499 → MDE80 0,140 (≈ 0,026 SD_y).
5. Placebo: nhiệt năm t+1 (hai vế: lead cùng lúc với nhiệt t, tương tác với cùng Z). Nếu hệ số lead×FS10 có p < 0,05 theo Conley HOẶC cụm-bang cho một outcome → gắn "mối lo nhận dạng" và hạ kết luận về outcome đó thành "gợi ý". (Placebo một vế V0 trước đóng băng: lead×FS10 = −0,0059 [t Conley −1,64; t bang −2,07] cho dALLOW|cond; −0,0071 [−1,90; −1,95] prov|cond; +0,036 [0,43; 1,24] dLIQ; hai vế dALLOW|cond: −0,0057 [−1,53; −1,85]. Đã biết, không phải bất ngờ.)

## 6. Danh sách chạy (tất cả đều chạy và ghi vào specs_run_v2.csv)
Xác nhận (F1, V2, RI): xem §5. Thăm dò/độ nhạy (không dùng để "phát hiện", chỉ mô tả hướng/độ lớn; Conley + cụm-bang): V0, V1; raw (không điều kiện) dALLOW, prov; D1 (lặp lại H4 dạng tương tác); h1 (dALLOW, dLIQ, prov); bin FarmShare (<5% làm gốc; 5–15, 15–25, 25–35, >35); ngưỡng nhị phân ag15/ag25/ag35; bỏ từng division (9) cho dALLOW|cond và dLIQ; năm 2009–2022; 2007–2024 + cecl_post; winsorize 0,5% và không winsorize; Heat×FS10×Cov (3 chiều, kèm Heat×Cov và gradient năm×Cov); cổ điển ag25 (nhiệt chính, FE ngân hàng + division×năm, không tương tác) cùng placebo lead. Tiêu chí "ổn định": dấu β2 giống nhau ở V0/V1/V2 và ở ≥ 7/9 lần bỏ division, độ lớn cùng bậc (hệ số trong khoảng 0,5–2 lần V2).
Heat×Clim (khí hậu ngân hàng) BỎ: sau FE ngân hàng nó không thêm biến thiên (tương quan 0,95–0,97, G4/G5).

## 7. Cây diễn giải: kết quả → bài báo trở thành gì (viết trước khi chạy) [P]
Quy ước: "phát hiện" = §5.2; "tương đương" = không phát hiện và CI90 nằm trong ±SESOI; "mơ hồ" = không phát hiện và không tương đương. Placebo sạch = §5.5 không kích hoạt. "Ổn định" = §6.
| Kịch bản | Điều kiện | Diễn giải [I] | Bài báo trở thành | Việc tiếp |
|---|---|---|---|---|
| S1 trích lập phòng ngừa | β2(dALLOW|cond) > 0 phát hiện; placebo sạch; ổn định | Ngân hàng nông nghiệp trích lập vượt tổn thất đã ghi nhận khi nóng bất thường (tương quan có điều kiện) | "Heat shocks and precautionary loan-loss reserving in agricultural community banks" (+ Hướng 1: mất doanh thu, bồi thường); đủ cho NEU; Q2/Q3 mới tính sau | Heat×FS×Cov (bảo hiểm làm dịu?), kiểm tra qua prov/dLIQ, bin dose-response |
| S2 xả dự phòng | β2(dALLOW|cond) < 0 phát hiện | Có thể là chu kỳ giá/thu nhập (năm nóng–giá cao), không phải "hành vi" | Chỉ báo cáo mô tả; KHÔNG làm headline | Xét nhiễu giá; D1, loan growth; hạ xuống phụ lục |
| S3 null có nghĩa | không phát hiện ở dALLOW & prov; CI90 trong ±SESOI; placebo sạch | Không thấy phản ứng dự phòng khác biệt ≥ 5% quỹ dự phòng; phù hợp "cú sốc được hấp thụ/bảo hiểm" nhưng KHÔNG chứng minh kênh bảo hiểm | "Insured shocks, quiet banks": Hướng 1 (mất doanh thu ≈ −11,7%/SD; bồi thường ≈ mất doanh thu, CI rộng) + null có tương đương; nêu rõ SESOI do nhóm đặt | Cov (3 chiều) để xem phản ứng chỉ khi bao phủ thấp; báo power |
| S4 mơ hồ | không phát hiện; không tương đương | Dữ liệu không đủ để nói gì về ngân hàng | Bỏ RQ3 khỏi claim; bài chỉ còn Hướng 1 + ghi chú phương pháp (power, kích cỡ Conley) | Không "cứu" bằng đổi đặc tả; cân nhắc thêm dữ liệu |
| S5 chỉ thanh khoản | dLIQ phát hiện, dALLOW không | Điều chỉnh bảng cân đối qua thanh khoản chứ không qua trích lập; cơ chế [?] (tiền gửi/lãi suất/tăng trưởng tín dụng) | "Liquidity rather than provisioning"; gắn nhãn thăm dò cho cơ chế | Kiểm loan growth, tiền gửi (outcome mới → PAP v2.1) |
| S6 placebo hỏng | bất kỳ phát hiện nào kèm placebo kích hoạt | Mối lo nhận dạng (xu hướng/thời tiết tự tương quan) | Hạ xuống "association"; không headline | Điều tra trước khi dùng |
| Hỗn hợp | outcome trái dấu / không ổn định | Không có câu chuyện nhất quán | Ghi nhận trung thực trong bảng; không chọn outcome đẹp | Thảo luận nhóm |
Dù kịch bản nào: (a) mọi kết quả là tương quan có điều kiện; (b) F1 là phần xác nhận duy nhất, còn lại thăm dò; (c) báo cả Conley và cụm-bang cạnh RI.

## 8. Điểm yếu đã biết / reviewer sẽ đánh đầu tiên [I]
1. FS vừa là tiếp xúc nông nghiệp vừa proxy quy mô/vùng/thanh khoản (tương quan −0,41 với size; +0,23 vĩ độ) → V2 kiểm soát gradient theo năm nhưng không loại hết (phi tuyến, vùng nhỏ).
2. Tiền đề "ngân hàng có thể không lỗ" (bảo hiểm): chưa có biến bảo hiểm cấp ngân hàng ngoài Cov thô (tương quan 0,55 với FS).
3. Chỉ ~17 năm; nhiệt toàn quốc theo năm bị hấp thụ trong V2 → nhận dạng từ biến thiên không gian trong năm; RI bao phủ phụ thuộc "các năm trao đổi được" (không xu hướng nhiệt 2006–2023, G4).
4. SESOI do người soạn đề xuất; MDE rất thấp so với SESOI → TOST dễ đạt nếu SE hoán vị đúng; reviewer có thể hỏi SESOI có quá rộng (bài học H3 v1).
5. Điều kiện hoá NCO/ΔNPL là bad control; prov|cond và dALLOW|cond gần đồng nhất.
6. Định nghĩa liquidity_ratio và CECL (MDRM 3123) chưa đối chiếu tài liệu chính thức [?].
7. Heat là GDD Tmax mùa vụ; với ngân hàng phi nông nghiệp là thước đo yếu → β1 (FS = 0) không phải placebo sạch.
8. Giải thích vì sao tương tác (không phải mức) hợp lý: nếu ngân hàng phi nông nghiệp vẫn phản ứng (qua kinh tế địa phương), β1 ≠ 0 là bình thường và không bác bỏ thiết kế.

## 9. Chẩn đoán đã chạy TRƯỚC khi đóng băng (rq3_v2/out/, T0–T6) — chỉ nhiệt placebo/hoán vị, không hệ số nhiệt thật
T0 kiểm tra kỹ thuật (CECL, đồng nhất thức dALLOW ≈ prov − NCO, liquidity, phân phối outcome, mẫu, Z); T1/T2 placebo lead (một vế/hai vế); T3 kích cỡ dưới hoán vị năm (Conley/cụm-bang); T4 so V0/V1/V2 bằng hoán vị năm; T5 dựng lại heat từ trọng số footprint × GDD hạt (khớp tuyệt đối; max|diff| = 0); T6 MDE/sd(β2) dưới RI. Các lựa chọn V2, RI, loại z_loans, quy tắc winsorize, SESOI được ra quyết định dựa trên T0–T6 và trước khi có hệ số nhiệt thật.

## 10. Quy tắc sau đóng băng
Mọi chỉnh sửa đặc tả/mẫu sau khi thấy kết quả ghi trong DECISIONS.md như "lệch khỏi PAP v2", báo cả bản gốc. Lỗi mã (không đổi ý định) được sửa kèm hash mới và ghi lý do. Không thêm outcome vào F1.
