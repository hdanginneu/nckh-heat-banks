# PAP giai đoạn 2 — RQ3: giá tín dụng nông nghiệp và đợt nóng hai năm

Trạng thái: đóng băng nội bộ bằng `freeze_p2.py` (SHA-256) trước khi chạy dữ liệu thật; `run_p2.py` từ chối chạy thật nếu hash không khớp. Không đăng lên nền tảng bên ngoài (quyết định của nhóm, 13/11/2026).

Kế thừa PAP v3 (đóng băng 13/11/2026 13:35): cùng mẫu ngân hàng cộng đồng, cùng nhiệt (ngày–độ trên 29°C tháng 4–9, cân theo tiền gửi chi nhánh t−1, chuẩn hoá cấp ngân hàng), cùng đặc tả V2, cùng suy luận hoán vị năm thời tiết. Mọi điều không nói ở đây giữ như PAP v3.

## 1. Vì sao có giai đoạn 2, và nhóm đã thấy gì trước khi viết

Giai đoạn xác nhận (PAP v3) cho thấy thanh khoản tăng trong năm nóng. Phân tích làm sau khi đóng băng (`POST_FREEZE_ADDENDUM_v3.md`) gợi ý mức tăng đi cùng dư nợ co lại. Câu hỏi còn mở là ai thu hẹp: nông hộ vay ít đi (cầu) hay ngân hàng siết cho vay (cung). Brei et al. (2026) giải thích theo hướng cung nhưng ghi rõ họ không có lãi suất của khoản vay nông nghiệp. Phản biện chính với kết quả null về tổn thất là bài chỉ đo một năm nóng, trong khi Jaromczyk et al. (2026) và Özsoy et al. (2025) chỉ thấy tác động khi cú sốc kéo dài hai năm trở lên.

Trước khi viết kế hoạch này, nhóm đã:
- tải bảng RI và RC-E của Call Report Q4 2005–2025 từ FFIEC (13/11/2026), trích RIAD4024 và các mục tiền gửi (`_claude_feasibility/12_ffiec_ri_rce_extract.py`);
- kiểm độ phủ: RIAD4024 có ở gần như mọi ngân hàng có tài sản từ 300 triệu USD trở lên hoặc vay sản xuất nông nghiệp từ 7% dư nợ trở lên (97–100%), và hiếm ở ngân hàng nhỏ có tỷ trọng dưới 3% (1–10%), tức có ngưỡng báo cáo; trung vị lãi suất hiệu dụng theo năm từ 4,8% đến 8,3%;
- tính độ lệch chuẩn của các biến kết quả để đặt ngưỡng Δ (mục 5);
- chạy toàn bộ code trên dữ liệu giả (biến kết quả hoán vị trong từng năm × nhóm ag25).

Nhóm **chưa** chạy hồi quy nào giữa nhiệt và các biến kết quả P1, P2. Những gì đã thấy từ trước trên dữ liệu thật: tổng tiền gửi và dư nợ năm nóng (E3, một năm nóng); tổn thất ròng cộng dồn với một năm nóng (C1); quá hạn sớm của nợ đất nông nghiệp với nhiệt năm t−1 làm biến kiểm soát (E2; code chỉ trả hệ số của nhiệt năm t, hệ số của nhiệt năm t−1 chưa được in hay xem). Các biến S1 (cơ cấu tiền gửi) gắn với tổng tiền gửi đã xem, nên chỉ là mô tả.

## 2. Câu hỏi và họ xác nhận

| Mã | Câu hỏi | Biến kết quả | Cú sốc | Thống kê θ |
| --- | --- | --- | --- | --- |
| P1 | Năm nóng có làm lãi suất cho vay sản xuất nông nghiệp thay đổi không (phân biệt cầu với cung)? | YLD(t+1) − YLD(t−1), điểm % | Nhiệt năm t | β(H_t × FS10) |
| P2 | Đợt nóng hai năm có làm nợ xấu của vay sản xuất nông nghiệp tăng không? | [NPA(t) − NPA(t−2)] / dư nợ vay sản xuất NN (t−2), điểm % | Nhiệt năm t và t−1 | β(H_t × FS10) + β(H_{t−1} × FS10) |

