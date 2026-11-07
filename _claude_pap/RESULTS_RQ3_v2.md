# RESULTS RQ3 — PAP v2 (chạy 06/11/2026)
Nguồn số liệu: `rq3_v2/results/primary_ri_results.csv` (xác nhận), `rq3_v2/results/specs_run_v2.csv` (692 dòng, mọi đặc tả đã đăng ký), `rq3_v2_explore/E_results_long.csv` + `rq3_v2_explore/jobs/ri_*.npy` (thăm dò sau đóng băng).
Đóng băng: `hashes_frozen_v2.json` (đồng hồ VM 2026-11-05T18:50:52 UTC), `freeze_v2.py --verify` khớp toàn bộ sau khi chạy. Panel chạy sha256 `fe76ef29813a…` (`rq3_v2/results/prep_log.txt`). Kiểm tra nhất quán: β của bộ ước lượng nhanh dùng cho RI = β của fit_lp (chênh tối đa 8,8e-15).
Nhãn: [F] đọc trực tiếp từ output; [I] suy luận; [P] đề xuất; [?] chưa biết. Mọi hệ số là tương quan có điều kiện trong thiết kế "nhiệt như-ngẫu-nhiên theo năm", không phải tác động nhân quả của FarmShare.
Đơn vị β2: thay đổi của outcome cho +1 SD nhiệt × +10 điểm % FarmShare_pre. So ngân hàng FS = 25% với FS = 0: nhân 2,5.

## 1. Kết quả xác nhận (họ F1, đặc tả V2, h0, mẫu 2007–2022) [F]
| Outcome | β2 | sd hoán vị | p_RI | p_RI (Westfall–Young) | SE Conley / cụm-bang (p) | CI90 (RI) | SESOI | Kết luận theo PAP |
|---|---|---|---|---|---|---|---|---|
| Δallowance\|cond (pp dư nợ) | −0,0019 | 0,0026 | 0,488 | 0,488 | 0,0025 (0,46) / 0,0018 (0,31) | [−0,0062; 0,0024] | ±0,0263 | không phát hiện; **tương đương** |
| provision\|cond (pp dư nợ) | −0,0042 | 0,0028 | 0,136 | 0,211 | 0,0029 (0,15) / 0,0021 (0,045) | [−0,0087; 0,0003] | ±0,0263 | không phát hiện; **tương đương** |
| ΔLIQ (điểm % tài sản) | +0,178 | 0,051 | 0,005 | 0,005 | 0,058 (0,002) / 0,044 (0,0002) | [0,094; 0,263] | ±0,216 | **phát hiện (dương)** |
R = 600 hoán vị năm thời tiết; N = 88.287 bank-năm/7.650 ngân hàng (allowance, provision), 89.637/7.740 (ΔLIQ). Với ΔLIQ chỉ 2/600 hoán vị có |β*| ≥ |β̂| (p = 3/601 = 0,005), kể cả sau WY.
Độ lớn [F→I]:
- Dự phòng: ở FS = 25%, CI90 của chênh lệch là [−0,016; +0,006] pp dư nợ, tức [−1,2%; +0,5%] quỹ dự phòng trung vị (1,31 pp). Biên tương đương ±5% đã đăng ký rộng hơn nhiều so với CI → kết luận "không trích lập phòng ngừa đáng kể" không phụ thuộc nhiều vào SESOI (vẫn đạt nếu SESOI chỉ ~2%). Provision: [−1,7%; +0,06%].
- Thanh khoản: ở FS = 25%, +0,45 điểm % tài sản (CI90 [0,23; 0,66]); bằng 0,08 SD của ΔLIQ; tỷ lệ thanh khoản trung bình ~32% tài sản → tăng tương đối ~1,4%. Có ý nghĩa thống kê, độ lớn kinh tế nhỏ.
- β1 (nhiệt ở FS = 0) không khác 0 cho cả ba outcome (p_RI 0,23–0,56).
Hiệu chuẩn SE: sd hoán vị / SE Conley = 0,89–1,03; / SE cụm-bang = 1,16–1,42 → SE cụm-bang hẹp quá; Conley gần đúng ở đặc tả V2 [F].

