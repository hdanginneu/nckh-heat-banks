# DECISIONS — NCKH NEU: Heat → hành vi ngân hàng (hướng hiện hành)
Ghi từ 2026-11-05. Không coi lịch sử chat là nguồn chính thức. Hướng 1 (nông nghiệp, PAP v1) có nhật ký riêng: `_claude_eda/DECISIONS_LOG.md`.
Nhãn trạng thái: **[CHỐT]** Hdang/nhóm đã quyết · **[ĐỀ XUẤT]** do Claude đề xuất, chưa ai duyệt · **[PHÁT HIỆN]** kết quả kiểm tra, có số · **[MỞ]** còn bỏ ngỏ.
Quy tắc đã chốt từ trước (giữ nguyên): hệ số là tương quan có điều kiện; không chọn đặc tả theo kết quả; seed cố định; không điền 0 cho ô trống; kiểm leakage.

## D-01 (05/11) Mục tiêu: ưu tiên giải NCKH NEU; bỏ Q1 [CHỐT]
- Bỏ mục tiêu Q1; có thể nhắm Q2/Q3. Việc chính: thiết kế theo thang điểm NEU (Kết quả 40, Nội dung 20, Phương pháp 15, Tổng quan 10, Hình thức 5, Công bố 10).
- Mốc chính thức (CV1272, 01/06/2026): hội đồng cấp Khoa/đơn vị **trước 28/02/2027**; nộp Phòng QLKH 22–26/03/2027; Trường chấm trước 30/06/2027. [F, từ kế hoạch NEU] Ghi chú: NEU đang soạn Quy chế mới (NQ 09/NQ-ĐHKTQD, 05/2025) nên có thể đổi.
- [MỞ] Ngày họp hội đồng Khoa cụ thể chưa biết; cần hỏi Khoa.

## D-02 (05/11) Phạm vi dùng ngưỡng FarmShare: bỏ ngưỡng 25%, dùng FarmShare liên tục (phương án B) [CHỐT bởi Hdang]
- Lý do Hdang nêu: mốc 25% khó bảo vệ. Nguyên tắc kèm theo: mọi luận điểm phải bảo vệ được.
- Đặc tả: Heat × FarmShare_pre (FS10 = +10 điểm %), bank FE + division×năm FE, kèm Heat × (log tài sản, thanh khoản, vay/tài sản, vĩ độ). Chi tiết: `_claude_pap/rq3_explore/DESIGN_B_DRAFT.md`. Ngưỡng 15/25/35 chỉ để kiểm tra độ nhạy.
- Đây là thay đổi so với PAP v1 (ag25); PAP v2 phải ghi rõ là đặc tả mới.

## D-03 (05/11) Cấu trúc RQ và chuỗi câu chuyện [ĐỀ XUẤT; Hdang đồng ý tiến hành, nhóm/thầy chưa duyệt]
- Chuỗi: nhiệt → mất doanh thu cây trồng → bồi thường bảo hiểm → tổn thất ngân hàng ≈ 0 → ngân hàng có điều chỉnh phòng ngừa không?
- RQ1 first stage (đã có, hướng 1). RQ2 ai gánh/pass-through (đã có). RQ3 lõi mới: ngân hàng điều chỉnh **trước** khi lỗ (provision, allowance, thanh khoản) theo liều FarmShare.
- Capital hạ xuống phụ (đã thuộc Dreusch et al.); bỏ SBL và maturity khỏi bài chính.
- [MỞ] Tên đề tài chốt chưa; đề xuất cũ "Heat Stress and Balance-Sheet Adjustment in U.S. Community Banks…" cần sửa cho khớp chuỗi này.

