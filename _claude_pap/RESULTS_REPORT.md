# RESULTS_REPORT — Ai gánh tổn thất nhiệt trong nông nghiệp?
**Kết quả chạy đúng kế hoạch đã đóng băng (`PRE_ANALYSIS_PLAN_v1`, đóng băng nội bộ 2026-10-15 21:38; kiểm tra `freeze.py --verify`: khớp).** Không có sai khác so với kế hoạch (không có `DEVIATIONS.md`). Mọi hệ số là tương quan có điều kiện ("gắn với"), không phải nhân quả; pass-through là số mô tả. Số liệu lấy từ `out/results/*.csv` và `specs_run.csv` (mọi đặc tả đã chạy). Tmin không chạy theo quyết định của nhóm.

## 1. Tóm tắt kết quả
1. **First stage (H1) đạt:** +1 SD nhiệt gắn với ln doanh thu cây trồng thấp hơn 0.125 (CI95 Conley [−0.164; −0.086], khoảng −11.7%), N = 51139 hạt-năm; cùng dấu ở nửa A (−0.093) và nửa B (−0.132); 24 trên 26 đặc tả robustness có CI95 loại 0.
2. **Trợ cấp trực tiếp (H2) không đạt:** β = 0.0007 (CI95 [−0.011; 0.013]); hệ số quanh 0, p_RW = 0.858; phép placebo nhiệt năm sau cũng lệch khỏi 0 (−0.010), nên kết quả họ B yếu.
3. **Bồi thường RMA (H6) đạt rất mạnh:** +1 SD nhiệt gắn với bồi thường nhiệt-hạn bằng 0.217 lần doanh thu cây trồng baseline (CI95 [0.134; 0.299]); riêng nhiệt + gió nóng 0.027 [0.017; 0.037]; p_RW lần lượt 0.001 và 0.002. Độ lớn này vượt mức doanh thu mất (xem mục 6).
4. **Tổn thất ngân hàng (H3) đạt theo ngưỡng đã đăng ký, nhưng ngưỡng rất rộng:** cả 8 cặp (outcome × horizon) có CI90 nằm trong ±SESOI_y (SESOI_y từ 8.7 đến 10.0 điểm % dư nợ danh mục; SESOI = 5 cent × 19.96 triệu USD = 0.998 triệu USD mỗi +1 SD). Với ngưỡng phụ ±0.10 SD chỉ 2 trong 8 cặp đạt.
5. **Pass-through gần 0:** ở ngân hàng nông nghiệp một hạt, tổn thất ngân hàng khoảng 0.003 cent trên mỗi USD doanh thu cây trồng mất ở h = 1 (CI95 bootstrap [−0.671; 0.265] cent) và −0.036 cent ở h = 2 ([−1.184; 0.489]) — cận trên dưới 0.5 cent, thấp hơn nhiều so với 5 cent.
6. **Điều chỉnh danh mục (H4):** dư nợ vay sản xuất / tổng dư nợ t−1 giảm 1.19 điểm % ở h = 0 (CI95 [−1.94; −0.45], p_RW = 0.001) và 0.44 điểm % ở h = 1, nhưng ở h = 1 SE Conley không đáng tin (xem mục 7) và CI95 theo SE cụm-bang là [−1.31; 0.42] (p_RW = 0.273). Hiệu ứng h = 0 không đồng đều: nửa A −0.37 (CI [−1.41; 0.68]), nửa B −1.42; bỏ division West North Central cho −0.62 (CI [−1.42; 0.17]); nhiệt P90 −0.26 (CI [−0.69; 0.17]); nhiệt > 32°C −0.60 (CI [−1.72; 0.52]).
7. **H5 không đạt:** Nhiệt × Vốn đệm với tổn thất h = 1 là 0.002 ([−0.071; 0.076], dấu dự đoán âm), và với Δ dư nợ vay sản xuất h = 0 là −0.162 ([−0.288; −0.037], dấu dự đoán dương: ngược dấu).
8. **Thất bại (mô tả):** odds ratio mỗi +1 SD nhiệt 1.334 (CI95 [1.123; 1.583], 432 sự kiện) và 1.369 ([1.109; 1.690], 85 sự kiện khi bỏ 2009–2012).

