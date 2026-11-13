# Phụ lục sau đóng băng PAP v3 — phân tích thăm dò E1–E4

Viết 13/11/2026, **sau** khi đã thấy kết quả xác nhận (`RESULTS_RQ3_v3.md`) và **trước** khi chạy các phân tích dưới đây. Đây là phân tích thăm dò: không đổi phân loại của C1–C5, không hiệu chỉnh đa kiểm định, trong bài phải ghi "làm sau khi đã thấy kết quả". Code: `rq3_v3/explore_v3.py` (không thuộc bộ file đóng băng). Cùng đặc tả V2, cùng mẫu, cùng R = 1000 và dãy hoán vị như PAP v3 trừ khi ghi khác.

## E1 — Hao hụt mẫu: mẫu cân bằng
Câu hỏi: kết quả có do thành phần ngân hàng sống sót khác nhau không?
Mẫu: chỉ ngân hàng có số liệu ở MỌI năm 2006–2025. Chạy lại năm θ.
Đọc: nếu θ trên mẫu cân bằng cùng dấu và trong khoảng 0,5–2 lần θ gốc (hoặc cả hai đều nằm trong ±Δ) → "kết quả không do hao hụt mẫu". Nếu khác hẳn → báo là kết quả phụ thuộc thành phần mẫu.

## E2 — Vì sao placebo của C3 hỏng
Giả thuyết cạnh tranh, viết trước:
- (a) **Nhiệt tự tương quan:** nhiệt năm t tương quan với nhiệt năm t−1, và nhiệt t−1 có thể đã làm quá hạn tăng ở t−1. Kiểm: thêm nhiệt t−1 × {FS10, z} và nhiệt t−1 vào cả placebo lẫn C3; hoán vị nhiệt t và t−1 cùng π. Nếu placebo hết (p > 0,10) khi có nhiệt t−1 → hỏng là do tự tương quan của nhiệt, không phải xu hướng trước của ngân hàng.
- (b) **Hồi quy về trung bình:** thêm mức quá hạn năm t−1 (chia dư nợ t−1) làm biến kiểm soát. Nếu placebo hết → hỏng là do quá hạn tự hồi về trung bình. (Biến này là "bad control" tiềm năng cho C3 vì nằm trong outcome; chỉ dùng để chẩn đoán.)
- Nếu không cách nào làm placebo hết → giữ nguyên kết luận "C3 chỉ là gợi ý".

## E3 — Thanh khoản tăng vì đâu
Cùng đặc tả với C4 (h = 0, 2007–2024). Outcome, tất cả = 100 × thay đổi từ t−1 đến t chia tổng tài sản t−1:
tài sản thanh khoản (ΔLA), tổng tài sản (ΔTA), tổng dư nợ (ΔL), dư nợ NN (ΔAG), dư nợ phi NN (ΔL − ΔAG), tiền gửi (ΔDEP), chứng khoán (ΔSEC = HTM + AFS), tiền mặt và liên ngân hàng (ΔCASH).
Đồng nhất thức xấp xỉ: ΔLIQ ≈ ΔLA − LIQ_{t−1}·ΔTA.
Đọc: ΔL < 0 và ΔDEP ≈ 0 → thanh khoản tăng vì dư nợ giảm (phù hợp cầu vay giảm hoặc cung thắt chặt; không tách được). ΔDEP > 0 → có dòng tiền gửi (phù hợp Brei et al. 2026). ΔAG so với ΔL−ΔAG cho biết dư nợ giảm ở đâu.

## E4 — Năm áp dụng CECL
Bỏ hẳn mọi ngân hàng từng báo mục RCONJJ30 trước 2023 (không chỉ bỏ cửa sổ chứa năm đó). Chạy lại C2. Đọc: so với C2 gốc.

---

# Kết quả E1–E4 (chạy 13/11/2026, R = 1000; `rq3_v3/results_explore/explore_results.csv`)

