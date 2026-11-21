# Lớp đệm bảo hiểm: bồi thường RMA so với doanh thu trồng trọt mất đi (LÀM SAU, 19/11/2026)

**Nhãn:** phân tích làm sau, không nằm trong kế hoạch v3. Hồi quy bồi thường theo nhiệt (họ E1, không trọng số, cùng năm) đã có trong kế hoạch
vòng đầu (15/10/2026; `out/results/familyABE.csv`, `RESULTS_REPORT.md` mục 6 đã đánh dấu "độ lớn đáng ngờ"). Phần mới: đưa doanh thu và
bồi thường về cùng đơn vị, cùng mẫu, tính tỷ lệ bù và khoảng tin cậy.

**Đặc tả:** giống RQ-0 (nhiệt cấp hạt chuẩn hoá 232,7 ngày–độ; mưa z và z²; FE hạt; FE division × năm; Conley 1.000 km, trễ 2; `fit_lp` của
`scripts/_pap_est.py`, không sửa). Mọi kết cục chia cho doanh thu trồng trọt gốc 2001–05 (USD). Hiệp phương sai chéo giữa các kết cục tính
bằng Conley trên điểm số xếp chồng; SE riêng khớp `fit_lp` (assert). Tỷ lệ bù θ = phản ứng của khoản bù / −phản ứng của doanh thu; KTC theo delta.

**Vì sao lấy hai năm:** BEA ghi thu tiền mặt theo năm dương lịch, vụ thu hoạch cuối năm t bán một phần ở t+1; RMA ghi theo năm vụ.
Doanh thu năm t+1 giảm gần bằng năm t, trong khi tương quan nhiệt t và t+1 sau FE chỉ 0,028, nên phần giảm năm t+1 không do nhiệt kéo dài.

## Số chính (`results_real/ins_offset_cum.csv`; 40.914 hạt–năm, 2.827 hạt; t = 2006–2021)

| Kết cục (÷ doanh thu gốc) | Cân theo doanh thu gốc: tích luỹ t, t+1 [KTC 95%] | Tỷ lệ bù | Không trọng số: tỷ lệ bù |
|---|---|---|---|
| Doanh thu trồng trọt | −0,358 [−0,566; −0,151] (t: −0,165; t+1: −0,193) | — | (−0,405) |
| Bồi thường hạn + nhiệt + gió nóng (mã 11, 12, 62) | +0,148 [0,059; 0,237] (t: 0,140) | 41% [27%; 56%] | 48% [28%; 67%] |
| Bồi thường mọi nguyên nhân | +0,169 [0,078; 0,261] | 47% [30%; 65%] | 118% [−12%; 248%] |
| Trợ cấp chính phủ (BEA dòng 130) | −0,003 [−0,035; 0,030] | −1% [−10%; 8%] | 84% [−43%; 210%] |

Cùng năm (`results_real/ins_offset.csv`, 44.416 hạt–năm): bồi thường hạn–nhiệt bằng 1,04 lần doanh thu mất (cân) và 0,91 lần (không cân);
E1 = 0,2167 tái lập đúng. Con số "0,217 lớn hơn mức giảm 0,117" trong RESULTS_REPORT so hai đơn vị khác nhau: cùng đơn vị, doanh thu năm t
giảm 0,237 lần doanh thu gốc (không cân), vì doanh thu danh nghĩa 2006–22 bình quân gần gấp đôi gốc 2001–05.

## Đọc kết quả
- Sự thật: theo tổng đô la, bồi thường do hạn, nhiệt và gió nóng của vụ năm t bù khoảng 41% doanh thu trồng trọt mất trong hai năm;
  trợ cấp chính phủ không tăng (cận trên khoảng 8%).
- Suy luận: bảo hiểm là tấm đệm lớn nhưng không đủ; hơn nửa phần mất phải do nông hộ tự chịu (tiết kiệm, thu nhập ngoài nông nghiệp,
  giảm chi) hoặc do ngân hàng gia hạn; bài không quan sát được các kênh này.
- Hạn chế: cấp hạt, không phải cấp người vay; bồi thường chỉ đến nông hộ có bảo hiểm; bản không trọng số của "mọi nguyên nhân" và trợ cấp
  rất không chính xác (bị chi phối bởi hạt có doanh thu gốc nhỏ); chọn bản cân theo doanh thu là để đọc theo đô la, cả hai bản được báo.