## 2. Kiểm tra đã đăng ký [F]
- Placebo (nhiệt t+1, hai vế, V2): lead×FS10 = +0,0016 (p 0,53/0,53) Δallowance; +0,0001 (0,97/0,98) provision; +0,054 (0,16/0,18) ΔLIQ → không kích hoạt quy tắc §5.5. Lưu ý [I]: với ΔLIQ, lead bằng ~30% hệ số chính và cùng dấu (không có ý nghĩa).
- Biến thể: V0 / V1 / V2: ΔLIQ 0,177 / 0,182 / 0,178 (p_RI 0,050 với R=100 / 0,010 / 0,005); Δallowance −0,0024 / −0,0022 / −0,0019; provision −0,0014 / −0,0035 / −0,0042.
- Bỏ từng division (9): ΔLIQ dương cả 9, 0,174–0,205 trừ **bỏ West South Central = 0,096 (p 0,29 Conley; 0,10 bang)**; Δallowance âm nhỏ cả 9 (−0,0006 … −0,0028; p ≥ 0,14). Theo tiêu chí PAP (cùng dấu ≥ 7/9, độ lớn 0,5–2 lần) → "ổn định", nhưng sát ngưỡng (0,54 lần).
- Năm 2009–2022: ΔLIQ 0,195 (p 0,0006); Δallowance +0,0005; provision −0,0018. Mở rộng 2007–2024 + cecl_post: Δallowance −0,0010; provision −0,0041 (bang p 0,03).
- Winsorize 0,5% / không winsorize: ΔLIQ 0,184 / 0,203; Δallowance −0,0022 / −0,0049; provision −0,0044 / −0,0063.
- Liều–đáp theo bin FarmShare (gốc < 5%), ΔLIQ: 5–15%: −0,05; 15–25%: +0,16; 25–35%: +0,47 (p 0,012/0,0004); > 35%: +0,70 (p 0,008/0,002) → tăng đơn điệu từ 15%. Δallowance: không bin nào có ý nghĩa; provision: bin > 35% = −0,026 (p 0,04).
- Ngưỡng nhị phân (thay FS10): ΔLIQ ag15 0,39; ag25 0,55; ag35 0,51 (đều p < 0,02); Δallowance/provision không có ý nghĩa.
- Không điều kiện hoá / h1 (phụ): Δallowance raw −0,0059 (p 0,052/0,016); provision raw −0,0051 (0,30); Δallowance h1 (t−1→t+1) **−0,0137 (p 0,008/0,003)**; provision h1 −0,017 (0,047/0,080); ΔLIQ h1 +0,051 (0,41). D1 (Δ vay sản xuất nông nghiệp/dư nợ) −0,251 (p < 0,001) — đã thấy ở feasibility (d_agprod).
- Heat×FS10×Cov (bao phủ bảo hiểm, phụ): provision −0,0052 (p 0,04/0,007); Δallowance −0,0027 (0,21/0,07); ΔLIQ +0,050 (0,21/0,05). Không hiệu chỉnh đa kiểm định; chỉ gợi ý.
- Đặc tả cổ điển ag25 (nhiệt mức, không tương tác, thăm dò): ΔLIQ heat +0,88 (p 0,004) **nhưng placebo lead +0,39 (p 0,017/0,005) — hỏng**; Δallowance, provision ≈ 0.

