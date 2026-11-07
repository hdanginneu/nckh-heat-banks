# DESIGN_B_DRAFT — thiết kế liều–đáp (dose-response) theo FarmShare liên tục (NHÁP, chưa đóng băng; sẽ thành PAP v2)
Trạng thái: bản nháp 2026-11-05. Chưa ước lượng hệ số nhiệt thật cho outcome RQ3. Mọi lựa chọn dưới đây phải chốt trước khi chạy.

## Đặc tả chính
y_{b,t+h} = β1·Heat_{b,t} + β2·Heat_{b,t}×FS10_b + γ'(Heat×Z_b) + δ'X_{b,t-1} + bank FE + division×year FE + e
- FS10 = FarmShare_pre × 10 (=+10 điểm %), trung bình 3 quan sát đầu của ngân hàng (tiền xác định, bất biến theo thời gian → hiệu ứng chính hấp thụ bởi bank FE).
- Heat = GDD mùa vụ trọng số tiền gửi t−1 / SD (như PAP v1). Z_b = {log tài sản, tỷ lệ thanh khoản, vay/tài sản, vĩ độ trụ sở} (kiểm soát FS làm proxy cho quy mô/vùng).
- Hệ số quan tâm: β2 (độ dốc theo liều). Hiệu ứng ở FS = 0 (ngân hàng phi nông nghiệp) = β1: đóng vai placebo (kỳ vọng ≈ 0 với outcome nông nghiệp).
- SE: Conley 1.000 km (chính), cụm-bang (kiểm tra). Romano–Wolf cho họ outcome.

## Outcome chính của RQ3 (đăng ký trước)
1. Provision/dư nợ t−1 có điều kiện (control NCO, ΔNPL, allowance trễ) — h0.
2. Δ allowance (allowance_legacy_kusd)/dư nợ t−1 có điều kiện — h0.
3. Δ tỷ lệ thanh khoản — h0.
4. (Lặp lại H4) Δ tỷ trọng vay sản xuất — dùng để tách phần đã thấy ở PAP v1.
Chỉ cho phép h0 làm chính; h1 là phụ.

## Bảng bảo vệ luận điểm (luận điểm → mối đe dọa → cách bảo vệ → kiểm định)
| Luận điểm | Đe dọa | Bảo vệ | Kiểm định |
|---|---|---|---|
| Nhiệt ngoại sinh theo thời điểm | Tương quan không gian; trọng số tiền gửi đổi theo thời gian | Bank FE + div×năm FE + mưa; Conley; trọng số t−1 | Placebo nhiệt năm sau (lead); SE cụm-bang |
| FarmShare đo "mức tiếp xúc nông nghiệp" | FS proxy cho quy mô/vùng/thanh khoản (tương quan −0,37 với log tài sản; +0,23 vĩ độ; +0,22 thanh khoản) | Heat×Z; không dùng ngưỡng; liều phi tham số | Dốc theo bin/spline; bỏ từng division; dốc giữ nguyên khi thêm Heat×Z |
| Không có ngưỡng tùy ý | Mốc 25% không bảo vệ được | FS liên tục; bin chỉ mô tả | Độ nhạy: nhóm 15/25/35 (đã có trong panel) |
| Phản ứng là "trước khi lỗ" | Provision phản ánh cơ học NPL/NCO | Điều kiện hóa trên NCO, ΔNPL, allowance trễ (khai báo bad-control; báo cả bản không control) | So sánh hai bản; hệ số trên NCO/NPL |
| Allowance liên tục qua CECL | allowance_to_loans sai với CECL adopters | Dùng allowance_legacy_kusd; chính 2007–2022; mở rộng 2023–24 với dummy năm áp dụng CECL | MDE đã tính (≈ không đổi); đối chiếu MDRM |
| Null có nghĩa | MDE ≠ biên tương đương; SESOI quá rộng (bài học H3) | Đặt SESOI từ lập luận kinh tế TRƯỚC khi chạy (đề xuất: ±5% allowance stock cho +1 SD nhiệt ở FS tại 25%) | TOST + CI pass-through; báo MDE |
| Không data-mining | Nhiều outcome, nhiều đặc tả | PAP v2 đóng băng bằng freeze.py; Romano–Wolf; outcome chính chỉ 3 | verify hash; ghi mọi đặc tả vào specs |
| Phân biệt xác nhận và thăm dò | Quyết định sau khi thấy kết quả (pass-through chính, SE cụm cho H4) | Gắn nhãn thăm dò ở PAP v1; chỉ outcome mới (1–3) là xác nhận | Addendum + DECISIONS_LOG |
| H4 vốn mong manh (1 division, nửa A không có) | Mỏ neo yếu | Không dùng H4 làm mỏ neo; báo kèm độ nhạy theo division | Bỏ từng division; chia nửa A/B |

## Hạn chế đã biết (phải nêu trong bài)
- Heat là GDD mùa vụ (thước đo nông nghiệp); với ngân hàng phi nông nghiệp phản ánh yếu hơn mức tiếp xúc nhiệt thật → dốc theo liều là bằng chứng gián tiếp.
- Tmax-only (PRISM); không Tmin.
- FS dựa trên danh mục cho vay, không phải phơi nhiễm bảo hiểm (chưa có dữ liệu bảo hiểm theo ngân hàng).
- SESOI cho RQ3 là đề xuất, cần nhóm chốt.

## Chẩn đoán đã chạy (xem GB_*.csv)
- FarmShare_pre (8.254 ngân hàng): median 2,9%; p75 19%; p90 42%; <5%: 4.612; 5–15%: 1.257; 15–25%: 699; 25–35%: 550; >35%: 1.124.
- MDE80 cho β2 (+1 SD nhiệt × +10 điểm % FS), toàn mẫu: provision|cond 0,036 sd; dALLOW|cond 0,038 sd; ΔLIQ 0,043 sd; tăng trưởng tín dụng 0,070 sd; D1 0,106 sd.
