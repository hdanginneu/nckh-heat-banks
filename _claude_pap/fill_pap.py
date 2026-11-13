"""Điền các ô còn trống trong PAP_v3.md (số từ results_sizetest, R = 99, 20 seed giả). Chạy từ thư mục _claude_pap."""
import re
p = "PAP_v3.md"; s = open(p, encoding="utf-8").read()
fill = {
    "«SD1»": "0,0247", "«F1»": "không (cần Δ ≥ 0,041)",
    "«SD2»": "0,0098", "«F2»": "không (cần Δ ≥ 0,016)",
    "«SD3»": "0,0023", "«F3»": "có",
    "«SD4»": "0,0337", "«F4»": "có",
    "«SD5»": "0,0734", "«F5»": "có",
    "«FEAS»": ("Với độ chính xác dự kiến, TOST **không thể đạt** cho C1 và C2 ngay cả khi tác động thật bằng 0. "
               "Hệ quả: dòng 1 của §8.2 (\"quiet thật\") thực tế không xảy ra được, và C1, C2 nhiều khả năng ra `?`. "
               "Đây là giới hạn của thiết kế, ghi trước khi chạy; ngưỡng không được nới. sd dự kiến lấy từ 20 bộ dữ liệu giả (outcome hoán vị), "
               "chưa nhân κ, nên sai số thật có thể lớn hơn."),
    "«ACCEPT»": """| Kiểm tra | Kết quả | Ngưỡng |
| --- | --- | --- |
| Đồng nhất thức §4.3 (C1, mẫu chung h = 0..6) | sai lệch 4,5e−14 | < 1e−8 |
| `V3Design.beta` = `fit_lp` (nhiệt hoán vị cố định) | sai lệch ≤ 1e−12 | < 1e−8 |
| Kích cỡ: tỷ lệ p_RI < 0,05 qua 5 θ × 20 seed giả, R = 99 | 3,0% (C5: 2/20, C3: 1/20, còn lại 0) | 2–9% |
| FWER của Westfall–Young, 20 seed giả, R = 99 | 0% (lượt R = 49: 5,0%) | ≲ 7% |
| Power khi gài tác động = MDE80, 20 lần, R = 49 | 55–85% theo θ | ≈ 80% |
| Chạy thật khi chưa có `hashes_frozen_v3.json` | dừng | phải dừng |

Power ở 4/5 θ thấp hơn mục tiêu. Tác động gài được ước lượng không chệch (θ̂/β gài = 0,93–1,15), nên nguyên nhân khả dĩ là R = 49 làm ngưỡng thô và 20 lần lặp có sai số khoảng 9 điểm % [I]. Hệ quả: MDE ở §6.2 có thể lạc quan. Code sau khi thêm κ được kiểm lại ở bước 1 của `RUN_v3.sh` trước khi đóng băng.""",
}
for k, v in fill.items():
    assert k in s, k
    s = s.replace(k, v)
assert "«" not in s, re.findall("«[^»]*»", s)
open(p, "w", encoding="utf-8").write(s)
print("đã điền", len(fill), "ô")
