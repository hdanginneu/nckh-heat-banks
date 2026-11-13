# PAP vòng cuối (P3) — Bảo hiểm cây trồng có phải tấm đệm giữa cú sốc nhiệt và ngân hàng?

Trạng thái: đóng băng nội bộ bằng `freeze_p3.py` trước khi chạy dữ liệu thật; `run_p3.py` từ chối chạy thật nếu hash không khớp. Đây là vòng phân tích cuối; kết quả nào cũng được đưa vào bài theo mục 5.

## 1. Câu hỏi và vì sao

Các giai đoạn trước cho thấy năm nóng không để lại tổn thất đo được, không làm quá hạn sớm tăng, và ngân hàng không định giá lại khoản vay sản xuất nông nghiệp (P1 = 0). Jaromczyk et al. (2026) cho rằng bồi thường bảo hiểm cây trồng và việc gia hạn nợ đỡ cho người vay. Vòng này kiểm phần bảo hiểm: nếu bảo hiểm là tấm đệm, tác động của nhiệt lên ngân hàng phải khác nhau giữa nơi bảo hiểm thấp và nơi bảo hiểm cao.

Trước khi viết, nhóm đã kiểm khả thi (không dùng nhiệt hay biến kết quả): mức bảo hiểm cấp ngân hàng có độ phân tán lớn (ngân hàng FarmShare ≥ 10%: phân vị 10% = 0,19, phân vị 90% = 0,79), gần như không tương quan với tỷ trọng chăn nuôi (−0,09), tương quan với vùng (R² = 0,31) và với FarmShare (0,45). Kết quả I1 (quá hạn sớm, cả mẫu) và I2, I3 trên cả mẫu đã được xem ở C3, P1, C4; việc chia theo mức bảo hiểm chưa từng được chạy.

## 2. Đo mức bảo hiểm

CR của hạt = giá trị được bảo hiểm (liability, RMA Summary of Business) TB 2001–2005 / doanh thu trồng trọt (BEA CAINC45, dòng 60) TB 2001–2005 (`rma_coverage_ratio.csv`), cắt trên ở phân vị 99% của hạt. Mức bảo hiểm của ngân hàng = trung bình CR các hạt, cân theo trọng số tiền gửi năm đầu tiên của ngân hàng; cần tổng trọng số của các hạt có CR ≥ 0,5. Đo trước giai đoạn mẫu nên không chịu ảnh hưởng của cú sốc trong mẫu. Giả định: thứ hạng mức bảo hiểm giữa các nơi tương đối ổn định sau 2005.

Nhóm: trong các ngân hàng FarmShare ≥ 10%, "thấp" là dưới trung vị mức bảo hiểm của nhóm này (0,562), "cao" là từ trung vị trở lên. Ngân hàng FarmShare < 10% là nhóm so sánh chung, có mặt ở cả hai bên. Ngân hàng FarmShare ≥ 10% thiếu mức bảo hiểm bị loại.

## 3. Thống kê

Với mỗi biến k, ước lượng θ_k(thấp) và θ_k(cao) bằng đúng đặc tả V2 (β của nhiệt × FS10) trên hai mẫu; thống kê là hiệu D_k = θ_k(thấp) − θ_k(cao).

| Mã | Biến (như) | Dự đoán của giả thuyết tấm đệm | Δ |
| --- | --- | --- | --- |
| I1 | Quá hạn sớm nợ đất NN, TB h = 0, 1 (C3) | D > 0 | 0,0072 (Δ của C3) |
| I2 | Δ lãi suất vay sản xuất NN t−1 → t+1, mẫu đủ điều kiện (P1) | D > 0 | 0,068 (Δ của P1) |
| I3 | Δ tỷ lệ thanh khoản năm nóng (C4) | D < 0 (tiền bồi thường làm thanh khoản tăng nhiều hơn ở nơi bảo hiểm cao) | 0,213 (Δ của C4) |

Ghi chú: I1 lấy trung bình hai horizon rồi mới winsorize, khác chút với C3 (winsorize từng horizon).

Suy luận: hoán vị năm thời tiết, R = 1.000, cùng dãy hoán vị với giai đoạn 2, cùng π cho hai nhóm nên phân phối của D tính được trực tiếp. Westfall–Young step-down trên {D_I1, D_I2, D_I3}. Khoảng tin cậy 90% = D ± 1,645 × độ lệch chuẩn hoán vị.

Độ chính xác (thử trên 9 bộ dữ liệu giả, R = 100): không bác bỏ sai lần nào trong 27 lượt; khả năng đạt "không khác biệt" khi thật sự không khác là 100% với I2, I3 và chỉ 11% với I1. Với I1, kết quả "?" là dự kiến nếu không có khác biệt.

## 4. Phân loại

Như các vòng trước: + / − nếu p_WY < 0,05; 0 nếu khoảng tin cậy 90% nằm trong (−Δ; Δ); ? còn lại.

## 5. Diễn giải (viết trước khi chạy)

- Ít nhất một D có p_WY < 0,05 theo đúng dấu dự đoán, và không D nào ngược dấu dự đoán có p_WY < 0,05: bằng chứng bảo hiểm là tấm đệm; đưa vào phần cơ chế.
- I2 và I3 đều "0": không có bằng chứng bảo hiểm tạo khác biệt về định giá và thanh khoản; viết ở phần thảo luận rằng bảo hiểm không giải thích được việc ngân hàng không phản ứng, trong phạm vi Δ.
- Còn lại (chủ yếu "?"): viết ở phần hạn chế rằng nhóm đã kiểm kênh bảo hiểm theo mức bảo hiểm của hạt nhưng dữ liệu không đủ chính xác để kết luận; bảng ở phụ lục.
- D có ý nghĩa nhưng ngược dấu dự đoán: báo cáo và giải thích; không được bỏ.
- θ(thấp), θ(cao) và p riêng từng nhóm chỉ để mô tả.

## 6. Thứ tự

1. `freeze_p3.py` (SHA-256 của PAP_P3.md, run_p3.py, run_p2.py, các file ngưỡng Δ và rma_coverage_ratio.csv).
2. Chạy thật: `python3 run_p3.py worker 0 1 3000` rồi `python3 run_p3.py collect`.
