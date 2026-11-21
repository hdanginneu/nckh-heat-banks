# Quy tắc diễn giải cho các phân tích bổ sung B1–B4 (chốt trước khi chạy dữ liệu thật)

Viết 21/11/2026, **sau** khi đã thấy kết quả xác nhận C1–C5 (`rq3_v3/results_real/`) và các phép chạy thêm R1–R12, E1–E4, **trước** khi viết code chạy thật cho B1–B4. Mục đích: trả lời các phản biện của vai giáo sư và reviewer (21/11) về cách đo nhiệt, giả định hoán đổi năm, khủng hoảng 2008–2009 và tổn thất riêng ở khoản vay nông nghiệp.

Ràng buộc chung:
- Đây là **phân tích bổ sung làm sau khi đã thấy kết quả**. Không đổi phân loại chính thức của C1–C5, không đổi Δ, không đổi tiêu đề. Trong bài ghi rõ "phân tích bổ sung, quy tắc viết trước khi chạy, sau khi đã thấy kết quả chính".
- Báo cáo **mọi** kết quả dưới đây, kể cả kết quả bất lợi. Chi tiết để ở phụ lục; thân bài một đoạn.
- Cùng đặc tả V2 của PAP v3 (FE ngân hàng + division×năm, mưa, biến kiểm soát, năm×gradient), cùng winsorize 1% trong mẫu, cùng R = 1000 và **cùng dãy hoán vị π** (seed 20261115, khối 10, năm 2006–2024) trừ khi ghi khác.
- Thống kê như `run_v3.stat_row`: p_RI hai phía, CI90 dùng sd hoán vị × max(1, κ), TOST với Δ chính (`sesoi_v3.json`). Không dùng kiểm định một phía.
- Phân loại "bóng" (chỉ để so với bản chính): `+`/`−` nếu p_WY < 0,05 (Westfall–Young trong khối 5 θ của phép đó); `0` nếu CI90 nằm trong ±Δ; còn lại `?`.
- Code: `rq3_b/run_b.py`. Kiểm code trước bằng outcome hoán vị (`--fake`), sau đó đóng băng hash file này và `run_b.py` rồi mới chạy thật.

## B1. Tổn thất riêng ở khoản vay nông nghiệp
Câu hỏi: NCO tổng (C1) có làm loãng tổn thất ở khoản vay nông nghiệp không?
Đã có, không chạy lại: NCO nợ bảo đảm bằng đất NN (`C1_fl`, độ vững đăng ký trong PAP v3): θ = 0,0114, p_RI 0,53, CI90 [−0,017; 0,040], n = 49.215. Đưa con số này lên thân bài.
Chạy mới: `C1_ag` = NCO nợ sản xuất NN / dư nợ sản xuất NN (`NCOag_h6`), cùng đặc tả và cửa sổ với C1 (h = 6). Kèm `C1_ag_o` = C1 gốc trên **cùng các dòng** có `NCOag_h6`.
Hạn chế biết trước: `NCOag_h6` thiếu có hệ thống theo FarmShare (trong mẫu C1 2007–2019: có số liệu ở 21%, 31%, 54%, 94% dòng theo tứ phân vị FS10 từ thấp đến cao), nên mẫu là mẫu chọn lọc nghiêng về ngân hàng nông nghiệp.
Ngưỡng: Δ_ag = Δ_C1 × (trung bình NCOag_h6 / trung bình NCOc_h6, cùng các dòng) — cùng tỷ lệ tương đối với C1.
Đọc:
- CI90 nằm trong ±Δ_ag → "không thấy tổn thất ở khoản vay sản xuất NN vượt ngưỡng".
- θ > 0 và p_RI < 0,05 → ghi là tín hiệu ở khoản vay sản xuất NN mà NCO tổng không bắt được; thảo luận như kết quả bổ sung, không đổi phân loại C1.
- Còn lại → "không kết luận được", nêu độ rộng CI90 so với Δ_ag.

