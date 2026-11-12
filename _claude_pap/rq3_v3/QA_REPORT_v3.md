# Báo cáo QA panel_v3 (bước S2), 12/11/2026

Chạy `python3 build_v3.py` rồi `python3 qa_v3.py`. Số liệu chi tiết nằm trong `qa/`. QA chỉ đếm, so khớp, mô tả và tính tương quan nhiệt–hạn hán; không ước lượng hệ số nhiệt nào.

## Kết luận

Panel_v3 đạt nghiệm thu S2. Có bốn điểm cần đưa vào quyết định trước khi đóng băng PAP v3: C3 dùng biến nào, cửa sổ cú sốc, cách đưa hạn hán vào mô hình, và rủi ro attrition ở h lớn.

## 1. Nghiệm thu S2 [F]

- 145/145 cột v2 trong panel_v3 trùng khớp tuyệt đối với `panel_v2.parquet` (cùng giá trị, cùng vị trí NaN). Đặc tả v2 chạy trên panel_v3 vì vậy cho đúng β cũ.
- Dựng lại `heat` từ cùng ma trận trọng số W dùng cho hạn hán: sai khác lớn nhất 1,8e−15 trên 107.502 dòng.
- Định nghĩa mới khớp định nghĩa cũ trên các dòng cùng có số: `NCOc_h0` = `NCO_h0` (v2), `LIQ_h0` = `dLIQ_h0`, `ALLOW_h0` = `dALLOW_h0`, `ALLOW_h1` = `dALLOW_h1`, `NCOfl_h0..3` = `C2_h0..3` (v1), `AGLt_h0..3` = `D1+D2` (v1). Sai khác lớn nhất 6e−14.

## 2. Số quan sát (đủ biến của frame v2; t từ 2007)

| Outcome | h | Cú sốc t | n | Ngân hàng |
| --- | --- | --- | --- | --- |
| C1 `NCOc` | 6 | 2007–2018 | 55.363 | 6.075 |
| C1 `NCOc` | 6 | 2007–2019 (dùng số liệu 2025) | 59.172 | 6.080 |
| C2 `ALLOW`, bỏ NH áp dụng CECL sớm | 0 / 6 | 2007–2022 / 2007–2016 | 89.284 / 47.163 | 7.700 / 6.070 |
| C3 `PDNAflt` | 0 / 1 | 2007–2024 / 2007–2023 | 97.525 / 89.732 | – |
| C3 `PDNAfl` | 0 / 1 | như trên | 79.897 / 73.703 | – |
| C3 `PDNAag` (bản Thịnh) | 0 / 1 | như trên | 51.248 / 46.549 | – |
| C4 `LIQ` | 0 | 2007–2024 | 97.526 | – |
| C5 `AGL` | 2 | 2007–2022 | 69.330 | – |

Bảng đầy đủ: `qa/obs_by_outcome_h.csv` và `qa/obs_C2_cecl_window.csv`. Số dòng C2 bị loại do áp dụng CECL sớm trong cửa sổ: 127–228 tùy h.

## 3. C3: chọn biến [F, I]

Tỷ lệ dòng có số ở h = 0, theo FarmShare_pre (t = 2007–2023):

| FarmShare_pre | n | `PDNAfl` | `PDNAag` (bản Thịnh) |
| --- | --- | --- | --- |
| ≤ 5% | 48.394 | 61,6% | 26,4% |
| 5–15% | 16.152 | 96,9% | 47,1% |
| 15–25% | 9.123 | 97,3% | 75,4% |
| > 25% | 22.734 | 97,7% | 94,6% |

- `PDNAag` thiếu theo đúng biến phơi nhiễm FS10, nên làm outcome xác nhận sẽ có mẫu bị chọn lệch.
- `PDNAfl` thiếu ở FS ≤ 5% chỉ vì ngân hàng không có nợ đất NN (mẫu số bằng 0).
- `PDNAflt` (chia tổng dư nợ) có đủ mọi dòng và cùng mẫu số với C1, C2.

Đề xuất cho phiên chốt: C3 xác nhận = `PDNAflt`; `PDNAfl` và `PDNAag` để ở phụ lục.

## 4. Attrition [F]

Tỷ lệ ngân hàng còn số liệu sau h năm (trong số có số ở h = 0): h=1 95,9%, h=3 88,1%, h=6 77,2%. Ở h = 6 đã mất 23% mẫu (sáp nhập, đóng cửa, ra khỏi nhóm cộng đồng). Cần kiểm attrition theo nhiệt trước khi diễn giải C1 (mục 8.4 trong file công thức của Thịnh).

## 5. Nhiệt và hạn hán [F]

| Tương quan | Thô | Sau khử FE ngân hàng + division×năm |
| --- | --- | --- |
| Heat – Dr (D2+) | 0,415 | 0,377 |
| Heat – Dr3 (D3+) | 0,383 | 0,324 |
| Dr – mưa mùa vụ | −0,427 | −0,281 |
| Heat×FS10 – Dr×FS10 | – | 0,546 |

Tương quan Heat–Dr theo năm dao động từ 0,01 (2021) đến 0,83 (2011). Tương quan ở mức vừa, đủ để đưa cả hai vào cùng hồi quy. Nhưng tương quan giữa hai tương tác là 0,546, nên có Dr×FS10 hay không sẽ làm β2 đổi ý nghĩa ("nhiệt" hay "nhiệt khi giữ hạn hán cố định"). Đây là câu B3 trong bảng quyết định.

## 6. Hạn chế đã biết

- Dr dùng mùa 4–9 (khớp Heat), còn Brei et al. (2026) dùng 5–10.
- `cecl_first` dựa trên RCONJJ30 nên có thể bỏ sót ngân hàng áp dụng CECL sớm (xem từ điển biến).
- Quá hạn và charge-off của vay sản xuất NN không đầy đủ (mục 3).