Định nghĩa:
- YLD(k) = 100 × RIAD4024(k) / trung bình dư nợ vay sản xuất NN (RCON1590) cuối bốn quý năm k; cần cả bốn quý dương. RIAD4024 là thu nhập lãi và phí cả năm (YTD tại Q4).
- NPA = quá hạn từ 90 ngày (RCON1597) + ngừng dồn tích (RCON1583) của vay sản xuất NN, giống định nghĩa nợ xấu của Jaromczyk et al. (2026).

Vì sao chọn P1 ở t+1: khoản vay sản xuất thường giải ngân vào mùa xuân và tất toán sau thu hoạch, nên lãi suất trong năm t phần lớn đã chốt trước khi mùa nóng xảy ra. Nếu ngân hàng định giá lại rủi ro, thay đổi xuất hiện khi gia hạn hoặc cho vay lại ở năm t+1. h = 0 báo kèm, chỉ để mô tả.

Vì sao chọn cửa sổ của P2: mốc gốc t−2 nằm trước cả hai năm nóng, nên θ là tác động của một đợt nóng hai năm (mỗi năm +1 SD) lên thay đổi kể từ trước đợt nóng. Biến kiểm soát ngân hàng lấy tại t−2 (không dùng t−1, vì t−1 đã chịu cú sốc thứ nhất).

## 3. Mẫu

Năm cú sốc t: P1 2007–2023 (cần YLD tại t+1 ≤ 2024), P2 2007–2024.

Điều kiện báo cáo được xác định trước cú sốc: P1 chỉ gồm (b, t) mà tại t−1 ngân hàng có vay sản xuất NN dương và (tỷ trọng vay sản xuất NN ≥ 7% tổng dư nợ hoặc tổng tài sản ≥ 300 triệu USD). P2 dùng cùng điều kiện nhưng tại t−2. Lý do: RIAD4024, RCON1597 và RCON1583 chỉ được báo khi vượt ngưỡng; nếu chọn mẫu theo năm sau cú sốc, ngân hàng giảm cho vay và rơi xuống dưới ngưỡng sẽ tự bị loại.

Mọi biến kết quả winsorize 1%/99% trong mẫu, như PAP v3.

## 4. Đặc tả và suy luận

P1 dùng đúng đặc tả V2 của PAP v3: H_t × {FS10, z_size, z_liq, z_lat}, H_t, mưa mùa vụ (bậc một và bậc hai), ba biến kiểm soát ngân hàng tại t−1, FE ngân hàng, FE division × năm, năm × {FS10, Z}.

P2 thêm khối nhiệt năm t−1: H_{t−1} × {FS10, Z} và H_{t−1}. Biến kiểm soát ngân hàng tại t−2. Nhiệt năm t−1 của ngân hàng là nhiệt cân theo trọng số tiền gửi của hàng (b, t−1).

Suy luận: hoán vị năm thời tiết như PAP v3, R = 1.000, seed mới 20261120, cùng một dãy hoán vị cho mọi thiết kế. Trong P2, nhiệt năm t nhận nhiệt năm π(t) và nhiệt năm t−1 nhận nhiệt năm π(t−1), với cùng π. Hoán vị coi các năm thời tiết là trao đổi được, nên cũng phá tự tương quan giữa hai năm liên tiếp của nhiệt; θ là tổng hai hệ số, không phải hệ số của một biến "hai năm nóng".

Westfall–Young step-down max-|t| trên họ {P1, P2}. Khoảng tin cậy 90% = θ ± 1,645 × độ lệch chuẩn hoán vị.

## 5. Ngưỡng tác động đáng kể Δ (đã tính, `sesoi_p2.json`)

| Thống kê | Neo | Δ (đơn vị β, mỗi 10 điểm % FarmShare) | Quy về FarmShare 25% |
| --- | --- | --- | --- |
| P1 | Quy ước 0,10 SD của biến kết quả (SD = 1,708) | 0,068 | khoảng 17 điểm cơ bản |
| P2 | Quy ước 0,10 SD (SD = 1,433) | 0,057 | khoảng 0,14 điểm % dư nợ vay sản xuất NN |

Tác động mà Jaromczyk et al. (2026) tìm thấy (khoảng 3% SD của tỷ lệ nợ xấu cho mỗi 1°C trong hai năm) nhỏ hơn ngưỡng của P2; thiết kế không nhằm phát hiện mức đó.

## 6. Phân loại và quy tắc diễn giải (viết trước khi chạy)

Phân loại như PAP v3: **+** / **−** nếu p_WY < 0,05 (theo dấu); **0** nếu không phát hiện và khoảng tin cậy 90% nằm trong (−Δ; Δ); **?** nếu còn lại.

