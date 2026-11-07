# HANDOFF v3 — Giao việc nhóm (07/11/2026)

Đề tài: Nhiệt cực đoan và cách ngân hàng cộng đồng nông nghiệp Mỹ hấp thụ cú sốc.
Trưởng nhóm duyệt mọi output trước khi sang bước sau.

## 0. Việc đầu tiên của mọi người (trước 10/11)
1. Đọc theo thứ tự: `docs/` → `_claude_pap/RESULTS_RQ3_v2.md` → `DECISIONS.md` → tài liệu khung chi tiết (link mục 5).
2. Khánh, Thịnh: clone repo, làm đủ mục 2–4 của `README.md`. **Nghiệm thu:** `verify_data.py` báo "Lỗi: 0", `verify_hashes.py` báo "sai 0, thiếu 0", `_v2_build.py` ra panel 107.502 × 145 (đã thử: trùng tuyệt đối với bản gốc).
3. Mọi người xác nhận đã đọc bài toàn văn được giao ở mục 3.

## 1. Câu hỏi nghiên cứu
- RQ-A: nhiệt có làm NH ghi nhận thêm tổn thất (h=0..6; kiểm định chính h=0..3)?
- RQ-B: không có tổn thất ngay là do không có tổn thất, gia hạn nợ, hay ghi nhận trễ?
- RQ-C: cho vay, tiền gửi, thanh khoản điều chỉnh ra sao? (hạn hán chỉ là biến kiểm soát)

## 2. Các bước, người làm, output

| Bước | Việc | Người | Output bắt buộc | Nghiệm thu | Hạn |
|---|---|---|---|---|---|
| S1a | Kiểm mã Call Report: NCO tổng và nông nghiệp; nợ nông nghiệp quá hạn 30–89, ≥90, ngừng dồn tích; TDR; nợ bảo đảm bằng đất nông nghiệp. Ghi năm khả dụng, thay đổi khi áp dụng CECL, TDR bỏ từ 2023 | Hữu Anh | `rq3_v3/data/codebook_v3.csv` + 1 trang tóm tắt | Mỗi mã có nguồn FFIEC/MDRM | 15/11 |
| S1b | Công thức: outcome cộng dồn; LP h=0..6; hệ số "muộn (3..6) – sớm (0..1)" và RI cho hiệu số; TOST; MDE80 theo h; WY cho C1–C5 | Thịnh | `rq3_v3/methods/PAP_v3_formulas.md` | Khánh code được không phải hỏi lại | 15/11 |
| S1c | SESOI lấy từ Lu & Nikolaev 2024 (Bảng 2) và Özsoy 2025 (Bảng 2, 4), quy đổi sang đơn vị của mình; viết giả thuyết H1–H4 | Mai | `rq3_v3/PAP_v3_SESOI.md` | Mỗi số có bảng/trang nguồn | 15/11 |
| S1d | Ghép thành PAP v3, đóng băng bằng hash | Hdang | `PAP_v3.md`, `hashes_frozen_v3.json`, D-14 trong `DECISIONS.md` | Đã commit hash | 15/11 |
| S2 | Panel v3: outcome đến 2024; USDM (dự phòng PDSI) cân theo tiền gửi; PRISM 2023–2024; outcome cộng dồn không dùng thông tin tương lai cho biến giải thích | Hữu Anh | `panel_v3.parquet`, `DATA_DICTIONARY_v3.md`, báo cáo QA (số NH, % thiếu, tương quan Heat–Drought) | Đặc tả v2 chạy trên panel mới ra đúng β cũ (< 1e-6) | 22/11 |
| S3 | Chạy C1–C3, RI, WY, TOST, MDE | Khánh (Thịnh kiểm) | `rq3_v3/results/v3_confirmatory.csv`, hình LP | Thịnh tái tính 3 hệ số độc lập | 28/11 |
| S3' | Chọn trục bài: quiet / ghi nhận trễ / gia hạn nợ / không kết luận | Hdang | `RESULTS_RQ3_v3.md` | Theo bảng diễn giải đóng băng | 30/11 |
| — | Mùa thi: việc nhẹ, tự nguyện (Mai đọc nốt nguồn CẦN; Hdang dàn ý) | | | | 12/2026 |
| S4 | Độ vững ΔLIQ: bỏ từng vùng, từng năm, thêm Drought | Khánh | bảng + hình leave-one-out | | đầu 01 |
| S5 | Nhiệt vs hạn hán cho C1, C4, C5 | Khánh, Thịnh; Mai viết diễn giải | bảng + 1 đoạn đối chiếu Brei 2026 | | đầu 01 |
| S6 | Bảng hòa giải: chạy lại thiết kế Jaromczyk, Brei, Özsoy, Lu & Nikolaev trên cùng mẫu | Mai (đặc tả), Hữu Anh (biến), Khánh (chạy) | 1 bảng + 1 đoạn | Ghi trang/bảng nguồn | giữa 01 |
| S7 | Replication 2023–2024 (C4, C5, h=0..1) | Khánh | bảng | | giữa 01 |
| S8 | Sổ cái PAP v2–v3 + WY toàn họ | Thịnh | `PAP_LEDGER.md` | | giữa 01 |
| S10 | Bản thảo: Intro/Discussion (Hdang); Lit review, References (Mai); Data (Hữu Anh); Methodology (Thịnh); bảng/hình (Khánh) | Cả nhóm | bản thảo | Citation đối chiếu toàn văn | giữa 02 |
| S11 | Phản biện nội bộ; chạy lại toàn bộ từ đầu; định dạng NEU | Cả nhóm | bản nộp + thư mục tái lập | | trước hạn NEU |

