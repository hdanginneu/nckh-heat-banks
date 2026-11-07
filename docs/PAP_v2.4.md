# PAP v2.4 — Kênh bảo hiểm: tiếp xúc trồng trọt (có bảo hiểm) so với chăn nuôi (gần như không bảo hiểm)
Phiên bản 2026-11-07, viết TRƯỚC khi dựng biến chăn nuôi và chạy với nhiệt. Hdang yêu cầu chạy ngay; nhóm chưa duyệt.

## Ý tưởng
Bảo hiểm cây trồng liên bang bao phủ phần lớn doanh thu trồng trọt; thu nhập chăn nuôi phần lớn không được bảo hiểm (bảo hiểm đồng cỏ PRF và LRP có quy mô nhỏ hơn nhiều [?]). Nếu bảo hiểm là lý do ngân hàng không chịu tổn thất, thì tổn thất và dự phòng phải tăng theo nhiệt ở ngân hàng có khách vay chăn nuôi, không tăng ở ngân hàng có khách vay trồng trọt.

## Biến
LIV_b = Σ_c w_bc · livestock_c / Σ_c w_bc · (livestock_c + crop_c), với livestock, crop = trung bình doanh thu BEA (CAINC45 dòng 20 và 60) 2001–05 của hạt; w = trọng số tiền gửi năm phân tích đầu của ngân hàng (cùng quy ước với Cov); hạt thiếu dữ liệu bị bỏ khỏi tử và mẫu số. CROPX = FS10·(1 − LIV), LIVX = FS10·LIV.
## Đặc tả (V2 mở rộng)
y = β_C·Heat·CROPX + β_L·Heat·LIVX + γ·Heat·LIV + Heat·Z + Heat + controls + FE ngân hàng + division×năm + năm×{CROPX, LIVX, LIV, Z}. Mẫu 2007–2022.
## Kiểm định xác nhận (họ F5, Westfall–Young trên Δ = β_L − β_C)
Outcome h0: NCO, ΔNPL, provision (không điều kiện), Δallowance (không điều kiện). [H] Δ > 0 (chăn nuôi chịu tổn thất nhiều hơn).
RI hoán vị năm thời tiết, R = 300, seed [20261109, khối]. Phát hiện ⇔ p_WY < 0,05.
## Phụ
β_L và β_C riêng; provision h1, Δallowance h1; vay sản xuất NN; ΔLIQ; placebo lead cho NCO và ΔNPL. Kiểm tra cấp hạt (mô tả): nhiệt → doanh thu chăn nuôi, nhiệt → thu nhập ròng nông trại theo tỷ trọng chăn nuôi.
## Cây diễn giải
- Δ > 0 phát hiện, placebo sạch → bằng chứng có nhận dạng cho kênh bảo hiểm: "ngân hàng không chịu tổn thất ở phần được bảo hiểm".
- Δ ≈ 0 và cả hai β ≈ 0 → nhiệt không gây tổn thất ngân hàng kể cả ở phần không bảo hiểm → null không do bảo hiểm (hoặc chăn nuôi có cơ chế đệm khác); kênh bảo hiểm KHÔNG được ủng hộ.
- Δ < 0 → ngược kỳ vọng; báo thẳng.
## Hạn chế đã biết
LIV tương quan với vùng (Plains/West); năm×LIV hấp thụ gradient tuyến tính theo năm. Chăn nuôi có thể chịu nhiệt qua giá thức ăn chứ không qua sản lượng. PRF mở rộng sau 2007 làm giảm tương phản.