## 3. Thăm dò sau đóng băng (không thuộc phần xác nhận) — `rq3_v2_explore/` [F số; I diễn giải]
Cùng đặc tả V2; đơn vị: điểm % tổng tài sản t−1 trừ khi ghi khác.
| Thành phần | β2 | p Conley / bang | p_RI (R=180) |
|---|---|---|---|
| Δ cho vay tổng | −0,325 | 0,0002 / 0,0002 | 0,006 (cực trị trong 180) |
| … Δ vay sản xuất nông nghiệp | −0,132 | 0,002 / <0,001 | 0,006 |
| … Δ vay farmland | −0,011 | 0,33 / 0,49 | — |
| … Δ vay phi nông nghiệp | −0,135 | 0,008 / 0,096 | 0,039 |
| Δ tài sản thanh khoản (LIQ×TA) | +0,137 | 0,074 / 0,069 | — |
| … Δ chứng khoán (HTM+AFS) | +0,144 | 0,084 / 0,019 | — |
| … Δ tiền mặt | +0,038 | 0,38 / 0,36 | — |
| Δ tổng tài sản | −0,162 | 0,091 / 0,25 | — |
| Δ tiền gửi | −0,157 | 0,068 / 0,20 | 0,094 |
| Δ vốn chủ sở hữu | −0,007 | 0,48 / 0,52 | — |
| NCO (pp dư nợ) | +0,006 | 0,18 / 0,24 | — |
| ΔNPL (pp) | −0,015 | 0,061 / 0,16 | — |
Kiểm tra nhất quán [F]: ΔLIQ ≈ ΔLA − LIQ_{t−1}·ΔTA ≈ 0,137 + 0,32×0,162 ≈ 0,19 ≈ 0,178.
Độ bền ΔLIQ: jackknife bỏ từng năm 0,147 (bỏ 2011) – 0,191, mọi p Conley < 0,06; bỏ riêng WSC×2011: 0,146 (p 0,043/0,008); FE ngân hàng + bang×năm: 0,198 (p 0,0003). Placebo lead2 −0,023 (0,66), lead3 +0,038 (0,41). Độ trễ: thêm nhiệt t−1×FS10 = −0,090 (p 0,09/0,011); cùng lúc lead và lag: hiện tại 0,167, lag −0,083, lead 0,047 → khoảng một nửa đảo chiều năm sau [I: phản ứng tạm thời].
Diễn giải [I]: tỷ lệ thanh khoản tăng chủ yếu vì DƯ NỢ GIẢM (cả vay sản xuất nông nghiệp và vay phi nông nghiệp), một phần chuyển sang chứng khoán; tiền gửi KHÔNG tăng (nếu có thì giảm) → không ủng hộ câu chuyện "tiền bồi thường chảy vào tiền gửi". Không thấy NCO/NPL tăng trong năm → không có tổn thất cần dự phòng ở h0, phù hợp với kết quả không trích lập. Không phân biệt được cầu (nông dân trả nợ bằng bồi thường/ít vay) với cung (ngân hàng siết) bằng dữ liệu cấp ngân hàng-năm.

## 4. Theo cây diễn giải đã đăng ký: bài báo trở thành gì
Kịch bản khớp: S5 (chỉ thanh khoản) + S3 cho dự phòng (null có tương đương), placebo đăng ký sạch, ổn định theo tiêu chí PAP.
Phát biểu được phép (tiếng Anh, tiết chế) [P]:
- "Farm-exposed community banks do not build loan-loss reserves beyond realized losses after unusually hot growing seasons; the 90% interval rules out differential reserve responses larger than about 1–2% of the allowance stock at a 25% farm share."
- "Heat shocks are associated with a temporary rise in the liquidity ratio of farm-exposed banks (+0.45 percentage points of assets at a 25% farm share per 1 SD of heat), which exploratory decompositions attribute mainly to lower loan balances rather than deposit inflows."
Không được phát biểu: ngân hàng "trích lập phòng ngừa"; "bảo hiểm làm ngân hàng không cần phản ứng" (chưa nhận dạng kênh bảo hiểm); "tiền bồi thường làm tăng tiền gửi"; "ngân hàng siết tín dụng" (cung/cầu chưa tách); bồi thường "bù gần hết" mất doanh thu (F-04: chỉ "ít nhất khoảng một nửa", CI 0,56–1,73). Lưu ý: ô S3 trong PAP_v2.md viết "bồi thường ≈ mất doanh thu" — diễn đạt đó quá mạnh, dùng theo F-04.
Khung bài [P]: (1) Hướng 1: nhiệt → doanh thu cây trồng −11,7%/SD (hạt), bồi thường bù ít nhất khoảng một nửa; (2) RQ3 xác nhận: không trích lập vượt tổn thất (tương đương), thanh khoản tăng; (3) thăm dò: dư nợ giảm, không có tổn thất tín dụng tăng, phản ứng tạm thời. Tên gợi ý: "Heat Shocks and Agricultural Community Banks: No Precautionary Provisioning, a Temporary Shift from Loans to Liquid Assets". Đủ cho giải NCKH NEU nếu viết trung thực; để lên Q2/Q3 cần tách cung–cầu tín dụng.