Thiếu thời gian: bỏ S7 rồi S6. Không bỏ S3, S4, S5, S8.

## 3. Đọc toàn văn bắt buộc
| Người | Bài |
|---|---|
| Cả nhóm | Jaromczyk, Ifft & Ortiz-Bobea 2026; Lu & Nikolaev 2024; Brei et al. 2026 |
| Mai | + Özsoy et al. 2025; Scott et al. 2026; Allen et al. 2022; Heil et al. 2024; Schüwer et al. 2019; Dal Maso et al. 2024 |
| Thịnh, Khánh | + phần phương pháp của Lu & Nikolaev (Bảng 2, Panel A/B) |
| Hữu Anh | + phần dữ liệu của Brei 2026 (USDM) và Özsoy 2025 (PDSI) |

## 4. Quy tắc
- Không sửa file đã đóng băng; code mới vào `rq3_v3/`.
- Không chạy kiểm định xác nhận trước khi PAP v3 có hash.
- Hệ số là tương quan có điều kiện, không viết nhân quả.
- Kết quả xấu vẫn báo cáo đủ. Mỗi quyết định ghi vào `DECISIONS.md`.
- Sửa lỗi citation: bỏ con số "~25%" gán cho Deryugina & Hsiang.

## 5. Tài liệu và nơi để
| Tài liệu | Nơi |
|---|---|
| Code + PAP + kết quả v2–v2.4 | GitHub repo này |
| Dữ liệu đầu vào (`data_inputs/`, 407 MB, có MANIFEST.sha256) | Google Drive, thư mục "HANDOFF v3" |
| Bài tham khảo PDF | Drive: "Danh sách bài báo mới" (+ Lu & Nikolaev 2024, Özsoy 2025, Scott 2026 bổ sung) |
| Khung chi tiết & phân công | Claude Docs: "RQ3 v3 — Khung nghiên cứu chi tiết & phân công nhóm" |
| Đề cương gửi thầy; kế hoạch nhóm | Claude Docs (2 tài liệu) |
| Bản đồ tài liệu; ma trận luận điểm–bằng chứng; khung v3 | Project "NCKH NEU": `STEP0_LIT_MAP_GAP`, `CLAIM_EVIDENCE_MATRIX`, `RESEARCH_FRAMEWORK_FINAL_v3` |
