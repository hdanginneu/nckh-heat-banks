# Quy tắc diễn giải cho các phép chạy thêm R1–R7 (chốt trước khi chạy)

Ghi chú về tính mù: mọi kết quả chính (C1–C5, E1–E4, P1–P2, I1–I3) đã được thấy trước khi viết file này. Quy tắc dưới đây chỉ chốt trước đối với chính các phép chạy thêm R1–R7. Bài phải ghi đúng như vậy.

Ký hiệu: θ = thống kê gốc (giữ đúng định nghĩa của C1–C5, P1); Δ = ngưỡng đã dùng trong bài (sesoi_v3.json, sesoi_p2.json); CI95 = θ ± 1,96 × SD hoán vị; R = 1.000 trừ khi ghi khác; seed và dãy hoán vị như giai đoạn 2.

## R1. First stage cấp ngân hàng
y = trung bình ln doanh thu trồng trọt (BEA CAINC45 dòng 60) của các hạt, cân theo trọng số tiền gửi t−1 của ngân hàng (cần tổng trọng số các hạt có số liệu ≥ 0,5); hồi quy theo nhiệt cấp ngân hàng (cùng SD chung 234,8 ngày–độ), mưa bậc một và bậc hai, FE ngân hàng, FE division × năm; t = 2007–2022; mọi ngân hàng trong mẫu; suy luận hoán vị.
- Nhánh A: β trong [−0,25; −0,0625] (0,5–2 lần −0,125 của cấp hạt) và CI95 không chứa 0. Viết: "thước đo nhiệt cấp ngân hàng bắt được cú sốc doanh thu trồng trọt; chưa loại trừ sai số ở phơi nhiễm của ngân hàng (vị trí khoản vay, FarmShare gồm chăn nuôi, ngưỡng 29°C chung)".
- β < −0,25 và CI95 không chứa 0: như nhánh A, ghi thêm độ lớn khác cấp hạt.
- Nhánh B (mọi trường hợp còn lại): viết "sai số đo có thể kéo các ước lượng về 0"; hạ mọi câu "không phát hiện" ở Tóm tắt, mục 5–8 thành "không phát hiện, có thể một phần do thước đo phơi nhiễm"; đưa lên Hạn chế số 1.

## R2. Độ nhạy theo Δ
Biên tương đương nhỏ nhất = max(|CI90 dưới|, |CI90 trên|) cho C1–C5, P1, P2. Báo trong phụ lục; mỗi câu "tương đương" trong bài ghi kèm mức đã loại trừ. Không có quy tắc nhánh.

## R3. FarmShare_pre
Mẫu: ngân hàng có số liệu cả 2005 và 2006. FS_alt = trung bình FarmShare 2005–2006. So θ(FS_alt) với θ(FS gốc) TRÊN CÙNG MẪU ĐÃ CẮT, cho C1–C5.
- Vấn đề thật nếu |θ(FS_alt) − θ(FS gốc, cùng mẫu)| > 0,5Δ. Viết: kết quả phụ thuộc cách đo FarmShare; đưa vào Hạn chế.
- Nếu không: một câu ở mục độ vững; nếu chỉ khoảng tin cậy rộng ra thì ghi là mất độ chính xác.

## R4. Bỏ lần lượt từng division (9) và từng năm sốc cho C1, C2, C3, C5
Chỉ dùng ước lượng điểm (C4 đã làm trong PAP v3).
- Vấn đề thật nếu có tập con mà |θ_bỏ − θ| > 0,5Δ. Viết: nêu tên division hoặc năm đó và hạ kết luận của thống kê đó xuống "phụ thuộc vào [tên]".
- Nếu không: "không division hay năm nào làm ước lượng điểm dịch chuyển quá nửa ngưỡng Δ". Không diễn giải việc phân loại đổi do khoảng tin cậy rộng ra.

## R5. Dự phòng chia dư nợ hiện tại
y = 100 × [ALL(t+h)/L(t+h) − ALL(t−1)/L(t−1)]; θ_r = TB h = 0, 1 trên mẫu chung (như phần sớm của C2). So với phần sớm gốc −0,0130.
- θ_r ≤ −0,0065 (cùng dấu, ≥ 0,5 lần): "dự phòng giảm không chỉ do dư nợ co lại".
- θ_r > −0,0065: "phần lớn mức giảm dự phòng đi cùng dư nợ co lại"; sửa câu ở mục 6.2.

## R6. Tuyến tính theo FarmShare
Thêm nhiệt × FS10² (và năm × FS10²) vào đặc tả, cho C1, C4, P1. Kiểm định: p hoán vị của hệ số nhiệt × FS10², hiệu chỉnh Holm trên ba thống kê.
- p Holm < 0,05: bác tuyến tính; báo theo nhóm FarmShare (0–10%, 10–25%, ≥ 25%) và bỏ cách quy về "FarmShare 25% so với 0%" cho thống kê đó.
- Còn lại: "không bác được giả định tuyến tính"; giữ cách quy đổi.

## R7. Vùng nóng và vùng lạnh
Chia ngân hàng theo trung vị trung bình ngày–độ > 29°C 2006–2024 của chính ngân hàng; θ trong mỗi nửa cho C1, C4, P1; thống kê = hiệu (nóng − lạnh), p hoán vị cùng π, Holm trên ba thống kê.
- p Holm < 0,05: báo theo vùng, nêu giới hạn phạm vi của giả định tuyến tính theo ngày–độ.
- Còn lại: "không thấy khác biệt giữa vùng nóng và lạnh"; vẫn nêu giả định tuyến tính trong phương pháp.
