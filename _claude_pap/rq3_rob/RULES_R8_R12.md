# Quy tắc diễn giải R8–R12 và E46 (chốt trước khi viết code và chạy; bổ sung cho RULES_R1_R7.md)

RULES_R1_R7.md giữ nguyên (SHA-256 451849c6…f26, commit adbe2ae). File này thêm các phép chạy đề xuất từ hai bản góp ý ngày 14/11/2026.
Ghi chú về tính mù: mọi kết quả chính đã được thấy trước khi viết file này. Quy tắc chỉ chốt trước đối với chính R8–R12. R11 và R12 là thăm dò.
Ký hiệu như RULES_R1_R7.md. Mọi phép có hoán vị dùng cùng dãy π của PAP v3 (seed 20261115, R = 1.000). Phân loại +/−/0/? theo đúng PAP v3.

## R8. FarmShare tại t−1 (xác định trước cú sốc)
FS10_alt = 10 × (dư nợ đất NN + vay sản xuất NN) / tổng dư nợ, đo tại Q4 năm t−1 (thay đổi theo năm). Mọi phần khác giữ nguyên đặc tả V2, kể cả năm × FS10.
So θ(FS10_alt) với θ(FS10 gốc) TRÊN CÙNG MẪU (hàng có FS10_alt), cho C1–C5, chỉ ước lượng điểm.
Báo kèm: tỷ lệ hàng (b, t) mà cửa sổ ba năm của FarmShare_pre chứa năm t hoặc năm sau t.
- Vấn đề thật nếu |θ_alt − θ_gốc| > 0,5Δ (C4, C5 dùng Δ quy ước). Viết: nêu thống kê đó; thêm vào Hạn chế rằng cách đo FarmShare_pre có chồng lên năm sốc và kết quả đổi khi dùng FarmShare t−1.
- Nếu không: một câu ở mục độ vững, kèm tỷ lệ chồng lấn.

## R9. Hoán vị cả nhiệt và mưa
Mưa cấp ngân hàng dựng lại từ mưa cấp hạt (ppt_season_z) và cùng trọng số tiền gửi t−1; mưa bậc hai = bình phương. Trong mỗi hoán vị, nhiệt và mưa cùng nhận giá trị của năm π(t). Báo sai lệch giữa mưa dựng lại và mưa trong panel.
θ quan sát tính với mưa dựng lại; tính lại p_RI, CI90, TOST và Westfall–Young cho C1–C5.
- Nếu phân loại của thống kê nào đổi so với kết quả chính: báo cả hai, ghi rằng phân loại đó phụ thuộc cách xử lý mưa trong suy luận.
- Nếu không đổi: một câu ở mục độ vững.

## R10. Thêm độ trễ của biến kết quả và nhiệt năm t−1
Thêm vào đặc tả: biến kết quả cùng định nghĩa đo từ t−2 đến t−1 (cột PRE_<biến>_m2), và khối nhiệt năm t−1: H_{t−1} × {FS10, Z} và H_{t−1}. Hoán vị: H_t nhận năm π(t), H_{t−1} nhận năm π(t−1). Thống kê vẫn là θ theo hệ số H_t × FS10, cho C1–C5.
So với θ gốc trên cùng mẫu (hàng đủ biến trễ).
- Vấn đề thật nếu |θ_R10 − θ_gốc| > 0,5Δ hoặc phân loại đổi: nêu thống kê, đưa vào mục độ vững và Hạn chế.
- Nếu không: một câu ở mục độ vững.

## R11. Bảo hiểm và vùng (thăm dò; chỉ cho C4)
R11a: C4 khi bỏ West South Central đã có trong kết quả v3 (C4_dd8). Không chạy lại; báo trong Tóm tắt và mục 5.6.
R11b: thêm H × INS, H × FS10 × INS và H × (biến giả division), cùng năm × {INS, FS10 × INS}; INS = mức bảo hiểm của ngân hàng (như P3), chuẩn hoá trên mẫu. Thống kê: hệ số H × FS10 × INS; p hoán vị.
- p < 0,05: bỏ câu "mức tăng thanh khoản không khác theo bảo hiểm"; báo hướng của hệ số.
- Còn lại: "sau khi cho phép tác động của nhiệt khác theo vùng, vẫn không thấy khác biệt theo mức bảo hiểm"; ghi là thăm dò.

## R12. Ngân hàng một hạt và nhiều hạt (thăm dò; đối chiếu Islam & Singh 2025)
Nhóm theo số hạt có tiền gửi tại t−1 (từ trọng số SOD): một hạt (= 1) và nhiều hạt (≥ 2). Ước lượng riêng từng nhóm, cùng đặc tả V2, cho AGLt h = 0 (dư nợ NN trong năm nóng) và LIQ h = 0 (C4). Thống kê: θ(nhiều hạt) − θ(một hạt); p hoán vị cùng π; Holm trên hai thống kê.
- p Holm < 0,05 và hiệu của AGLt âm: "dư nợ NN giảm mạnh hơn ở ngân hàng nhiều hạt, cùng chiều với Islam & Singh (2025)".
- p Holm < 0,05 và hiệu dương: "ngược chiều với Islam & Singh".
- Còn lại: "không thấy khác biệt giữa ngân hàng một hạt và nhiều hạt"; nêu số ngân hàng mỗi nhóm.

## E46. Quy cận trên của tổn thất ra vốn cấp 1 (phép tính, không hồi quy)
Cận trên C1 quy về FarmShare 25% (0,047 điểm % dư nợ) × trung vị dư nợ/tài sản ÷ trung vị tỷ lệ vốn cấp 1/tài sản, tính trên ngân hàng FarmShare_pre trong (15%, 35%], năm 2007–2024. Báo trong mục 6.4.