## 5. Reviewer sẽ đánh trước [I]
1. Tập trung vùng: bỏ West South Central làm ΔLIQ giảm còn 0,096 (không có ý nghĩa); H4 v1 cũng chỉ mạnh ở West North Central → câu hỏi "hiệu ứng có phải của vài vùng–năm?". Đã có: FE bang×năm giữ nguyên (0,198); jackknife năm ổn định; nhưng phải nêu thẳng.
2. Placebo của đặc tả cổ điển (ag25, nhiệt mức) hỏng (lead +0,39) → đặc tả mức không dùng được; V2 giảm vấn đề (lead×FS10 0,05, không ý nghĩa) nhưng chưa bằng 0.
3. Cơ chế cung/cầu chưa nhận dạng; tiền gửi giảm nhẹ là bất ngờ [?].
4. Độ lớn kinh tế nhỏ (0,08 SD); null dự phòng có thể do không có tổn thất ở h0 (NCO, NPL không tăng) → "không cần" chứ chưa chắc "không thận trọng".
5. FarmShare không ngẫu nhiên; V2 chỉ kiểm soát gradient tuyến tính theo năm của quy mô, thanh khoản, vĩ độ.
6. RI dựa vào "các năm thời tiết trao đổi được" với ~19 năm; không có xu hướng nhiệt 2006–2023 (G4) nhưng vẫn là giả định.
7. Dữ liệu đã thấy trước: provision raw×FS (feasibility), D1, loan growth → provision\|cond chỉ xác nhận một phần.
8. Định nghĩa liquidity_ratio và MDRM allowance/CECL chưa đối chiếu tài liệu chính thức [?].
9. Δallowance không điều kiện ở h1 âm (−0,0137, p 0,008; ~−2,6% quỹ ở FS 25%) — nằm trong biên ±5% nhưng khác 0: cần giải thích (ít tổn thất → xả dự phòng?) hoặc nêu là thăm dò.

## 6. Ghi chú quy trình [F]
- Toàn bộ 149 job đăng ký đã chạy; không bỏ đặc tả nào. Mọi phân tích trong §3 thực hiện SAU khi thấy kết quả xác nhận → thăm dò.
- Các script chẩn đoán T1–T4 được chạy với phiên bản `_v2_spec.py` trước khi sửa giao diện hàm; bản đóng băng không tái tạo y nguyên output T1–T4 (số liệu vẫn lưu ở `rq3_v2/out/`).
- Mất kết nối máy hai lần trong khi chạy; job ghi nguyên tử (tạm → đổi tên) nên không có job dở dang được tính.

## 7. Việc tiếp theo đề xuất [P]
1. Nhóm duyệt kết quả và các mục [P] (SESOI, cách phát biểu); chốt tên đề tài.
2. Nếu muốn tách cung–cầu: viết PAP v2.1 TRƯỚC khi chạy, dùng số liệu quý (Phase 1 có q1–q4: dư nợ, tiền gửi) để xem dư nợ giảm vào quý nào so với thời điểm chi trả bồi thường; thêm lãi suất cho vay (loan_interest_fees/dư nợ) — giá giảm + lượng giảm gợi ý cầu, giá tăng + lượng giảm gợi ý cung.
3. Đối chiếu Allen et al. (JFS 2022) về thanh khoản sau thiên tai cho phần Discussion.
4. Đối chiếu MDRM cho allowance (3123) và định nghĩa liquidity_ratio.
5. Viết bản thảo theo khung §4; bảng chính = §1, bảng độ bền = §2, bảng cơ chế = §3 (ghi rõ thăm dò).