P1 (giá):
- **+**: lãi suất tăng ở ngân hàng nông nghiệp sau năm nóng. Cùng với dư nợ giảm (đã thấy ở E3), mẫu hình này phù hợp với cung tín dụng thắt lại.
- **−**: lãi suất giảm. Phù hợp với cầu vay giảm.
- **0**: lãi suất không phản ứng quá Δ. Không phân biệt được cầu với cung; chỉ nói được ngân hàng không định giá lại rủi ro nông nghiệp ở mức đáng kể.
- **?**: không kết luận.
- Đọc kèm Q1 (thay đổi dư nợ vay sản xuất NN t−1 → t+1, cùng mẫu P1; mô tả). Kết luận "cung" hay "cầu" chỉ được viết khi P1 là +/− và Q1 âm.
- Thiên lệch đã biết: nợ ngừng dồn tích tăng làm thu nhập lãi giảm cơ học, nên kéo P1 về phía âm. Vì vậy một kết quả **−** chỉ được diễn giải là cầu giảm nếu độ vững R-P1b (mẫu số là dư nợ đang sinh lãi) cùng dấu và bằng ít nhất 0,5 lần.

P2 (đợt nóng hai năm):
- **+**: đợt nóng hai năm làm nợ xấu tăng. Đây sẽ là khác biệt lớn so với kết quả một năm và được viết thành phát hiện chính.
- **0**: tác động của đợt nóng hai năm nhỏ hơn Δ.
- **?**: không kết luận.

Placebo (ngưỡng p < 0,025 như PAP v3; hỏng thì hạ kết luận của thống kê đó xuống mức gợi ý):
- P1_pl: YLD(t−1) − YLD(t−3), mẫu đủ điều kiện tại t−1, nhiệt năm t.
- P2_pl: [NPA(t−2) − NPA(t−4)] / dư nợ vay sản xuất NN (t−4), đủ điều kiện tại t−4, nhiệt năm t và t−1.

Hao hụt mẫu P1 (P1_exit): trong mẫu đủ điều kiện tại t−1 và có YLD(t−1), biến chỉ báo thiếu YLD(t+1). Nếu p < 0,05, báo cáo kết quả P1 kèm cảnh báo chọn mẫu.

## 7. Độ vững đã đăng ký (không đổi phân loại; báo số)

- R-P1a: P1 ở h = 0 (YLD(t) − YLD(t−1)).
- R-P1b: P1 với mẫu số là trung bình dư nợ vay sản xuất NN trừ nợ ngừng dồn tích cuối năm (RCON1583).
- R-P2a: chỉ nhiệt năm t (bỏ khối t−1), cùng mẫu và cửa sổ, để tách phần do năm thứ hai.

## 8. Mô tả, không kết luận (ghi rõ trong bài là ngoài họ xác nhận)

- S1: thay đổi tiền gửi giao dịch (RCON2215) và phi giao dịch (RCON2385) trong năm nóng, chia tổng tài sản t−1.
- S1 tách trước và sau 2012 (t ≤ 2011, t ≥ 2012), để so với Brei et al. (2026), nơi dòng tiền gửi vào tập trung trước 2012. Tổng tiền gửi đã được xem, nên các kết quả này chỉ để mô tả.

## 9. Kiểm thử trước khi chạy thật

- Code chạy đầy đủ trên dữ liệu giả (13 thiết kế, R = 200).
- Tỷ lệ bác bỏ sai trên các bộ dữ liệu giả cho họ {P1, P2}: xem `size_p2.py`.
- Khoá chạy thật đã kiểm: `run_p2.py` từ chối chạy khi chưa có `hashes_frozen_p2.json`.

## 10. Thứ tự thực hiện

1. Thêm R-P1b, R-P2a vào code; kiểm thử dữ liệu giả.
2. `freeze_p2.py` ghi SHA-256 của PAP_P2.md, run_p2.py, sesoi_p2.json và file dữ liệu đầu vào mới.
3. Chạy thật; diễn giải theo đúng mục 6.

Ghi chú 13/11/2026: P3 (tổn thất cộng dồn sau đợt nóng hai năm) bị bỏ trước khi chạy, vì thử trên dữ liệu giả cho thấy nó gần như chắc chắn không đạt được kết luận với ngưỡng neo theo C1 và không thêm thông tin so với C1.