## D-04 (05/11) Ba outcome chính của RQ3 [ĐỀ XUẤT]
1. Provision/dư nợ t−1 có điều kiện (NCO, ΔNPL, allowance trễ). 2. Δ allowance/dư nợ t−1 có điều kiện, dùng `allowance_legacy_kusd`. 3. Δ tỷ lệ thanh khoản. Chỉ h0 là chính; h1 phụ; H4 lặp lại để tách phần đã thấy.
- Control NCO/ΔNPL có thể là bad control; phải khai báo và báo cả bản không control.
- Xử lý CECL: mẫu chính 2007–2022; 2023–24 là mở rộng với dummy năm áp dụng CECL.

## D-05 (05/11) SESOI cho RQ3 [ĐỀ XUẤT, chờ nhóm]
- Đề xuất ±5% allowance stock cho +1 SD nhiệt (ở FarmShare 25%); phải đặt từ lập luận kinh tế TRƯỚC khi chạy. Bài học từ H3 (SESOI quá rộng nên "đạt 8/8" ít giá trị).

## D-06 (05/11) Biến nhiệt chính và baseline [ĐỀ XUẤT]
- Dùng `heat` của PAP v1 (GDD mùa vụ, trọng số tiền gửi t−1, chuẩn hóa SD). Nếu cần diễn đạt "bất ngờ": rolling 20 năm. Shock/Clim không tạo thêm biến thiên khi có bank FE (xem F-05).
- Heat × Clim (thích nghi) là giả thuyết kiểm định được; [MỞ] chưa chạy, chưa tính power.

## D-07 (05/11) Kỷ luật thăm dò [CHỐT bởi cách làm]
- Mọi thăm dò sau đóng băng nằm trong `_claude_pap/rq3_explore/`; KHÔNG ước lượng hệ số nhiệt thật cho outcome mới trước PAP v2; chỉ tính SE dưới H0 (heat placebo), phân phối, diagnostics.
- `freeze.py --verify` (05/11) báo LỆCH duy nhất ở `scripts/70_post_freeze_E_by_crop.py` (file thăm dò sau đóng băng từ 16/10, không nằm trong danh sách hash đóng băng; không phải do `rq3_explore/`). Mọi script và kế hoạch đã đóng băng không bị đổi.

## Phát hiện (05/11)
- **F-01 Dreusch et al. (EFM 2026) và Allen et al. (JFS 2022) đã đọc toàn văn.** Không bài nào làm allowance/provision với nhiệt; Dreusch chồng lấn mạnh với capital (RQ2b cũ); Allen là tiền lệ thanh khoản sau thiên tai (hazard khác, cú sốc theo quý). Chưa rà tìm kiếm rộng để khẳng định "chưa ai làm".
- **F-02 MDE** (placebo-lead, FE bank + division×năm): outcome RQ3 khoảng 0,04–0,11 sd; FE state×năm làm SE tăng 1,05–1,98 lần. Độ dốc theo FarmShare (toàn mẫu) MDE khoảng 0,036–0,070 sd. File: `rq3_explore/G1_*`, `G3_*`, `GB_*`.
- **F-03 Lỗi dữ liệu Phase 1:** `allowance_to_loans`/`allowance_loans_kusd` ≈ 0 với ngân hàng CECL (2023–24 TB 0,005 so với ~0,013). `allowance_legacy_kusd` liên tục (corr Δallowance vs provision−NCO = 0,915). [MỞ] đối chiếu MDRM.
- **F-04 E1 vs mất doanh thu:** mâu thuẫn do so log (−0,125) với tỷ lệ mức. Cùng thang mức: bồi thường 0,217 vs mất 0,237 (mỗi +1 SD). Tỷ lệ 0,91, CI bootstrap theo bang [0,56; 1,73]; mã nhiệt thuần/mất = 0,11 [0,07; 0,18]. ~88% E1 là mã Drought. Phát biểu được phép: bù ít nhất khoảng một nửa; không nói "gần hết"; không gắn riêng với nhiệt. File: `rq3_explore/G2_*`, `G2b_*`.
- **F-05 G4:** nhiệt dựng lại = gdd hiện có (corr 1,0000); `gdd_anom` hiện có ≈ Shock trọng số nhất quán (corr 0,9998; lỗi trọng số t−1/t−2 có thật nhưng ~2% sd); không có xu hướng ấm 2006–2023 (−0,14/năm, p=0,95); sau FE các baseline tương quan 0,98–0,998 → chọn baseline không đổi kết quả. Claude đã rút lại hai nhận định trước (xu hướng ấm; Shock/Clim tạo thêm biến thiên).
- **F-06 Giới hạn của hướng 1 cần nêu:** H4 chỉ mạnh ở một division (West North Central), nửa A không có hiệu ứng, h=1 không được ủng hộ; một số quyết định diễn giải được chốt sau khi thấy kết quả (pass-through là phát hiện chính; H4 đọc theo SE cụm-bang) → gắn nhãn thăm dò.

