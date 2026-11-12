# Từ điển biến panel_v3 (bước S2)

Tạo bởi `build_v3.py` (12/11/2026). File: `~/mnt/NCKH - NEU/_claude_pap/rq3_v3/out/panel_v3.parquet`, 107.502 dòng (ngân hàng × năm), 8.254 ngân hàng, t = 2006–2024, 228 cột. Không commit file parquet.

145 cột đầu là panel v2, trùng khớp tuyệt đối với `rq3_v2/out/panel_v2.parquet` (xem QA). Mã Call Report của từng biến gốc: `data/codebook_v3.csv`.

## Quy ước chung

- Mỗi dòng (b, t) là ngân hàng b ở năm cú sốc t. Outcome `X_h{h}` đo thay đổi từ cuối năm t−1 đến cuối năm t+h, h = 0..6.
- Đơn vị: điểm phần trăm (×100).
- Mẫu số là giá trị năm t−1 (`totloans_l1`, `farmland_l1` lấy từ bank_panel v1; `ag_loans_l1` tính mới). Mẫu số ≤ 0 cho NaN.
- Thiếu bất kỳ năm nào trong [t, t+h] thì outcome là NaN; cờ `alive_h{h}` = 1 nếu ngân hàng có đủ các năm đó.
- Số liệu gốc có đến năm 2025, nên cú sốc t cho được h đến 2025 − t. Cửa sổ cú sốc dùng để ước lượng do PAP v3 quyết định.

## Cột mới

| Cột | Định nghĩa | Vai trò dự kiến |
| --- | --- | --- |
| `NCOc_h{h}` | 100 · Σ_{k=0..h} (charge-off − thu hồi tổng)_{t+k} / tổng dư nợ_{t−1} | C1 |
| `ALLOW_h{h}` | 100 · (dự phòng_{t+h} − dự phòng_{t−1}) / tổng dư nợ_{t−1}; dự phòng = RCON3123 | C2 |
| `PDNAfl_h{h}` | 100 · Δ(quá hạn 30–89 + nonaccrual của nợ bảo đảm bằng đất NN) / dư nợ đất NN_{t−1} | C3, mẫu số là dư nợ NN |
| `PDNAflt_h{h}` | Như trên nhưng chia cho tổng dư nợ_{t−1} | C3, mẫu số là tổng dư nợ |
| `PDNAag_h{h}` | Như trên, cộng thêm vay sản xuất NN (RCON1594 + 1583), chia cho dư nợ NN_{t−1} | C3 bản của Thịnh; thiếu theo FarmShare |
| `LIQ_h{h}` | 100 · (liquidity_ratio_{t+h} − liquidity_ratio_{t−1}) | C4 (h=0 trùng `dLIQ_h0` của v2) |
| `AGL_h{h}` | 100 · (dư nợ NN_{t+h} − dư nợ NN_{t−1}) / dư nợ NN_{t−1}; dư nợ NN = RCON1420 + RCON1590 | C5, tăng trưởng % sổ NN |
| `AGLt_h{h}` | Như trên nhưng chia cho tổng dư nợ_{t−1} | C5, mẫu số là tổng dư nợ |
| `NCOfl_h{h}` | NCO cộng dồn của nợ bảo đảm bằng đất NN / dư nợ đất NN_{t−1} (trùng `C2_h` của v1) | Thăm dò |
| `NCOag_h{h}` | NCO cộng dồn của đất NN + vay sản xuất NN / dư nợ NN_{t−1} | Thăm dò; thiếu theo FarmShare |
| `alive_h{h}` | 1 nếu ngân hàng có số liệu ở mọi năm t..t+h | Kiểm attrition |
| `ag_loans_l1` | Dư nợ NN năm t−1 (> 0) | Mẫu số |
| `Dr` | Σ_c w_{b,t,c} · (số tuần D2+ có trọng số diện tích của hạt c, tháng 4–9 năm t); w = trọng số tiền gửi footprint t−1 như Heat | Hạn hán, biến kiểm soát |
| `Dr3` | Như `Dr` với D3+ | Hạn hán, biến phụ |
| `Dr_wcov` | Tỷ lệ trọng số tiền gửi có số liệu USDM (= 1 ở mọi dòng) | QA |
| `cecl_first` | Năm đầu tiên ngân hàng có số RCONJJ30 (dự phòng tài sản PCD) | Xác định áp dụng CECL; xem cảnh báo |
| `cecl_early` | 1 nếu `cecl_first` ≤ 2022 | Loại NH áp dụng CECL sớm khỏi C2 |

## Cảnh báo dữ liệu

1. **JJ30 không phải tổng dự phòng CECL [F].** Cột `allowance_cecl_kusd` của Phase 1 lấy từ RCONJJ30, theo MDRM là dự phòng cho tài sản PCD. Năm 2023 chỉ 59,5% ngân hàng có số, và 98,6% trong số đó bằng 0. Biến `cecl_adopt_year` của v2 và `cecl_first` ở đây vì vậy có thể bỏ sót ngân hàng áp dụng sớm [I]. Tổng dự phòng sau CECL vẫn là RCON3123.
2. **Vay sản xuất NN thiếu theo FarmShare [F].** Quá hạn, nonaccrual và charge-off của vay sản xuất NN chỉ có ở 26% dòng khi FS ≤ 5% nhưng 95% khi FS > 25%. Dùng các biến này làm outcome xác nhận sẽ cho mẫu bị chọn theo chính biến phơi nhiễm. Nghi do ngưỡng báo cáo theo tỷ trọng vay NN [?: chưa đọc hướng dẫn FFIEC].
3. **TDR chỉ có 2011–2023 [F]** và đổi định nghĩa từ 2023 (ASU 2022-02). Theo quy tắc S2 của khung, bỏ TDR khỏi v3.
4. **Ba dòng USDM sai thứ tự cộng dồn** (ngày 05/06/2018, hạt 08009 và 40025). Giữ nguyên số gốc, liệt kê ở `data_external/usdm/usdm_inconsistent_rows.csv`.
