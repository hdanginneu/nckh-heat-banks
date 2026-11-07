# PAP v2.2 — Cung hay cầu tín dụng nông nghiệp: bằng chứng từ khảo sát ngân hàng nông nghiệp của các Fed khu vực
Phiên bản 2026-11-07, viết TRƯỚC khi ghép dữ liệu khảo sát với nhiệt. Hdang yêu cầu chạy ngay; nhóm chưa duyệt → các mục [P] là lựa chọn của người soạn.

## Dữ liệu
- Federal Reserve District Surveys of Ag Credit Conditions (KC Fed, file Historical Data Q2 2026): 7 khu vực (CHI, DAL, KC, MIN, RICH, SF, STL), theo quý 1991Q1–2026Q2, chỉ số khuếch tán so với cùng kỳ năm trước (>100 = cao hơn): 001 nhu cầu vay, 002 vốn sẵn có để cho vay, 003 tỷ lệ trả nợ, 004 gia hạn/kéo dài, 005 yêu cầu tài sản bảo đảm, 006 thu nhập nông trại (KC, MIN, SF, STL); 015 lãi suất cố định vay vốn lưu động (%).
- Nhiệt khu vực-năm: GDD > 29°C (1/4–30/9, PRISM Tmax) theo hạt, trọng số = doanh thu cây trồng BEA 2001–05 của hạt (rma_coverage_ratio.csv), gộp theo bang thuộc khu vực [P, xấp xỉ ranh giới Fed bằng bang]: CHI = IA, IL, IN, MI, WI; KC = CO, KS, NE, OK, WY; DAL = TX; MIN = MN, MT, ND, SD; STL = AR, MO, KY, TN, MS; RICH = VA, WV, MD, NC, SC; SF = CA, OR, WA, ID, NV, UT, AZ. Chuẩn hoá: chia SD của nhiệt sau khi trừ trung bình khu vực, 1991–2025.

## Đặc tả
Y_{d,t}^{q} = β·Heat_{d,t} + α_d + τ_t + ε, riêng cho từng quý q. Chính: q = Q4 năm t (khảo sát cuối năm, sau thu hoạch). Phụ: Q3_t, Q1_{t+1}. Placebo: Q1_t (trước mùa sinh trưởng) — nếu |β| có p < 0,05 → mối lo nhận dạng.
FE khu vực + năm: nhận dạng từ chênh lệch nhiệt giữa các khu vực trong cùng năm.

## Suy luận
RI: hoán vị năm của chuỗi nhiệt (π chung cho mọi khu vực, không điểm cố định, các năm 1991–2025), R = 2000; p hai phía. Họ xác nhận F3 = 5 outcome ở Q4 (001–005), Westfall–Young. Phụ, không vào họ: 006 thu nhập (kiểm tra cú sốc có thật), 015 lãi suất.

## Cây diễn giải (viết trước)
- Cầu giảm / trả nợ: 001 ↓ hoặc 003 ↑ hoặc 004 ↓, trong khi 002 và 005 không xấu đi.
- Cung siết: 002 ↓ hoặc 005 ↑ (hoặc 015 ↑).
- Căng thẳng tài chính thông thường của năm xấu: 003 ↓, 004 ↑, 001 ↑ (cần vốn bù) — trái với câu chuyện bảo hiểm che chắn.
- Không phát hiện gì (WY ≥ 0,05) → "không phân biệt được" ở cấp khu vực.
- 006 phải ↓ khi nóng; nếu không, nhiệt khu vực đo kém → mọi kết luận khác chỉ là gợi ý.

## Hạn chế đã biết
7 khu vực, ~35 năm; ranh giới xấp xỉ theo bang; chỉ số là đánh giá chủ quan của ngân hàng, so với cùng kỳ năm trước (đã là dạng chênh lệch); không cùng mẫu ngân hàng với phân tích chính.
