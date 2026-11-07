# PAP v2.1 — RQ3 bổ sung: dư nợ giảm là do CUNG (ngân hàng siết) hay CẦU (người vay vay ít/trả nợ)?
Phiên bản 2026-11-06, viết sau PAP v2 và sau thăm dò F-09 (dư nợ giảm khi nhiệt × FarmShare cao), TRƯỚC khi chạy bất kỳ hệ số nhiệt thật nào cho các outcome mới dưới đây. Hdang yêu cầu chạy ngay; nhóm chưa duyệt → các mục [P] là lựa chọn của người soạn.
Nhãn: [F] [I] [H] [P] [?] như PAP v2.

## 1. Câu hỏi
Theo F-09 (thăm dò), ở ngân hàng FarmShare cao, năm nóng đi kèm dư nợ giảm (−0,325 điểm % tài sản/+1 SD nhiệt/+10 điểm % FS). Hai cách giải thích: cầu giảm (nông dân trả nợ vốn lưu động bằng bồi thường/doanh thu, ít vay) hoặc cung giảm (ngân hàng siết). Dữ liệu cấp ngân hàng-năm KHÔNG tách hoàn toàn được; v2.1 chỉ tìm bằng chứng gợi ý.

## 2. Ba kiểm tra (cùng đặc tả V2, FE ngân hàng + division×năm + năm×{FS10, Z}; mẫu 2007–2022; winsorize 1/99 trong mẫu)
- M1 — giá đi cùng lượng (xác nhận): y = ΔYLD_t = YLD_t − YLD_{t−1}, YLD = 100 × thu lãi và phí cho vay YTD / dư nợ bình quân năm (loan_interest_fees_ytd_kusd / annual_avg_loans_and_leases_kusd). Hệ số β2 (nhiệt × FS10). [H] Siết theo giá → β2 > 0; cầu giảm → β2 ≤ 0.
- M2 — ràng buộc vốn (xác nhận): y = ΔLOAN = 100 × (dư nợ Q4_t − Q4_{t−1}) / tổng tài sản_{t−1}; thêm nhiệt × FS10 × CAP, nhiệt × CAP, năm × CAP (CAP = vốn chủ/tài sản trung bình 3 quan sát đầu, cắt p1/p99 theo ngân hàng, chuẩn hoá; tương quan với FarmShare 0,04). Hệ số β3 (nhiệt × FS10 × CAP). [H] Cung bị ràng buộc vốn → ngân hàng vốn mỏng cắt mạnh hơn → β3 > 0; cầu thuần → β3 ≈ 0.
- M3 — thời điểm trong năm (mô tả): Δ dư nợ tổng và Δ vay sản xuất NN tích luỹ từ Q4_{t−1} đến Q1, Q2, Q3, Q4 của năm t (chia tổng tài sản_{t−1}). Q1 (trước phần lớn mùa sinh trưởng) đóng vai placebo; báo đường đi β2 theo quý.
Phụ (thăm dò, chỉ mô tả): ΔAGP với CAP; M1 ở V0; placebo nhiệt t+1 hai vế cho M1 và M2.

## 3. Suy luận
- RI hoán vị năm thời tiết như PAP v2 (π chung cho mọi ngân hàng; trọng số footprint năm t thật), R = 300, seed [20261107, khối]. Westfall–Young trên họ F2 = {β2 của M1, β3 của M2}. "Phát hiện" ⇔ p_RI,WY < 0,05.
- SESOI M1: ±10 điểm cơ bản lãi suất cho chênh lệch FS 25% vs 0 → β2 trong ±0,04 [P]. CI90 = β ± 1,645·sd(hoán vị).
- M3 và phần phụ: Conley + cụm-bang, không dùng để "phát hiện".
- Placebo: nếu lead × (FS10 | FS10×CAP) có p < 0,05 (Conley hoặc bang) cho M1/M2 → gắn mối lo nhận dạng.

## 4. Đã thấy trước (khai báo)
ΔLOAN và ΔAGP mức (không có CAP) đã thấy trong thăm dò F-09; tương tác CAP, YLD và dữ liệu quý CHƯA từng chạy với nhiệt thật. Chạy thử end-to-end chỉ với nhiệt hoán vị (results_dry/).

## 5. Cây diễn giải (viết trước)
| Kịch bản | Điều kiện | Diễn giải [I] | Câu được viết |
|---|---|---|---|
| C1 nghiêng về cung | M1 phát hiện β2 > 0 HOẶC M2 phát hiện β3 > 0; placebo sạch | Lượng giảm đi cùng giá tăng hoặc tập trung ở ngân hàng vốn mỏng | "consistent with a supply-side tightening component" |
| C2 nghiêng về cầu | M1 không phát hiện tăng và CI90 nằm dưới +SESOI (hoặc β2 < 0 phát hiện); M2 không phát hiện | Không thấy giá tăng hay vai trò của vốn | "more consistent with lower credit demand/repayment than with price-based tightening; non-price rationing cannot be ruled out" |
| C3 hỗn hợp | M1 và M2 trái chiều | Có thể cả hai kênh | Báo cả hai, không chọn |
| C4 mơ hồ | M1 không phát hiện và không tương đương; M2 không phát hiện | Không đủ dữ liệu | "we cannot distinguish supply from demand" |
| C5 placebo hỏng | bất kỳ phát hiện nào kèm placebo kích hoạt | Mối lo nhận dạng | Hạ xuống gợi ý |
Lưu ý chung: YLD là lãi suất bình quân toàn danh mục; dịch chuyển cơ cấu (bớt vay NN) có thể làm YLD đổi cơ học [?]. Siết có thể không qua giá (rationing) → C2 không loại trừ cung.
