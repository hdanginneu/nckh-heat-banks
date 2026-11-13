# Kết quả RQ3 v3 (PAP v3)

Chạy ngày 13/11/2026 trên máy của Hdang. PAP v3 đóng băng lúc 13:35:17 (`hashes_frozen_v3.json`), trước khi chạy dữ liệu thật; kiểm lại sau khi chạy: `freeze_v3.py --verify` → khớp toàn bộ. R = 1000 hoán vị, seed 20261115. Nguồn số: `rq3_v3/results_real/` và `results_real_dr/`.

Kiểm nhất quán [F]: bộ ước lượng nhanh trùng `fit_lp` (sai lệch lớn nhất 3,1e−13 trên 46 hồi quy); dựng lại hạn hán từ ma trận trọng số sai 7e−15. κ của năm θ chính nằm trong 0,88–0,97 (< 1), nên CI và TOST dùng đúng sd hoán vị, không nới.

Đơn vị θ: điểm % (của dư nợ t−1, trừ C4 là điểm % tài sản) cho nhiệt +1 SD và FarmShare +10 điểm %. Quy về FS 25% so với 0: nhân 2,5.

## 1. Họ xác nhận

| θ | θ̂ | sd | p_RI | p_WY | CI90 | Δ (chính) | TOST | Phân loại |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 NCO cộng dồn t..t+6 | −0,0120 | 0,0186 | 0,54 | 0,89 | [−0,0426; 0,0186] | 0,0129 | không | **?** |
| C2 dự phòng muộn − sớm | −0,0023 | 0,0059 | 0,70 | 0,91 | [−0,01200; 0,0075] | 0,01200 | đạt (sát ngưỡng) | **0** |
| C3 quá hạn 30–89 + nonaccrual đất NN, h=0..1 | −0,0008 | 0,0029 | 0,77 | 0,91 | [−0,0056; 0,0040] | 0,0072 | đạt | **0** (cờ placebo) |
| C4 ΔLIQ h=0 | +0,1753 | 0,0462 | 0,002 | 0,002 | [0,099; 0,251] | 0,213 | – | **+** |
| C5 dư nợ NN t−1→t+2 | −0,1440 | 0,1512 | 0,35 | 0,84 | [−0,393; 0,105] | 0,308 | không | **?** |

n: 59.172 / 47.163 / 93.601 / 97.526 / 86.143 ngân hàng–năm; 13 / 10 / 18 / 18 / 17 năm sốc.

Ghi chú bắt buộc:
- **C2 đạt TOST với biên gần bằng 0** (cận dưới −0,011995 so với −Δ = −0,011996). Bản phi tham số (§6.3) cho cận dưới −0,0129, **không đạt**. Theo PAP: ghi "nhạy với giả định phân phối". Với Δ phụ (0,0132) cả hai bản đều đạt. Ở đặc tả có hạn hán (R1), C2 không đạt.
- **C3 kích hoạt cờ placebo** (§8.4): outcome trước cú sốc m = 2 có β = −0,0061, p_RI = 0,014 < 0,025 (m = 3: p = 0,028). Mọi kết luận về C3 hạ xuống "gợi ý".
- **C4 có ý nghĩa nhưng θ̂ (0,175) nhỏ hơn Δ (0,213)**, và CI90 chứa Δ. Viết là "có ý nghĩa thống kê; độ lớn không phân biệt được với ngưỡng đáng kể". Khớp v2 (0,178 trên 2007–2022).

## 2. Diễn giải theo quy tắc đã đăng ký

**RQ-A (§8.1): C1 = ?** Không phát hiện và không chứng minh được tương đương; đúng như dự báo ở PAP §6.2. Loại trừ được (CI90): ở ngân hàng FS 25% so với FS 0, nhiệt +1 SD **không làm NCO cộng dồn 7 năm tăng quá 0,047 điểm % dư nợ**, tức khoảng 18% NCO bình quân của một năm, hay khoảng 2,6% NCO cộng dồn 7 năm [I: dùng ȳ = 0,255%/năm của nhóm FS 15–35%]. Không được viết "không có tổn thất".