## B2. Nhiệt tại hạt đặt trụ sở thay cho nhiệt theo mạng chi nhánh
Câu hỏi: kết luận có phụ thuộc giả định nhiệt theo trọng số tiền gửi của chi nhánh không?
Biến: `heat_hq` = gdd_ex29 của hạt trụ sở tại t−1 (`hq_county_fips_l1`), năm t, chia cùng SD_BANK = 234,79 (để θ cùng đơn vị với bản chính). Hoán vị: `heat_hq` của năm π(t) cho cùng hạt.
Mẫu: mẫu của từng θ chính, chỉ giữ dòng có `heat_hq`. Kèm `B2o` = θ chính (nhiệt mạng chi nhánh) trên cùng các dòng.
Báo thêm: tương quan `heat_hq` với `heat`; SD của `heat_hq` theo đơn vị SD_BANK; κ.
Đọc (theo từng θ, so B2 với B2o):
- Cùng phân loại bóng → "kết luận không phụ thuộc cách đo nhiệt".
- Từ `0` sang `?` (CI90 rộng hơn) → "kém chính xác hơn, không mâu thuẫn" (dự kiến vì nhiệt trụ sở đo sai mức phơi nhiễm của ngân hàng nhiều hạt → suy giảm về 0 và nhiễu hơn).
- Đổi dấu có ý nghĩa (p_WY < 0,05 ngược dấu với θ chính) → báo là mâu thuẫn, thảo luận trong hạn chế; không đổi bản chính.

## B3. Xu hướng của nhiệt (giả định hoán đổi năm)
Câu hỏi: hoán vị năm thời tiết giả định các năm 2006–2024 hoán đổi được; một xu hướng ấm lên sẽ làm giả định này yếu đi.
Kiểm (không hồi quy outcome):
- (a) Chuỗi năm: trung bình `heat` của mọi ngân hàng-năm trong panel, 2006–2024 (19 năm). Hệ số góc tuyến tính (SD/năm), p OLS, p hoán vị năm (20.000 lần, seed 20261121), tương quan Spearman, tự tương quan bậc 1.
- (b) Theo vùng: cùng chuỗi cho từng division (9), hệ số góc và p hoán vị; hiệu chỉnh Holm trên 9 division.
Đọc:
- (a) p hoán vị ≥ 0,10 và không division nào có p Holm < 0,10 → "không thấy xu hướng làm hỏng giả định hoán đổi năm trong 2006–2024".
- Nếu (a) p < 0,10 hoặc có division p Holm < 0,10 → chạy **B3b**: dựng lại nhiệt từ gdd_ex29 cấp hạt đã khử xu hướng tuyến tính riêng từng hạt (hồi quy trên năm 2006–2024, cộng lại trung bình hạt), cùng trọng số tiền gửi và SD_BANK, chạy lại C1–C5 với cùng π. Đọc như B2 (so với bản chính).
- Không chạy B3b nếu điều kiện trên không xảy ra.

## B4. Bỏ năm sốc 2008–2009 (khủng hoảng tài chính)
Câu hỏi: kết quả có bị chi phối bởi các năm khủng hoảng, khi tổn thất tín dụng tăng vì lý do khác nhiệt?
Mẫu: bỏ mọi dòng có năm sốc t ∈ {2008, 2009} khỏi mẫu của từng θ (mẫu chung của C2, C3 lấy giao trước rồi mới bỏ năm); winsorize lại trong mẫu mới. Giữ **nguyên** dãy π và tập năm hoán vị 2006–2024: tập năm chỉ là năm thời tiết, không chứa khủng hoảng; giữ nguyên để khác biệt với bản chính chỉ đến từ mẫu.
Hạn chế biết trước: cửa sổ h = 6 của C1 bắt đầu từ 2007 hoặc 2010–2013 vẫn chứa một phần năm khủng hoảng ở phía outcome; B4 chỉ loại năm sốc, không loại hết. Division×năm FE đã hấp thụ cú sốc chung theo vùng.
Đọc: như B2 (so với bản chính trên mẫu đầy đủ). Đã có từ trước (R4, chỉ ước lượng điểm): bỏ riêng 2008 hoặc riêng 2009; B4 bổ sung suy diễn bằng hoán vị khi bỏ cả hai.

## Không làm
- Không địa mã hoá lại chi nhánh để thay biến nhiệt chính (G6: tương quan 0,9967; báo độ lớn ở phần hạn chế).
- Không thêm biến thể khác ngoài danh sách trên sau khi đã thấy kết quả B1–B4.

## Nhật ký trước khi đóng băng
- 21/11/2026: kiểm code `run_b.py` bằng outcome hoán vị (`--fake 7`, R = 20). MAIN tái lập đúng θ của v3 bản fake (sai khác 0); nhiệt dựng lại từ W trùng cột `heat` (sai khác 0); mọi dòng đều có `heat_hq`, nên mẫu B2 = mẫu chính.
- B3 không dùng outcome, nên lần kiểm code đã in ra kết quả B3 **thật** (nhiệt không bị hoán vị ở chế độ fake) trước khi đóng băng. Quy tắc B3 ở trên không sửa sau khi thấy kết quả này. B3 sẽ được chạy lại ở chế độ thật sau khi đóng băng để có file kết quả chính thức.