## 2. Dữ liệu và mẫu cuối cùng
**Hạt (họ A, B, E), t 2006–2022:** BEA 69080 hạt-năm (3140 hạt) → nối nhiệt + mưa 53380 → 48 bang + DC có tâm hạt 51833 (3049 hạt) → A 51139 (3009 hạt); B 51153 (3009); E1/E2 44416 (2859, chỉ hạt-năm có bản ghi RMA).
**Ngân hàng (t 2006–2024):** Phase 1 120257 bank-năm (8587 ngân hàng) → có nhiệt footprint 119251 (8568) → đủ controls, division, tọa độ hạt trụ sở, mưa 118605 (8538) → t 2006–2024 107502 (8254). Ngân hàng nông nghiệp (FarmShare_pre ≥ 25%): 25403 bank-năm (1674 ngân hàng); một hạt: 13502 (1105). Mẫu hồi quy họ C: h = 1 từ 22355 đến 23177 bank-năm (1598–1612 ngân hàng), h = 2 từ 21647 đến 22539 (1562–1579 ngân hàng); họ D: 23879 (h = 0), 23236 (h = 1). Pass-through chính: 11488 (h = 1) và 11039 (h = 2) bank-năm, 1049 và 1022 ngân hàng.
**RMA:** 44 file 2001–2022, 178 MB, tải từ bản sao `www.rma.usda.gov` (chụp 3/2024), log SHA-256 ở `~/Projects/nckh_data/external/rma/download_log.csv`.

## 3. Kết quả từng họ (toàn mẫu là chính; A, B là kiểm tra nhất quán)
| Họ | Kết cục | Toàn mẫu β (SE) | CI95 | Nửa A β | Nửa B β |
|---|---|---|---|---|---|
| A | ln doanh thu cây trồng | −0.1246 (0.0199) | [−0.1637; −0.0855] | −0.0933 | −0.1323 |
| B | trợ cấp / baseline | 0.0007 (0.0062) | [−0.0114; 0.0128] | 0.0095 | −0.0024 |
| E1 | bồi thường nhiệt-hạn / baseline | 0.2167 (0.0422) | [0.1340; 0.2994] | 0.1737 | 0.2323 |
| E2 | bồi thường nhiệt + gió nóng / baseline | 0.0266 (0.0051) | [0.0166; 0.0365] | 0.0216 | 0.0259 |

**Họ C (TOST, CI90 Conley, SESOI_y theo công thức đóng băng):**
| Outcome | β (SE) | CI90 | SESOI_y | Đạt SESOI | Đạt ±0.10 SD |
|---|---|---|---|---|---|
| C1_h1 farmland NPL | −0.236 (0.154) | [−0.489; 0.018] | 9.951 | có | không |
| C1_h2 | −0.241 (0.126) | [−0.449; −0.033] | 9.836 | có | không |
| C2_h1 farmland net charge-off | −0.021 (0.028) | [−0.066; 0.024] | 9.951 | có | không |
| C2_h2 | −0.030 (0.025) | [−0.070; 0.011] | 9.836 | có | có |
| C3_h1 vay sản xuất NPL | 0.059 (0.095) | [−0.097; 0.215] | 8.877 | có | không |
| C3_h2 | 0.061 (0.084) | [−0.078; 0.200] | 8.744 | có | có |
| C4_h1 vay sản xuất net charge-off | 0.035 (0.048) | [−0.044; 0.114] | 8.892 | có | không |
| C4_h2 | 0.066 (0.053) | [−0.021; 0.153] | 8.733 | có | không |