- **F-07 Biến bao phủ bảo hiểm cấp ngân hàng (G5):** dựng từ `rma_coverage_ratio.csv` (liability/doanh thu cây trồng 2001–05, tiền xác định), trọng số tiền gửi năm đầu của ngân hàng; 7.655/8.254 ngân hàng có giá trị. Trung vị 0,33 (toàn mẫu), 0,59 (FarmShare ≥ 15%); có ngoại lai (tối đa 3,06 và 10,4) → PAP v2 phải ghi cách winsorize. **Tương quan với FarmShare = 0,55** (với log tài sản −0,27): bao phủ phần lớn là proxy của mức tiếp xúc nông nghiệp; chỉ có thông tin riêng ở ngân hàng nông nghiệp (trong nhóm FarmShare ≥ 15%: sd 0,24; 25% phương sai nằm giữa các division). MDE (dưới H0, đơn vị điểm % dư nợ, theo +1 SD của biến tương tác): Heat×Clim — provision 0,018, Δallowance 0,014 (khoảng 0,025–0,036 sd); tam tương tác Heat×FS10×Cov — provision 0,007, Δallowance 0,005 mỗi đơn vị (đơn vị là tích nên không so trực tiếp với sd). File: `rq3_explore/G5_*`.

## D-08 (06/11) PAP v2 cho RQ3 viết và ĐÓNG BĂNG trước khi chạy [CHỐT bởi cách làm; nội dung [P] chờ nhóm duyệt]
- File: `_claude_pap/PAP_v2.md`; hash: `_claude_pap/hashes_frozen_v2.json` (`freeze_v2.py --verify` khớp sau khi chạy). PAP v1 không đổi.
- Đặc tả chính V2: FE ngân hàng + division×năm + dummy năm×{FS10, quy mô, thanh khoản, vĩ độ}; tương tác nhiệt×{FS10, Z}; Z bỏ vay/tài sản (corr −0,984 với thanh khoản).
- Suy luận chính đổi sang randomization inference (hoán vị năm thời tiết, R = 600) + Westfall–Young trên 3 outcome; Conley/cụm-bang chỉ mô tả. Lý do: dưới hoán vị năm, Conley lệch kích cỡ 10–19%, cụm-bang 31–45% (R nhỏ, thô).
- SESOI: allowance/provision ±5% quỹ dự phòng ở FS 25% (β2 ±0,026 pp); ΔLIQ ±0,10 SD/2,5. Heat×Clim bỏ. Heat×FS×Cov chỉ phụ.
- Khai báo đã thấy: provision raw×FS (feasibility), D1, loan growth. Δallowance và ΔLIQ chưa từng chạy với nhiệt thật trước v2.

## D-09 (06/11) Kết quả xác nhận RQ3 (PAP v2) [KẾT QUẢ; diễn giải [I]]
- Δallowance|cond: β2 −0,0019, p_RI 0,49, tương đương (CI90 ở FS 25% = [−1,2%; +0,5%] quỹ dự phòng). provision|cond: −0,0042, p_RI 0,14 (WY 0,21), tương đương.
- ΔLIQ: +0,178 điểm % tài sản (+0,45 ở FS 25%), p_RI = p_WY = 0,005; placebo đăng ký sạch; ổn định theo tiêu chí PAP nhưng bỏ West South Central còn 0,096 (không ý nghĩa).
- Kịch bản theo cây: S5 (thanh khoản) + S3 cho dự phòng. Chi tiết: `_claude_pap/RESULTS_RQ3_v2.md`.

