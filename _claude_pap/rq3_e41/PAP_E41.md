# Kế hoạch phân tích E41: mẫu ngoài, năm sốc 1995–2006

Viết ngày 16/11/2026, trước khi chạy bất kỳ hồi quy nào trên outcome thật của mẫu mở rộng. Chỉ dùng nội bộ, không đăng ký công khai.
Đã chạy thử toàn bộ đường ống trên outcome hoán vị (`--fake 1`, R = 20). Đã xem thống kê mô tả của dữ liệu, chưa xem hệ số nhiệt nào trên dữ liệu thật.
File này, `run_e41.py` và các script dựng dữ liệu được đóng băng bằng SHA-256 (`freeze_e41.py`).

## 1. Câu hỏi

Kết quả chính của bài là C4. Năm nóng hơn làm tỷ lệ tài sản thanh khoản của ngân hàng nông nghiệp tăng: θ = 0,175, p_WY = 0,002, năm sốc 2007–2024.
E41 kiểm xem kết quả này có lặp lại trên các năm sốc **1995–2006** không. Giai đoạn này không trùng năm sốc nào với bài.
C1, C2, C3, C5 được báo cáo để đối chiếu.

## 2. Dữ liệu (các kiểm đã chạy, số liệu từ `out/check_02.txt`, `out/check_03.txt`, `out/cr_coverage.csv`, `out/panel_e41_flow.csv`)

- **Call Report Q4.** Nguồn: Chicago Fed (1994–2000) và FFIEC bulk (2001–2004). Từ 2005 dùng Phase 1 như bài. Dùng đúng mã MDRM của Phase 1 (`MDRM_MAP.csv`).
  Có một chỗ đổi mã: bán vốn liên ngân hàng trước 2002 là RCON/RCFD1350, từ 2002 là B987 + B989. Hai mã cùng khái niệm.
  - Kiểm chỗ nối: giá trị 2004 tự trích khớp tuyệt đối với cột `_l1` của Phase 1 năm 2005. Các biến kiểm: tài sản, dư nợ, thanh khoản, dư nợ/tài sản, log tài sản, FarmShare. Khớp với 7.184/7.184 ngân hàng.
  - Tổng tài sản khớp ASSET của FDIC: trung vị tỷ số 1,0000; từ 98,6% đến 100% ngân hàng lệch ≤ 0,1% mỗi năm.
- **Ngân hàng cộng đồng.** Lấy cờ CB của FDIC tại Q4 từng năm (api.fdic.gov). Năm 2005, 7.168/7.170 ngân hàng Phase 1 nối được có CB = 1.
- **Trọng số tiền gửi t−1.** Lấy từ SOD, theo mã hạt khai báo (STCNTYBR). Phase 2 thì gán chi nhánh theo toạ độ, và một số toạ độ là giá trị mặc định.
  Đo trên năm 2006, nhiệt dựng theo hai cách có tương quan 0,9967; 1,9% ngân hàng lệch quá 0,1 SD.
  Riêng Connecticut: SOD dùng hạt cũ, không khớp với vùng quy hoạch của lưới nhiệt 2024, nên ngân hàng CT rơi khỏi mẫu qua quy tắc tổng trọng số ≥ 0,98.
- **C3 chỉ có cho t ≥ 2002.** Quá hạn 30–89 ngày của nợ đất NN chỉ có từ Call Report 2001. Trước đó, quá hạn 90+ và ngừng dồn tích của đất NN chỉ có ở khoảng 10–13% ngân hàng.
- **Mẫu.** 91.253 bank-năm, 10.441 ngân hàng. Ngân hàng nông nghiệp (FarmShare_pre ≥ 25%): 27.094 bank-năm. C4 có 90.891 bank-năm.

## 3. Đặc tả: giữ như bài, trừ các điểm ghi rõ

Giữ như bài: outcome và θ_C (C1 NCO cộng dồn t..t+6; C2 trọng số −½, −½, ¼, ¼, ¼, ¼ trên h = 0, 1, 3–6, mẫu chung; C3 trung bình h = 0, 1, mẫu chung; C4 h = 0; C5 h = 2).
Cũng giữ: Heat×{FS10, z_size, z_liq, z_lat}, Heat, mưa và mưa², biến kiểm soát t−1, FE ngân hàng, FE division×năm, năm×{FS10, Z}, winsorize 1%.
Bộ ước lượng là lớp G của `run_rob.py`, đã kiểm khớp với v3.
Nhiệt dùng SD của mẫu chính (`bank_scales.json`), nên θ cùng đơn vị với bài. Δ của TOST lấy đúng Δ của bài (`sesoi_v3.json`).

Các điểm khác bài:
1. Trọng số theo mã hạt khai báo (mục 2).
2. FarmShare_pre lấy trung bình 3 quan sát CB đầu tiên kể từ 1994 (cùng quy tắc, khác giai đoạn). Z được chuẩn hoá trên tập ngân hàng của mẫu mở rộng.
3. Hoán vị năm thời tiết trong 1995–2006 (12 năm, hoán vị không điểm bất động). Seed 20261116, khối 10, R = 1000. κ và Westfall–Young như bài.
4. C3 chỉ có năm sốc 2002–2006.

## 4. Quy tắc (chốt trước khi chạy)

- **E41-1 (C4).** Gọi z là hiệu θ_mở rộng − θ_bài chia cho căn của tổng hai phương sai (sd_adj² + sd_adj_bài²).
  - TÁI LẬP nếu θ > 0 và p_RI < 0,05. Khi đó đưa vào bài như bằng chứng ngoài mẫu.
  - CÙNG CHIỀU, CHƯA ĐỦ CHẮC nếu θ > 0, p_RI ≥ 0,05 và |z| < 1,96. Báo cáo kèm MDE80, nói thẳng là mẫu ngoài không đủ lực để xác nhận.
  - KHÔNG TÁI LẬP trong mọi trường hợp còn lại. Khi đó viết rõ kết quả C4 chỉ thấy trong giai đoạn 2007–2024, và không khái quát ra ngoài giai đoạn đó.
- **E41-2.** Phân loại +/−/0/? cho C1–C5 trên mẫu mở rộng, dùng Westfall–Young trên các outcome có số liệu. Chỉ báo cáo; không đổi phân loại của bài.
- **E41-3.** C3 ghi rõ chỉ có năm sốc 2002–2006.
- **E41-4.** Thay FarmShare_pre bằng FarmShare t−1, so trên cùng mẫu (như R8). Vấn đề nếu |lệch| > 0,5Δ.

Không làm trong bản này: không gộp hai mẫu, không thêm biến, không đổi đặc tả theo kết quả.

## 5. Hạn chế đã biết

- Trước 2012, các thrift nộp TFR không có trong Call Report, ở cả mẫu chính lẫn mẫu mở rộng. Từ 2012 mẫu chính có thêm thrift, nên thành phần hai mẫu khác nhau.
- Ngân hàng CT bị loại (mục 2).
- Chicago Fed 1994–2000 có khoảng 5% thực thể thiếu các mục cân đối. Phần lớn số này không có cờ CB, nên không vào mẫu.