H3 theo intersection-union (SESOI): **đạt (8/8)**. SESOI = 5% × |β̂ first stage USD| = 0.05 × 19.96 triệu USD (SE 8.23 triệu USD; N = 12638) = 998081 USD mỗi +1 SD; chia cho dư nợ danh mục trung vị.

**Họ D:** D1_h0 −1.193 (SE 0.380; CI95 [−1.938; −0.448]); D1_h1 −0.444 (SE Conley 0.083 không đáng tin vì phương sai Conley thô ≤ 0 và bị cắt trị riêng âm; SE cụm-bang 0.442, CI95 [−1.31; 0.42]); D2 (farmland, phụ) h = 0 −0.096 ([−0.430; 0.238]), h = 1 −0.185 ([−0.701; 0.332]). Romano–Wolf (2000 lần, cụm bang): D1_h0 p_RW = 0.001; D1_h1 p_RW = 0.273 (SE cụm-bang 0.442 so với SE Conley 0.083).

**Pass-through (cent tổn thất ngân hàng trên mỗi USD doanh thu mất):**
| Mẫu | h | PT | CI95 bootstrap | Tử số (USD) | Mẫu số (USD) |
|---|---|---|---|---|---|
| Chính (một hạt) | 1 | 0.003 | [−0.671; 0.265] | 567 | −19903640 |
| Chính | 2 | −0.036 | [−1.184; 0.489] | −7277 | −20081400 |
| Phụ (mọi ngân hàng nông nghiệp) | 1 | −0.014 | [−0.931; 0.740] | −2915 | −20933750 |
| Phụ | 2 | 0.150 | [−0.897; 1.026] | 31765 | −21228070 |
Nửa A có CI rộng hơn (h = 2: [−0.479; 10.459] cent), nửa B âm.

**H5 và thất bại:** xem tóm tắt (mục 1, điểm 7–8). Romano–Wolf: A 0.0005; B 0.858; D1_h0 0.001; D1_h1 0.273; E1 0.001; E2 0.002.

## 4. Áp tiêu chí diễn giải đã viết trước (mục 10 của kế hoạch)
**Sự thật từ dữ liệu:** H1 đạt (CI95 loại 0, đúng dấu, nhất quán hai nửa). H3 đạt theo định nghĩa đã đăng ký (8/8, CI90 trong ±SESOI_y). Nhánh áp dụng: **"câu đố có cơ sở"** — doanh thu cây trồng giảm nhưng tổn thất tín dụng ngân hàng ước lượng gần 0. Các kênh: H6 đạt (bồi thường bảo hiểm tăng mạnh) hỗ trợ kênh chuyển giao qua bảo hiểm; H2 (trợ cấp trực tiếp) không đạt; H4 đạt ở h = 0 (dư nợ vay sản xuất giảm 1.19 điểm %, p_RW = 0.001) nhưng chỉ mạnh vừa phải: 29 trên 33 đặc tả loại 0, hiệu ứng tập trung ở một division (bỏ West North Central thì CI chứa 0), nửa A không có hiệu ứng, thước đo nhiệt P90 và > 32°C cho CI chứa 0; phần "phục hồi một phần ở h = 1" không có CI đáng tin (Conley không xác định, SE cụm-bang cho CI chứa 0, và dấu đổi sang +0.44 khi trọng số theo dư nợ); H5 không đạt (hoãn/hấp thụ qua vốn đệm không được ủng hộ).
**Suy luận (của người soạn):** (i) "ngân hàng gần như không gánh" phù hợp với dữ liệu, nhưng ngưỡng SESOI rộng (khoảng 9 điểm % dư nợ danh mục, tức khoảng 2.7 lần SD của C1 và 16 lần SD của C2) nên H3 "đạt" ít mang tính thuyết phục; bằng chứng mạnh hơn là CI pass-through có cận trên khoảng 0.3–0.5 cent trên mỗi USD ở mẫu chính (mẫu phụ có cận trên 0.74 và 1.03 cent; nửa A h = 2 là 10.5 cent). CI pass-through chỉ tính trên các lần rút có mẫu số âm: mẫu chính loại 0.1% lần rút, nửa A loại 11%–12%. Seed bootstrap là 20261015 cộng độ lệch theo h và mẫu. (ii) Bồi thường bảo hiểm và điều chỉnh dư nợ là hai ứng viên giải thích; dữ liệu hiện có không phân tách được vai trò từng kênh.