## Phát hiện (06/11)
- **F-08 dALLOW ≈ provision − NCO** (hệ số 0,978; corr 0,915–0,919) → provision|cond và Δallowance|cond gần như cùng một biến; bằng chứng không độc lập.
- **F-09 Thăm dò sau đóng băng (`_claude_pap/rq3_v2_explore/`):** ΔLIQ tăng chủ yếu do dư nợ giảm (−0,325 điểm % tài sản, p_RI 0,006; vay sản xuất NN −0,132, phi NN −0,135), một phần sang chứng khoán; tiền gửi không tăng (−0,157, p_RI 0,09); NCO, NPL không tăng; khoảng một nửa đảo chiều năm sau (lag×FS −0,09). Không tách được cung/cầu.
- **F-10 Đặc tả cổ điển ag25 (nhiệt mức) có placebo hỏng cho ΔLIQ** (lead +0,39, p 0,005–0,017) → không dùng đặc tả mức cho thanh khoản.
- **F-11 Δallowance không điều kiện ở h1 âm** (−0,0137, p 0,008; ~−2,6% quỹ ở FS 25%), trong biên ±5% → cần giải thích hoặc gắn thăm dò.
- **F-12 Diễn đạt trong PAP_v2.md ô S3 ("bồi thường ≈ mất doanh thu") quá mạnh** so với F-04; khi viết bài dùng "bù ít nhất khoảng một nửa".
- **F-13 Quy trình:** script T1–T4 chạy với phiên bản `_v2_spec.py` trước khi sửa giao diện → bản đóng băng không tái tạo y nguyên output T1–T4 (output vẫn lưu ở `rq3_v2/out/`).

## D-10 (06/11) PAP v2.1 (cung/cầu tín dụng) viết, đóng băng, chạy [KẾT QUẢ]
- File: `_claude_pap/PAP_v2.1.md`, `hashes_frozen_v21.json`, kết quả `rq3_v21/results/`. Tóm tắt: RESULTS_RQ3_v2.md §8.
- M1 lãi suất ngầm định: không tăng (β2 +0,0054, p_RI 0,30; tương đương ±10 bp). M2 vốn trước kỳ: không đóng vai trò (p_RI 0,83). → C2 nghiêng về cầu, không loại trừ siết phi giá.
- Placebo hỏng cho dư nợ tổng (lead −0,198; Q1 đã âm) → C5 cho hiệu ứng dư nợ tổng.

## Phát hiện (06/11, chiều)
- **F-14 Vay sản xuất NN giảm là phần cơ chế sạch** (t −0,18; lead −0,002), còn dư nợ phi NN không nhận dạng được (lead −0,19 kể cả khi thêm lag). Sửa F-09 theo hướng này.
- **F-15 Nhiệt×FS có cấu trúc nhiều năm** (corr t–t+1 0,24; t−2–t+1 −0,32) → khi viết phải nói rõ hiệu ứng là trong năm, có phần đảo chiều năm sau.

- **F-16 Đối chiếu biến (06/11):** `liquidity_ratio` = (tiền và tiền gửi tại TCTD [RCON0081+0071] + HTM [1754/JJ34] + AFS [1773] + fed funds sold) / tổng tài sản — khớp tuyệt đối 100% số quan sát [F]. `allowance_legacy_kusd` = RCON3123 (Schedule RC mục 4.c: ALLL trước CECL, ACL trên khoản vay sau CECL) → liên tục qua CECL [F, hướng dẫn FFIEC]. `allowance_cecl_kusd` = RCONJJ30, ý nghĩa chưa đối chiếu [?]. FarmShare = (farmland + vay sản xuất NN)/tổng dư nợ, TB 3 năm đầu [F].
- **F-17 Bản thảo v1 (06/11):** doc "Heat Shocks and Agricultural Community Banks — Manuscript Draft v1" (Claude Docs, xuất được .docx); mọi số đối chiếu với output, citation chỉ dùng bài nhóm đã đọc; tên tác giả/tập/trang còn dấu [?] cần điền.