## 8. PAP v2.1 — cung hay cầu tín dụng (đóng băng 2026-11-06T06:42 UTC, `hashes_frozen_v21.json`; kết quả `rq3_v21/results/`) [F]
| Kiểm tra | Hệ số | p_RI (WY) | SE Conley / bang (p) | CI90 (RI) | Kết luận theo PAP v2.1 |
|---|---|---|---|---|---|
| M1 Δ lãi suất cho vay ngầm định (pp) | β2 = +0,0054 | 0,30 (0,54) | 0,0048 (0,25) / 0,0048 (0,26) | [−0,0028; +0,0137] | không phát hiện; **tương đương** (ở FS 25%: −0,7 đến +3,4 điểm cơ bản, trong ±10 bp) |
| M2 Δ dư nợ × vốn trước kỳ | β3 = +0,0086 | 0,83 (0,83) | 0,032 (0,79) / 0,026 (0,74) | [−0,053; +0,070] | không phát hiện |
R = 300; kiểm tra nhất quán bộ ước lượng nhanh = fit_lp (chênh 9e-16). Placebo đăng ký: lead × FS10 cho M1 = −0,0002 (p 0,97); lead × FS10×CAP cho M2 = +0,034 (p 0,39/0,32) — sạch cho hai hệ số xác nhận; NHƯNG lead × FS10 trong đặc tả M2 = **−0,198 (p 0,006/0,016)** → quy tắc §3 của v2.1 kích hoạt "mối lo nhận dạng" cho hiệu ứng mức của dư nợ.
Theo cây v2.1: **C2 — nghiêng về cầu** cho hai kiểm tra xác nhận (giá không tăng; vốn không đóng vai trò), kèm C5 cho chính hiệu ứng dư nợ tổng.
M3 thời điểm (mô tả; β2 tích luỹ từ Q4_{t−1}, điểm % tài sản t−1): dư nợ tổng Q1 −0,070 (p 0,021/0,008), Q2 −0,146, Q3 −0,301, Q4 −0,325; vay sản xuất NN Q1 −0,040 (p 0,037/0,046), Q2 −0,060, Q3 −0,125, Q4 −0,132. Phần lớn giảm xảy ra ở Q2–Q3 (mùa sinh trưởng/thu hoạch), nhưng **Q1 (placebo) đã âm và có ý nghĩa** → một phần hiệu ứng có trước mùa nóng.
Phụ: M1 ở V0 −0,0059 (p 0,13); ΔAGP × CAP −0,007 (p 0,52).

### 8b. Thăm dò sau v2.1: độ trễ phân phối (nhiệt t−2, t−1, t, t+1 cùng lúc; V2) — `rq3_v2_explore/E2_distlag.py`
| Outcome | t | t−1 | t−2 | t+1 (placebo) |
|---|---|---|---|---|
| Δ vay sản xuất NN | −0,181 (p<0,001) | +0,076 (0,001) | −0,063 (0,001) | **−0,002 (0,94) sạch** |
| Δ dư nợ tổng | −0,303 (0,001) | +0,069 (0,32) | −0,066 (0,33) | **−0,190 (0,002 / 0,031) hỏng** |
| ΔLIQ | +0,196 (<0,001) | −0,090 (0,08/0,02) | +0,109 (0,01) | +0,060 (0,15) |
Tương quan (sau FE) giữa các số hạng nhiệt×FS: t với t+1 = 0,24; t−2 với t+1 = −0,32 → nhiệt có cấu trúc nhiều năm.
Diễn giải [I]: phần đáng tin của cơ chế là **vay sản xuất nông nghiệp giảm trong năm nóng** (đúng thời điểm, placebo sạch, D1 cùng chiều). Phần giảm của dư nợ phi nông nghiệp KHÔNG được quy cho nhiệt (placebo hỏng). ΔLIQ vẫn giữ (lead không có ý nghĩa). Giá cho vay không tăng và ngân hàng vốn mỏng không cắt nhiều hơn → phù hợp với cầu giảm/trả nợ hơn là siết qua giá; không loại trừ siết phi giá.
Sửa phát biểu so với §3–§4: thay "dư nợ giảm (cả NN và phi NN)" bằng "vay sản xuất NN giảm; thay đổi dư nợ phi NN không nhận dạng được".