## 5. Robustness và falsification (định trước; tổng hợp)
*Lưu ý cách đọc:* mỗi bảng đếm cả các đặc tả placebo và falsification (nhóm FarmShare thấp, nhiệt năm sau) trong mẫu số; với A và E1 hai ô không loại 0 chính là placebo và heat×khô, với B ô "1 loại 0" chính là placebo, và với họ C "33/33 tương đương" gồm cả ô falsification có SE rất lớn nên con số này ít có ý nghĩa. D1_h1: các CI Conley dưới 0.03 ở `drop_year:2011` và `no_controls` cũng là sản phẩm của bước cắt trị riêng âm.
| Kết cục | Số đặc tả | β chính | β min | β max | Cùng dấu với chính | CI95 loại 0 | Đạt tương đương SESOI |
|---|---|---|---|---|---|---|---|
| A | 26 | −0.125 | −0.134 | 0.006 | 25 | 24 | — |
| B | 26 | 0.001 | −0.010 | 0.011 | 16 | 1 | — |
| E1 | 26 | 0.217 | 0.003 | 0.245 | 26 | 24 | — |
| C1_h1 | 33 | −0.236 | −0.661 | 1.193 | 31 | 7 | 33 |
| C1_h2 | 33 | −0.241 | −0.569 | 3.926 | 31 | 9 | 33 |
| C2_h1 | 33 | −0.021 | −0.069 | 0.272 | 27 | 0 | 33 |
| C2_h2 | 33 | −0.030 | −0.069 | 1.806 | 28 | 1 | 33 |
| C3_h1 | 33 | 0.059 | −0.142 | 0.330 | 29 | 0 | 33 |
| C3_h2 | 33 | 0.061 | −0.086 | 0.339 | 29 | 0 | 33 |
| C4_h1 | 33 | 0.035 | −0.498 | 0.123 | 25 | 3 | 33 |
| C4_h2 | 33 | 0.066 | −1.182 | 0.191 | 28 | 7 | 33 |
| D1_h0 | 33 | −1.193 | −1.844 | −0.045 | 33 | 29 | — |
| D1_h1 | 33 | −0.444 | −0.651 | 0.442 | 30 | 15 | — |
- Mọi 33 đặc tả của mỗi cặp họ C đều đạt tương đương theo SESOI (ngưỡng rộng). Các giá trị β cực lớn ở C1, C2, C4 đến từ phép falsification nhóm FarmShare thấp (mẫu có dư nợ nông nghiệp nhỏ nên ước lượng rất không chính xác; ví dụ C1_h2 3.926, SE 3.412).
- **Placebo nhiệt năm sau cửa sổ:** A −0.019 ([−0.059; 0.020]), E1 0.003 ([−0.025; 0.031]), D1_h0 −0.160 ([−0.786; 0.465]) đều quanh 0; **họ B −0.010 ([−0.017; −0.003]) lệch khỏi 0** và C4_h1 có CI95 [0.005; 0.175]: hai điểm cần thận trọng.
- D1_h0 giữ dấu âm ở cả 33 đặc tả (từ −1.844 đến −0.045).

## 6. Sai khác so với kế hoạch
Không có. Mọi script ở trạng thái đã đóng băng (hash khớp). Hai bất thường nêu ở mục 7 là hạn chế/phát hiện, không phải sai khác.