## D-11 (07/11) PAP v2.2 — khảo sát Fed khu vực (cung/cầu) [KẾT QUẢ]
- Đã tìm toàn bộ nguồn cấp khoản vay: FR 2028B và ARMS bí mật; FSA guaranteed nội bộ (chỉ FOIA); CRA chỉ ngân hàng trên ~1,3 tỷ USD; SBA 7(a) ít khoản vay NN. Dùng Fed District Ag Credit Surveys (7 khu vực, 1991–2026).
- Không chỉ số nào có ý nghĩa sau Westfall–Young; thu nhập nông trại giảm rõ (−7,8, p 0,005). Hướng: nhu cầu vay ↓ (p 0,065), vốn sẵn có và lãi suất không đổi, gia hạn ↑ (p 0,043), tài sản bảo đảm ↑ (p 0,079). → gợi ý cầu, không xác nhận. Chi tiết RESULTS §9.
- Sửa lỗi hiệu năng code v2.2 sau đóng băng (không đổi đặc tả), hash ở `hashes_v22_fix1.json`.

## D-12 (07/11) PAP v2.3 — hạn mức chưa giải ngân (FDIC API) và tương tác bảo hiểm [KẾT QUẢ]
- U1 hạn mức "khác" không đổi (−0,0008; p_RI 0,97; CI hẹp) → ngân hàng không cắt hạn mức. U2 nhiệt×FS×bao phủ cho vay sản xuất NN −0,022 (p_RI 0,26) → không phát hiện; chiều phù hợp với trả nợ bằng bồi thường. Không có dữ liệu lãi suất riêng khoản vay NN trong Call Report/FDIC API. Chi tiết RESULTS §10.

## D-13 (07/11) PAP v2.4 — chăn nuôi vs trồng trọt [KẾT QUẢ]
- Chênh lệch tổn thất/dự phòng ≈ 0 (p_RI 0,64–0,80). Nhưng nhiệt không làm giảm doanh thu chăn nuôi cấp hạt (+0,018, p 0,20) → phép thử không có nhóm "bị sốc, không bảo hiểm" → không kiểm định được kênh bảo hiểm. Không viết "bác bỏ".
- Phản ứng vay sản xuất và thanh khoản tập trung ở trồng trọt. Thu nhập ròng nông trại cấp hạt không giảm dù doanh thu trồng trọt −12% (thăm dò; cách BEA hạch toán bồi thường [?]). Chi tiết RESULTS §11.

## Việc còn mở (theo thứ tự)
1. Nhóm duyệt D-08/D-09 và các mục [P] (SESOI, cách phát biểu); chốt tên đề tài; xin ý kiến thầy về khung kết quả (RESULTS_RQ3_v2.md §4).
2. Nếu muốn tách cung/cầu tín dụng: viết PAP v2.1 trước khi chạy (số liệu quý q1–q4; lãi suất cho vay ngầm định).
3. Đối chiếu MDRM (allowance 3123, CECL) và định nghĩa liquidity_ratio.
4. Rà tài liệu: Allen et al. (JFS 2022) cho Discussion về thanh khoản; Vollmar & Wening, Cortés–Saxena–Singh; tìm kiếm rộng cho allowance/provision + nhiệt.
5. Viết bản thảo theo khung RESULTS_RQ3_v2.md §4.
6. Hỏi Khoa ngày hội đồng; đọc Thể lệ QĐ 2853/2021.
7. Tải 15 bài còn thiếu (Dreusch đã có).
(Danh sách cũ 05/11 trước khi cập nhật: xem `_claude_pap/rq3_v2/out/DECISIONS_backup_before_v2.md`.)