## 9. PAP v2.2 — khảo sát ngân hàng nông nghiệp của 7 khu vực Fed (đóng băng `hashes_frozen_v22.json`; sửa hiệu năng `hashes_v22_fix1.json`, không đổi đặc tả) [F]
Dữ liệu: KC Fed, Federal Reserve District Surveys of Ag Credit Conditions (Historical Data Q2 2026), tải 07/11/2026 vào `data_external/fed_ag_survey/`. Nhiệt khu vực-năm trọng số doanh thu cây trồng; FE khu vực + năm; RI R = 2000. Đơn vị β: điểm chỉ số khuếch tán / +1 SD nhiệt. Kết quả: `rq3_v22/results/v22_results.csv`.
| Chỉ số (Q4 năm t) | β | p_RI | p_WY | SD của chỉ số |
|---|---|---|---|---|
| Nhu cầu vay | −2,13 | 0,065 | 0,21 | 18,7 |
| Vốn sẵn có để cho vay | −0,22 | 0,83 | 0,83 | 17,7 |
| Tỷ lệ trả nợ | −1,44 | 0,34 | 0,54 | 25,4 |
| Gia hạn/kéo dài | +2,38 | 0,043 | 0,20 | 18,4 |
| Yêu cầu tài sản bảo đảm | +1,48 | 0,079 | 0,21 | 10,8 |
| (kiểm tra) Thu nhập nông trại | −7,80 | 0,005 | — | 49,8 |
| (phụ) Lãi suất cố định vay vốn lưu động | +0,007 pp | 0,76 | — | 1,7 |
Q3_t: nhu cầu −2,35 (p 0,051), thu nhập −10,7 (0,012). Q1_{t+1}: vốn sẵn có −1,62 (0,061), còn lại không ý nghĩa. Placebo Q1_t: không chỉ số nào p < 0,05 (tài sản bảo đảm −1,38, p 0,076).
Theo cây v2.2: không phát hiện sau WY → "không phân biệt được ở cấp khu vực". Diễn giải [I]: cú sốc có thật (thu nhập nông trại giảm rõ); hướng các chỉ số nghiêng về cầu giảm (nhu cầu vay ↓, vốn sẵn có và lãi suất không đổi) kèm dấu hiệu căng thẳng nhẹ của người vay (gia hạn ↑, tài sản bảo đảm ↑); không thấy siết qua vốn hay giá. Độ lớn nhỏ (~0,1 SD). Bằng chứng gợi ý, không phải xác nhận.
Kết luận cho hướng (a): dữ liệu cấp khoản vay không tiếp cận được (FR 2028B, ARMS bí mật; FSA nội bộ); CRA và SBA không bao phủ ngân hàng cộng đồng nông nghiệp. Khảo sát Fed khu vực là nguồn tốt nhất có thể dùng, và không tách được cung/cầu một cách chắc chắn.