**RQ-B (§8.2): dòng 6, "không kết luận được về thời điểm".** s₁ = ?, s₂ = 0, s₃ = 0. Dòng 1 ("quiet thật") cần cả ba bằng 0; C1 không đạt. Không dòng 2–5 nào thoả vì không θ nào dương.

Mô tả (không dùng để quyết định):
- Thành phần của C2: dự phòng "sớm" (TB h=0,1) −0,0130 (p_RI 0,03); "muộn" (TB h=3..6) −0,0153 (p_RI 0,10). Dự phòng giảm tương đối ngay năm nóng và **không hồi lại** về sau, nên hiệu muộn − sớm ≈ 0. LP từng h đều âm, h=1..4 có p_RI < 0,02 (không hiệu chỉnh). Không có dấu hiệu dự phòng dồn về sau kiểu Lu & Nikolaev.
- NCO: t..t+1 +0,0056 (p 0,52); t+3..t+6 −0,0033 (p 0,87).
- C3 bản mẫu số dư nợ đất NN (R3): −0,082 (p_RI 0,009, không hiệu chỉnh), cùng chiều với placebo âm → có thể là xu hướng trước cú sốc, không phải tác động. Bản có vay sản xuất NN: −0,020 (p 0,35).

**RQ-C (§8.3):**
- C4 `+`: thanh khoản tăng trong năm nóng ở ngân hàng nông nghiệp, tái lập v2 trên mẫu 2007–2024.
- R2 (độ ổn định): cùng dấu ở 9/9 division và 18/18 năm; độ lớn 0,59–1,16 lần ở mọi division và 0,82–1,16 lần ở mọi năm → **ổn định** theo tiêu chí đăng ký. Bỏ West South Central: 0,103 (p_RI 0,11), thấp nhất nhưng vẫn ≥ 0,5 lần.
- R1 (hạn hán): C4 = 0,153, p_RI 0,005 (≥ 0,5 lần, cùng dấu) → được viết **"nhiệt, sau khi tính đến hạn hán"**.
- C5 `?`. Mô tả: dư nợ NN/dư nợ giảm ngay năm nóng (h=0: −0,260, p_RI 0,001, đã thấy ở v2 dạng D1) nhưng không còn rõ ở h=2. Ở R1, C5 = −0,355 (p_RI 0,028): chỉ báo số, không đổi phân loại.
- C4 `+` và C5 `?`: chưa đủ để nói "thanh khoản tăng vì cho vay giảm" (H4) ở cấp xác nhận.

**Attrition (§8.4):** β₂ của rời mẫu ở h = 6: +0,0021 (p_RI 0,38); không h nào có p < 0,05 → không gắn cờ.

## 3. Câu kết luận được phép (§8.5)

> Over a six-year horizon we cannot rule out, nor detect, cumulative credit losses from extreme heat at agricultural community banks; we rule out increases above roughly one-fifth of a year's average net charge-offs. We find no evidence of delayed provisioning: allowances fall in hot years and do not rebuild later. Liquidity rises in the year of the shock, robustly across regions, years and drought controls, although its magnitude is not distinguishable from our pre-specified threshold of economic importance.

Không được viết: "heat does not cause losses", "banks are quiet", hay bất cứ câu nào về forbearance.

## 4. Hạn chế phát sinh từ kết quả

1. C2 đạt tương đương chỉ với biên ~1e−6 và không đạt ở bản phi tham số; phải nói rõ là kết luận mong manh.
2. Placebo của C3 hỏng ở m = 2: ngân hàng nông nghiệp có xu hướng quá hạn đất NN khác biệt ngay trước năm nóng.
3. sd thật của C2 (0,0059) thấp hơn sd trên dữ liệu giả (0,0098); MDE ở PAP §6.2 vì vậy bi quan cho C2.
