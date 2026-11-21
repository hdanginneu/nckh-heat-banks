# Tái lập độc lập năm thống kê xác nhận bằng pyfixest (19/11/2026)

Script: `rep_pyfixest.py` (pyfixest 0.60.0). Kết quả: `results_real/rep_pyfixest.csv`, nhật ký `results_real/rep_pyfixest_log.txt`.

**Dùng chung với code gốc:** panel_v3 và các hàm chọn mẫu, winsorize (`_v3_spec.load_panel`, `common_rows`, `make_frame`), để hai bên
ước lượng trên đúng một tập quan sát. **Độc lập:** biến tương tác nhiệt × {FS10, z} và năm × {FS10, z} do công thức pyfixest tự dựng;
FE ngân hàng và division × năm do pyfixest khử (LSMR có tiền điều kiện viết bằng Rust, dung sai 1e-10, giữ quan sát singleton);
nghiệm OLS và sai số chuẩn cụm do pyfixest tính. Không tái lập phân phối hoán vị (suy luận chính của bài).

**Kết quả:** 11 hệ số thành phần (C1 h6; C2 h0, 1, 3, 4, 5, 6; C3 h0, 1; C4 h0; C5 h2) và 5 thống kê θ khớp đến sai số máy
(chênh lệch tương đối lớn nhất 2e-12); n khớp ở mọi chân. Sai số chuẩn cụm theo bang trụ sở khớp (chênh lệch tương đối < 1e-8) khi dùng cùng
hiệu chỉnh mẫu nhỏ G/(G−1)·(n−1)/(n−k) với k không tính FE (`ssc(k_fixef="none")`); với hiệu chỉnh mặc định của pyfixest (k tính cả FE
không lồng trong cụm), sai số chuẩn lớn hơn 4–7%, khác biệt do quy ước chứ không do lỗi.
