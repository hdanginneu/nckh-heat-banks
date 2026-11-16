# Bổ sung cho PAP_E41: gộp hai mẫu (16/11/2026)

Viết sau khi đã có kết quả của mẫu ngoài (commit f96f8f3). PAP_E41.md giữ nguyên, và hash của nó vẫn đúng như ở Phụ lục A. File này ghi thêm một phép tổng hợp, và trong bài phép này được ghi rõ là quyết định sau khi có kết quả.

- **Phép tính.** Gộp θ của mẫu chính (năm sốc 2007–2024) và θ của mẫu ngoài (1995–2006) theo trọng số nghịch đảo phương sai. Phương sai của mỗi θ là sd_adj², tức độ lệch chuẩn hoán vị đã nhân κ. Hai mẫu không chung năm sốc và dùng hai dãy hoán vị riêng, nên hai ước lượng được coi là độc lập. TOST dùng Δ của bài. Không chạy hồi quy mới. Code: `pooled_e41.py`.
- **Quy tắc.** Chỉ gộp các thống kê mà hiệu giữa hai mẫu có |z| < 1,96. Thống kê có |z| ≥ 1,96 (ở đây là C4) không gộp, và được báo là hai giai đoạn khác nhau.
- **Cách dùng trong bài.** Kết quả gộp chỉ dùng như phép tổng hợp mô tả ở mục 6.1. Phân loại chính thức của C1–C5 vẫn là phân loại của mẫu chính.