Kiểm nhất quán: E2_base (cùng mẫu, cùng đặc tả với C3 và placebo m = 2) cho θ = −0,00083 và placebo −0,00609, p 0,014 — trùng kết quả xác nhận. Mọi p dưới đây chưa hiệu chỉnh đa kiểm định.

**E1 — mẫu cân bằng** (3.273 ngân hàng có số liệu mọi năm 2006–2025):
| θ | Gốc | Mẫu cân bằng | CI90 cân bằng |
| --- | --- | --- | --- |
| C1 | −0,0120 | −0,0024 | [−0,034; 0,029] |
| C2 | −0,0023 | +0,0020 | [−0,0075; 0,0116] (trong ±0,0120) |
| C3 | −0,0008 | +0,0005 | [−0,0045; 0,0056] (trong ±0,0072) |
| C4 | +0,175 | +0,157 (p 0,004) | [0,069; 0,246] |
| C5 | −0,144 | −0,253 (p 0,12) | [−0,51; 0,008] |
→ Kết quả không do hao hụt mẫu: C4 giữ 0,90 lần; C2 và C3 vẫn nằm trong ngưỡng tương đương; C1 vẫn không kết luận được.

**E2 — placebo của C3:**
- (a) Thêm nhiệt t−1 (hoán vị cùng π): placebo vẫn hỏng (m = 2: −0,0063, p 0,011; m = 3: p 0,049) → không phải do tự tương quan của nhiệt.
- (b) Thêm mức quá hạn t−1: placebo hết (m = 2: −0,0036, p 0,13; m = 3: p 0,48) → khác biệt trước cú sốc nằm ở **mức quá hạn năm t−1**: ngân hàng nông nghiệp gặp năm nóng ở t đã có quá hạn cao hơn ở t−1. Lưu ý: biến kiểm soát này là một phần của outcome placebo, nên đây là chẩn đoán, không phải bằng chứng nhân quả.
- C3 khi kiểm soát mức t−1: +0,0020, CI90 [−0,0025; 0,0064], vẫn trong ±0,0072. Kết luận "không thấy quá hạn sớm tăng" không đổi; vẫn ghi là gợi ý.

**E3 — thanh khoản tăng vì đâu** (điểm % tổng tài sản t−1, cho nhiệt +1 SD và FS +10 điểm %):
| Khoản mục | β₂ | p_RI |
| --- | --- | --- |
| Tài sản thanh khoản ΔLA | +0,127 | 0,11 |
| Tổng tài sản ΔTA | −0,204 | 0,04 |
| Tổng dư nợ ΔL | −0,358 | 0,001 |
| — dư nợ NN | −0,136 | 0,001 |
| — dư nợ phi NN | −0,180 | 0,017 |
| Tiền gửi ΔDEP | −0,221 | 0,021 |
| Chứng khoán ΔSEC | +0,110 | 0,056 |
| Tiền mặt + liên ngân hàng | +0,011 | 0,86 |
Đồng nhất thức: ΔLA − LIQ_{t−1}·ΔTA = 0,127 + 0,322 × 0,204 ≈ 0,193, gần θ_C4 = 0,175.
→ Thanh khoản tăng chủ yếu vì **dư nợ giảm và bảng cân đối co lại**, phần tài sản giải phóng chuyển sang chứng khoán. **Tiền gửi giảm, không tăng** — trái với dòng tiền gửi đổ vào sau hạn hán trong Brei et al. (2026). Dư nợ và tiền gửi cùng giảm phù hợp với việc khách hàng dùng tiền gửi (có thể gồm cả tiền bồi thường) để trả nợ [I], nhưng không phân biệt được với ngân hàng thắt chặt cho vay. Dư nợ phi NN giảm: v2 đã thấy phần này có placebo lead hỏng, nên không quy cho nhiệt.

**E4 — bỏ hẳn ngân hàng áp dụng CECL sớm** (5.949 ngân hàng): C2 = −0,0021, CI90 [−0,011; 0,0072], trong ±0,0120 với biên rộng hơn bản gốc → kết luận C2 không do nhận diện CECL sai.
