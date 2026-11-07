# PAP v2.3 — Cung hay cầu: hạn mức chưa giải ngân và vai trò của bảo hiểm
Phiên bản 2026-11-07, viết TRƯỚC khi ghép dữ liệu FDIC (hạn mức chưa giải ngân, khoản vay nông nghiệp nhỏ) với nhiệt, và trước khi chạy tương tác nhiệt × FarmShare × bao phủ cho vay sản xuất NN, NCO, ΔNPL. Hdang yêu cầu chạy ngay; nhóm chưa duyệt.

## Dữ liệu mới
FDIC BankFind API (financials), tải 07/11/2026 (`data_external/fdic_api/`): UCOTHER (hạn mức chưa giải ngân "khác": gồm hạn mức thương mại và nông nghiệp; không gồm thẻ, BĐS thương mại, HELOC), UC (tổng), số khoản vay nông nghiệp nhỏ (LNAG1N < 100 nghìn USD, quý 2). Ghép theo CERT. Không có hạn mức riêng cho nông nghiệp → UCOTHER là proxy [hạn chế].

## Kiểm định xác nhận (họ F4, Westfall–Young)
- U1: ΔUCOTHER_t / tổng tài sản_{t−1} (điểm %), đặc tả V2, hệ số nhiệt × FS10. [H] Cầu giảm (rút ít hơn từ hạn mức) → β2 > 0; cung siết (cắt hạn mức) → β2 < 0.
- U2: Δ vay sản xuất NN / tổng tài sản_{t−1}, thêm nhiệt × FS10 × Cov (+ nhiệt × Cov, năm × Cov), hệ số ba chiều β3. [H] Trả nợ bằng bồi thường / cầu giảm → giảm mạnh hơn nơi bao phủ cao → β3 < 0; ngân hàng siết vì sợ lỗ → giảm mạnh hơn nơi bao phủ thấp → β3 > 0.
Suy luận: RI hoán vị năm thời tiết như PAP v2, R = 300, seed [20261108, khối]; "phát hiện" ⇔ p_WY < 0,05.
## Phụ (mô tả)
ΔUC tổng; NCO và ΔNPL × Cov (β3; [H] tổn thất chỉ xuất hiện nơi bao phủ thấp → β3 < 0 với NCO/NPL); Δ log số khoản vay NN < 100 nghìn (quý 2 năm t+1 so với quý 2 năm t); placebo nhiệt t+1 cho U1 và U2.
## Cây diễn giải
- U1 > 0 và/hoặc U2 < 0 (phát hiện): bằng chứng gián tiếp ủng hộ cầu/trả nợ.
- U1 < 0 và/hoặc U2 > 0: ủng hộ có thành phần cung.
- Trái chiều: báo cả hai, không chọn.
- Không phát hiện: không phân biệt được bằng hai phép thử này.
- Placebo p < 0,05: hạ thành gợi ý.