## 7. Hạn chế và điều cần nhóm quyết
1. **SESOI quá rộng.** Ngưỡng 5 cent trên mỗi USD doanh thu mất của *cả hạt* quy ra 0.998 triệu USD mỗi +1 SD, trong khi dư nợ nông nghiệp trung vị của một ngân hàng chỉ khoảng 10 triệu USD. Ngân hàng có thể mất ~10% danh mục mà vẫn "tương đương". H3 đạt vì thế khá dễ; ngưỡng ±0.10 SD (đối chiếu) chỉ đạt 2/8. Nhóm cần cân nhắc dùng pass-through (cận trên 0.3–0.5 cent) làm bằng chứng chính cho "gần 0".
2. **Họ E có độ lớn đáng ngờ:** bồi thường nhiệt-hạn tăng 0.217 lần doanh thu cây trồng baseline mỗi +1 SD, lớn hơn mức giảm doanh thu cây trồng (khoảng 0.117 lần) — có thể do bồi thường gồm cả loại cây không nằm trong "cash receipts: crops" của BEA, hoặc nhiệt gắn với hạn trên diện rộng. Cần kiểm tra đơn vị/mức tổng hợp trước khi công bố con số.
3. **Họ B** khác kết quả feasibility (trợ cấp tăng khi chỉ có FE hạt + năm) vì đặc tả hiện dùng FE division×năm và kiểm soát mưa; placebo của B cũng lệch 0.
4. **SE:** (a) SE Conley của D1_h1 là sản phẩm của bước cắt trị riêng âm (phương sai thô ≤ 0, SE sau cắt 0.083 so với 0.362–0.449 của các SE cụm); các ô khác đã kiểm có phương sai thô dương. Kiểm định Conley chạy trên dữ liệu mô phỏng nên không bắt được trường hợp này. (b) Conley dưới hoán vị cho tỷ lệ bác bỏ 8% (A), 7% (C2_h1) và 14% (D1_h0) thay vì 5%; SE cụm-bang cho D1_h1 lớn hơn Conley 5 lần (0.442 so với 0.083) nên kết luận h = 1 cho H4 nên đọc theo p_RW (0.273).
5. **Dữ liệu:** chỉ Tmax (không Tmin); BEA đến 2022; RMA từ bản chụp 3/2024 và bố cục `sobcov` suy ra từ dữ liệu; mã 55 (SCO/STAX…) không có nguyên nhân cụ thể; thrift trước 2012; vay sản xuất bị cắt theo ngưỡng báo cáo (trong toàn bộ ngân hàng khoảng 62%–78% có số; trong mẫu ngân hàng nông nghiệp khoảng 91%–95%); ngân hàng chỉ nắm một phần nợ nông nghiệp của hạt (PT là cận dưới).
6. **Thất bại** là mô tả: 85 sự kiện khi bỏ 2009–2012, SE cụm bang, không điều chỉnh đa so sánh.
7. **Câu hỏi cho nhóm:** (a) dùng pass-through làm phát hiện chính thay vì TOST với SESOI hiện tại? (b) có kiểm tra thêm họ E bằng cách tách theo loại cây không? (c) có cần dùng wild bootstrap/SE cụm-bang làm chính cho H4 vì Conley đang rất hẹp? (d) bổ sung Tmin sau này (không bắt buộc)?

## Phụ lục (sau đóng băng; thăm dò, xem `POST_FREEZE_ADDENDUM.md`)
- **Pass-through** là phát hiện chính cho "tổn thất ngân hàng gần 0" (cận trên 0.265 cent ở h = 1 và 0.489 cent ở h = 2); TOST giữ nguyên như đã đăng ký nhưng ngưỡng rộng.
- **H4 đọc theo SE cụm-bang:** h = 0: −1.193 (SE 0.245, CI95 [−1.692; −0.694]); h = 1: −0.444 (SE 0.449, CI95 [−1.357; 0.470]); "phục hồi một phần ở h = 1" không được ủng hộ.
- **Họ E theo cây:** ngô 0.069, bông 0.069, lúa mì 0.033, đậu tương 0.022, cây khác 0.023 (tổng 0.217); dương ở mọi nhóm, độ lớn bất thường không do một loại cây riêng.
- Tmin không chạy.