## 10. PAP v2.3 — hạn mức chưa giải ngân và vai trò bảo hiểm (đóng băng `hashes_frozen_v23.json`; kết quả `rq3_v23/results/`) [F]
Dữ liệu FDIC BankFind API tải 07/11/2026 (`data_external/fdic_api/`, 265.053 bản ghi; khớp 97,3% bank-năm). R = 300; kiểm tra nhất quán chênh 1e-15.
| Kiểm định | Hệ số | p_RI (WY) | CI90 (RI) | Đọc theo cây |
|---|---|---|---|---|
| U1 Δ hạn mức chưa giải ngân "khác" / TA (nhiệt × FS10) | −0,0008 | 0,97 (0,97) | [−0,041; 0,039] | Không đổi (SD 2,0) |
| U2 Δ vay sản xuất NN × bao phủ (ba chiều) | −0,022 | 0,26 (0,44) | [−0,054; 0,010] | Không phát hiện; chiều âm (giảm mạnh hơn nơi bao phủ cao) |
Phụ: ΔUC tổng +0,007 (p 0,74); NCO × Cov −0,0055 (p 0,13/0,09); ΔNPL × Cov −0,0095 (0,28/0,15); Δ log số khoản vay NN < 100 nghìn −0,18 (0,45). Placebo lead: U1 −0,035 (0,08/0,065), U2 ba chiều +0,016 (0,39/0,10) → không kích hoạt.
Theo cây v2.3: không phân biệt được bằng hai phép thử. Diễn giải [I]: ngân hàng không cắt hạn mức (bác bỏ dạng siết qua cắt hạn mức, trong phạm vi proxy UCOTHER không riêng nông nghiệp); chiều của tương tác bảo hiểm (vay sản xuất giảm mạnh hơn và tổn thất tăng ít hơn nơi bao phủ cao) phù hợp với câu chuyện bảo hiểm + trả nợ, nhưng không có ý nghĩa thống kê.

## 11. PAP v2.4 — chăn nuôi (gần như không bảo hiểm) so với trồng trọt (có bảo hiểm) (đóng băng `hashes_frozen_v24.json`; kết quả `rq3_v24/results/`) [F]
LIV (tỷ trọng chăn nuôi trong doanh thu NN của footprint, BEA 2001–05): TB 0,47, SD 0,28, tương quan với FarmShare 0,18. R = 300; kiểm tra nhất quán chênh 0.
| Outcome h0 | Δ = β_chăn nuôi − β_trồng trọt | p_RI | p_WY | CI90 (RI) |
|---|---|---|---|---|
| NCO (pp dư nợ) | −0,0059 | 0,72 | 0,98 | [−0,032; 0,020] |
| ΔNPL (pp) | −0,0143 | 0,66 | 0,98 | [−0,068; 0,040] |
| Provision (pp dư nợ) | −0,0041 | 0,80 | 0,98 | [−0,030; 0,022] |
| Δallowance (pp dư nợ) | −0,0045 | 0,64 | 0,98 | [−0,021; 0,012] |
Phụ: vay sản xuất NN: trồng trọt −0,209 (p 0,0006), chăn nuôi −0,077 (0,15); ΔLIQ: trồng trọt +0,324 (0,008), chăn nuôi +0,112 (0,053); allowance h1 chăn nuôi −0,019 (0,006). Placebo lead của chênh lệch: NCO +0,004 (0,82), ΔNPL −0,033 (0,26).
Kiểm tra cấp hạt (đăng ký ở mục Phụ, `rq3_v24/county_check.py`, FE hạt + division×năm, SE cụm bang): ln doanh thu chăn nuôi +0,018 (p 0,20) — **nhiệt GDD > 29°C mùa vụ không làm giảm doanh thu chăn nuôi**; ln doanh thu trồng trọt −0,125 (p < 0,001); thu nhập ròng / doanh thu +0,010 (p 0,37); × tỷ trọng chăn nuôi −0,020 (0,39).
Theo cây v2.4: Δ ≈ 0 và cả hai β ≈ 0. NHƯNG vì phía chăn nuôi không chịu cú sốc doanh thu, phép thử này **không kiểm định được** kênh bảo hiểm (không có "nhóm bị sốc mà không có bảo hiểm" để so sánh) [I]. Không được viết là "kênh bảo hiểm bị bác bỏ".
Quan sát thăm dò [I, ?]: doanh thu trồng trọt giảm 12% nhưng thu nhập ròng nông trại cấp hạt không giảm — phù hợp với việc thu nhập nông dân được đệm (bảo hiểm, chi phí, giá); cách BEA hạch toán tiền bồi thường bảo hiểm trong thu nhập ròng cần đối chiếu [?].
Phản ứng bảng cân đối (vay sản xuất giảm, thanh khoản tăng) tập trung ở tiếp xúc trồng trọt — đúng nơi có cú sốc doanh thu và có bảo hiểm.
