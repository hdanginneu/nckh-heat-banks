# PAP v3 — Nhiệt cực đoan và ngân hàng cộng đồng nông nghiệp Mỹ: tổn thất, thời điểm ghi nhận, bảng cân đối

Phiên bản 12/11/2026. Viết **trước** khi ước lượng bất kỳ hệ số nào của C1–C5 với nhiệt thật trên outcome thật. Đóng băng bằng `freeze_v3.py` (hash ở `hashes_frozen_v3.json`). Sau khi đóng băng không sửa file này; mọi sai lệch ghi ở `POST_FREEZE_ADDENDUM_v3.md` với hash riêng.

Nhãn: **[F]** sự thật đã kiểm (có file hoặc số nguồn), **[I]** suy luận, **[A]** giả định, **[Q]** quy ước do người soạn chọn, **[?]** chưa kiểm.

Mọi hệ số là **tương quan có điều kiện** trong thiết kế "nhiệt theo năm như ngẫu nhiên". Không dùng ngôn ngữ nhân quả cho FarmShare.

Nguồn đặc tả: `PAP_v3_formulas.md` (Thịnh, 09/11) cho công thức; `PAP_v3_SESOI.md` (Mai, 09/11) cho số neo và giả thuyết; `RESEARCH_FRAMEWORK_FINAL_v3` (07/11) cho câu hỏi và họ kiểm định. Chỗ nào bản này khác các tài liệu đó được liệt kê ở §11.

---

## 0. Những gì đã thấy trước khi viết bản này

Người đọc cần biết phần nào của v3 là mới, phần nào đã lộ từ v1/v2.

**Đã thấy ở v1/v2 [F, `RESULTS_RQ3_v2.md`, `RESULTS_REPORT.md`]:**
- ΔLIQ h=0 (C4): +0,178, p_RI 0,005, mẫu 2007–2022. Bỏ vùng West South Central còn 0,096 (không có ý nghĩa). ΔLIQ h=1: +0,051 (p 0,41).
- Δallowance h=0 không điều kiện: −0,0059; Δallowance h=1 (t−1→t+1): −0,0137 (p_RI 0,008). Hai số này chính là hai thành phần "sớm" của C2. Hệ quả [I]: nếu phần "muộn" bằng 0 thì θ_C2 kỳ vọng dương khoảng +0,010 chỉ vì phần sớm âm. Quy tắc §8.2 xử lý việc này.
- Δ vay sản xuất NN/dư nợ h=0 (D1): −0,251 (p < 0,001). Đây là một phần của C5 tại h=0.
- NCO h=0 với nhiệt×(trồng trọt, chăn nuôi) ở v2.4: không phát hiện.
- v1 (đặc tả khác: nhiệt mức trong mẫu FarmShare ≥ 25%): NCO và nợ xấu (≥ 90 ngày + nonaccrual) của nợ đất NN đến h=3 đạt tương đương với SESOI rộng; nợ đất NN quá hạn 30–89 ngày là outcome phụ.

**Đã thấy khi chuẩn bị v3 [F, `rq3_v3/QA_REPORT_v3.md`]:** thống kê mô tả không điều kiện theo nhiệt (số quan sát, trung bình, SD, tỷ lệ thiếu, attrition), tương quan nhiệt–hạn hán, và các lượt chạy trên **dữ liệu giả** (outcome hoán vị trong từng năm). Từ dữ liệu giả đã biết sd hoán vị gần đúng của từng θ, tức là đã biết C1 và C2 khó đạt tương đương (§6.2).

**Chưa thấy:** mọi hồi quy của outcome v3 trên nhiệt thật, gồm NCO tổng cộng dồn h ≥ 1, allowance h ≥ 2, quá hạn 30–89 + nonaccrual của nợ đất NN trên tổng dư nợ, ΔLIQ h ≥ 2, dư nợ NN h ≥ 1 theo đặc tả V2, và mọi kết quả có dữ liệu 2023–2025.

---

## 1. Câu hỏi nghiên cứu

- **RQ-A (tổn thất):** nhiệt cực đoan trong mùa vụ có đi kèm tổn thất tín dụng cộng dồn cao hơn ở ngân hàng có tỷ trọng nông nghiệp cao, tính đến 6 năm sau, không?
- **RQ-B (thời điểm):** nếu có căng thẳng tín dụng, nó lộ ra sớm (quá hạn, ngừng dồn tích ở t..t+1) hay muộn (dự phòng dồn về t+3..t+6)?
- **RQ-C (bảng cân đối):** thanh khoản và dư nợ nông nghiệp thay đổi thế nào?

Giả thuyết kinh tế H1–H4 và ma trận dự đoán: `PAP_v3_SESOI.md` mục 2. Mọi kiểm định hai phía, vì H1–H4 cho dấu khác nhau ở từng outcome.

---

## 2. Dữ liệu

- `panel_v3.parquet` dựng bởi `rq3_v3/build_v3.py`: 107.502 dòng ngân hàng × năm, 8.254 ngân hàng cộng đồng (48 bang + DC), năm cú sốc t = 2006–2024 [F]. 145 cột của panel v2 được giữ nguyên, khớp tuyệt đối với `panel_v2.parquet` [F, `qa/qa_summary.json`].
- Outcome lấy từ Call Report 2005–2025 (Phase 1 và file FFIEC nông nghiệp). Mã từng biến: `rq3_v3/data/codebook_v3.csv`, tên mục lấy từ MDRM [F].
- Nhiệt: $H_{b,t}=\sum_c w_{b,t,c}\,\mathrm{GDD}_{c,t}/\sigma_{GDD}$, GDD trên 29°C tháng 4–9, trọng số tiền gửi theo hạt của năm t−1, $\sigma_{GDD}$ giữ nguyên hằng số v1 (`bank_scales.json`) [F].
- Hạn hán (chỉ dùng ở R1, §9.1): $Dr_{b,t}=\sum_c w_{b,t,c}\cdot$ (số tuần USDM ≥ D2 tháng 4–9 năm t của hạt c, mỗi tuần nhân tỷ lệ diện tích hạt ở D2+). Cùng trọng số với nhiệt [F: dựng lại `heat` từ cùng ma trận trọng số, sai khác 1,8e−15].

---

## 3. Outcome, thống kê xác nhận, mẫu

### 3.1 Outcome
Mỗi dòng (b, t). $\Delta^h y$ đo thay đổi từ cuối năm t−1 đến cuối năm t+h, đơn vị điểm %. Mẫu số luôn là tổng dư nợ năm t−1 ($L_{t-1}$, > 0), trừ LIQ. Thiếu bất kỳ năm nào trong [t, t+h] thì $\Delta^h y$ là NaN; không điền 0.

| C | Cột | Công thức $\Delta^h y_{b,t}$ |
| --- | --- | --- |
| C1 | `NCOc_h` | $100\sum_{k=0}^{h}(\mathrm{CO}-\mathrm{REC})_{b,t+k}/L_{b,t-1}$; CO, REC = charge-off và thu hồi **tổng** (RIAD4635, RIAD4605) |
| C2 | `ALLOW_h` | $100\,(A_{b,t+h}-A_{b,t-1})/L_{b,t-1}$; A = RCON3123, **không điều kiện hoá** |
| C3 | `PDNAflt_h` | $100\,(P_{b,t+h}-P_{b,t-1})/L_{b,t-1}$; P = nợ bảo đảm bằng đất NN quá hạn 30–89 ngày + nonaccrual (RCON3493 + RCON3495) |
| C4 | `LIQ_h` | $100\,(\mathrm{LIQ}_{b,t+h}-\mathrm{LIQ}_{b,t-1})$; LIQ = tài sản thanh khoản / tổng tài sản (định nghĩa v2) |
| C5 | `AGLt_h` | $100\,(AG_{b,t+h}-AG_{b,t-1})/L_{b,t-1}$; AG = nợ bảo đảm bằng đất NN + vay sản xuất NN (RCON1420 + RCON1590) |

Lý do chọn [I]:
- C1 dùng NCO tổng để so được với Lu & Nikolaev và vì NCO nông nghiệp không đầy đủ (xem C3).
- C3 không gồm vay sản xuất NN. Quá hạn của vay sản xuất NN chỉ có số ở 4% dòng khi vay sản xuất NN < 3% dư nợ nhưng 99% khi > 7% (ngân hàng dưới 300 triệu USD) [F, dữ liệu nhóm]; phù hợp với ngưỡng báo cáo của Call Report (≥ 300 triệu USD tài sản, hoặc vay sản xuất NN > 5% dư nợ) [?: chưa mở hướng dẫn FFIEC]. Mẫu có số vì vậy bị chọn theo chính biến phơi nhiễm. Bản có vay sản xuất NN chạy ở R3.
- C5 chia cho tổng dư nợ, không chia cho dư nợ NN, để tránh mẫu số rất nhỏ ở ngân hàng ít cho vay NN và để cùng thang với C1–C3. `AGLt_h` trùng D1 + D2 của v1 [F, sai khác 6e−14].
- TDR không dùng: chỉ có số 2011–2023 và đổi định nghĩa từ 2023 [F, codebook].

### 3.2 Thống kê xác nhận
$\beta_2^{k,h}$ là hệ số của $H\times FS10$ trong hồi quy §4 cho outcome k, horizon h.

| C | $\theta_C$ | Ý nghĩa |
| --- | --- | --- |
| C1 | $\beta_2^{NCO,6}$ | NCO cộng dồn t..t+6 |
| C2 | $\frac14\sum_{h=3}^{6}\beta_2^{A,h}-\frac12\sum_{h=0}^{1}\beta_2^{A,h}$ | dự phòng "muộn" trừ "sớm" |
| C3 | $\frac12(\beta_2^{P,0}+\beta_2^{P,1})$ | căng thẳng sớm |
| C4 | $\beta_2^{LIQ,0}$ | thanh khoản năm cú sốc (tái lập v2, thêm 2023–2024) |
| C5 | $\beta_2^{AG,2}$ | dư nợ NN t−1→t+2 |

Họ xác nhận gồm đúng năm thống kê này. Không thêm sau khi đóng băng.

### 3.3 Mẫu
$\mathcal S_{k,h}$ gồm (b, t) thoả: (i) $2007\le t\le\min(2024,\ T-h)$ với T = 2025 (C1, C3, C4, C5) hoặc T = 2022 (C2); (ii) $\Delta^h y$ không NaN; (iii) đủ nhiệt, mưa, controls, FS10, Z; (iv) riêng C2: bỏ (b, t) có năm đầu báo RCONJJ30 nằm trong [t, t+h]. Winsorize y ở 1%/99% trong mẫu, riêng từng h.

θ ghép nhiều h (C2, C3) dùng **mẫu chung** $\bigcap_h\mathcal S_{k,h}$ cho mọi h của nó.

| θ | Cú sốc t | Số năm sốc | n xấp xỉ [F, QA] |
| --- | --- | --- | --- |
| C1 | 2007–2019 | 13 | 59.200 |
| C2 | 2007–2016 | 10 | 47.200 |
| C3 | 2007–2024 | 18 | 93.600 |
| C4 | 2007–2024 | 18 | 97.500 |
| C5 | 2007–2023 | 17 | 86.100 |

Số chính xác ghi ở `results_real/designs.csv` khi chạy.

---

## 4. Đặc tả

### 4.1 Phương trình (đặc tả V2, không đổi)
Với mỗi (k, h), một hồi quy riêng:

$$\Delta^h y^{k}_{b,t}=\beta_2^{k,h}(H_{b,t}FS10_b)+\beta_1^{k,h}H_{b,t}+\sum_{z}\gamma_z^{k,h}(H_{b,t}z_b)+\delta'X_{b,t}+\alpha_b+\tau_{d(b),t}+\sum_{s\ne s_0}1[t=s]\Big(\phi_sFS10_b+\sum_z\psi_{z,s}z_b\Big)+\varepsilon_{b,t}$$

- $FS10_b$ = 10 × FarmShare_pre (trung bình 3 quan sát đầu); $z_b\in\{$`z_size`, `z_liq`, `z_lat`$\}$.
- $X_{b,t}$: mưa năm t (`ppt_season_z`, `ppt_z2`), controls ngân hàng năm t−1 (log tài sản, thanh khoản, dư nợ/tài sản).
- $\alpha_b$: FE ngân hàng; $\tau_{d,t}$: FE division × năm.
- Code: `_v3_spec.fit` gọi `fit_lp` của v1 với cùng thứ tự cột như `_v2_spec.fit`.

**Hạn hán không nằm trong đặc tả xác nhận.** Lý do: khung v3 mục 3.2 quy định giữ đặc tả V2; C4 chỉ là phép tái lập nếu đặc tả không đổi; và hạn hán một phần là hệ quả của nhiệt, nên kiểm soát nó sẽ loại bớt tác động tổng của một mùa nóng [I]. Câu hỏi "nhiệt hay hạn hán" được trả lời ở R1 (§9.1).

### 4.2 Estimand
$\beta_2^{k,h}$: chênh lệch về thay đổi của y từ t−1 đến t+h, khi nhiệt năm t cao hơn 1 SD, giữa hai ngân hàng chênh nhau 10 điểm % FarmShare_pre, trong cùng division × năm, sau khi giữ các gradient theo năm của FarmShare, quy mô, thanh khoản, vĩ độ. Quy về ngân hàng FS = 25% so với FS = 0: nhân 2,5.

Vì nhiệt tự tương quan giữa các năm [F: 0,24 giữa t và t+1 sau FE], $\beta_2^{k,h}$ với h ≥ 1 là phản ứng với một năm nóng **kể cả phần nóng kéo theo sau đó**, không phải phản ứng với một cú sốc cô lập [I].

### 4.3 Đồng nhất thức kiểm code
Trên cùng mẫu, không winsorize: $\hat\beta^{k,h}_{cum}=\sum_{j\le h}\hat b^{k,j}_{flow}$. Kiểm bằng `run_v3.py check` trên nhiệt hoán vị cố định.

### 4.4 SE mô tả
Conley (1.000 km, Bartlett lag = h + 2) và cụm theo bang. Chỉ để tham khảo; không dùng để quyết định.

---

## 5. Suy luận: randomization inference

### 5.1 Hoán vị
R = 1000 hoán vị $\pi_r$ của các năm thời tiết 2006–2024, không điểm cố định, áp cho mọi ngân hàng: $H^*_{b,t}=\sum_c w_{b,t,c}\mathrm{GDD}_{c,\pi_r(t)}/\sigma_{GDD}$. Seed: `default_rng([20261115, khối])`, 10 hoán vị mỗi khối. **Cùng một dãy $\pi_r$** cho mọi outcome, mọi h, mọi phân tích phụ. Trọng số, outcome, mưa, controls, FE giữ nguyên.

### 5.2 p-value
H0 sắc: nhiệt không ảnh hưởng y ở bất kỳ ngân hàng–năm nào. Giả định [A]: các năm thời tiết 2006–2024 trao đổi được.
$$p^{RI}_C=\frac{1+\#\{r:|\theta^*_{C,r}|\ge|\hat\theta_C|\}}{1+R}$$

### 5.3 Westfall–Young
Step-down max-|t| trên họ C1–C5, chuẩn hoá bằng sd hoán vị của từng θ, dùng chung $\pi_r$ (thuật toán như `cmd_collect` của v2). **Phát hiện ⇔ $p^{WY}_C<0{,}05$.**

### 5.4 Kiểm nhất quán
Bộ ước lượng nhanh (`V3Design.beta`) phải trùng `fit_lp` (< 1e−8). Trước đóng băng kiểm trên nhiệt hoán vị cố định; khi chạy thật, `collect` so β nhanh với β của `fit_lp` cho mọi thiết kế có tính SE.

---

## 6. SESOI và kiểm định tương đương

### 6.1 Quy tắc
Phép so sánh tham chiếu: ngân hàng FS = 25% so với FS = 0, nhiệt +1 SD (quy ước PAP v2), nên $\Delta_C=\delta_y/2{,}5$.
- C1–C3: $\delta_y=r_C\times\bar y_C$. $r_C$ là tác động tương đối trong bài gốc (số in trong bài, do Mai đối chiếu trang). $\bar y_C$ là trung bình không điều kiện theo nhiệt của nhóm ngân hàng FarmShare_pre trong (15%, 35%] [Q].
- C4, C5: $\delta_y=0{,}10\times SD(y)$ trong mẫu ước lượng. Đây là quy ước của PAP v2 cho ΔLIQ, chốt trước khi có kết quả v2; áp thêm cho C5 [Q]. Không có neo tài liệu cho hai outcome này.

### 6.2 Giá trị (file `rq3_v3/sesoi_v3.json`, sinh bởi `sesoi_v3.py`)

| C | Neo | r chính (phụ) | $\bar y$ hoặc SD | $\Delta_C$ chính (phụ) | sd dự kiến (dữ liệu giả) | Khả năng đạt tương đương |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | Lu & Nikolaev, Bảng 2A: lỗ muộn năm 5–6 cộng lại = 12,6% NCO bình quân một năm | 0,126 (0,063) | NCO năm 0,255% | 0,0129 (0,0064) | 0,0247 | không (cần Δ ≥ 0,041) |
| C2 | Lu & Nikolaev, Bảng 2A cột 4: ALL muộn trừ sớm = 2,0% ALL bình quân | 0,020 (0,022) | ALL 1,499% | 0,0120 (0,0132) | 0,0098 | không (cần Δ ≥ 0,016) |
| C3 | Özsoy et al., Bảng 2 cột 4: cận dưới một phía 5% = 9,2% NPL bình quân (ước lượng điểm 25%) | 0,092 (0,25) | 0,196% | 0,0072 (0,0196) | 0,0023 | có |
| C4 | quy ước v2 | – | SD 5,33 | 0,213 | 0,0337 | có |
| C5 | quy ước v2 mở rộng | – | SD 7,69 | 0,308 | 0,0734 | có |

TOST chỉ có thể đạt khi $\Delta_C>1{,}645\times sd$. Với độ chính xác dự kiến, TOST **không thể đạt** cho C1 và C2 ngay cả khi tác động thật bằng 0. Hệ quả: dòng 1 của §8.2 ("quiet thật") thực tế không xảy ra được, và C1, C2 nhiều khả năng ra `?`. Đây là giới hạn của thiết kế, ghi trước khi chạy; ngưỡng không được nới. sd dự kiến lấy từ 20 bộ dữ liệu giả (outcome hoán vị), chưa nhân κ, nên sai số thật có thể lớn hơn.

Ghi chú trung thực:
- $\Delta_{C1}$ so tổn thất cộng dồn 7 năm với 12,6% của **một** năm NCO bình quân, tức khoảng 1,8% tổn thất bình quân của cả 7 năm. Ngưỡng này lấy theo phương án Mai ưu tiên và chặt hơn độ chính xác mà thiết kế đạt được.
- Các ngưỡng không được nới theo công suất. Khi một θ ra "?", bài báo cáo khoảng tin cậy và mức tác động nhỏ nhất loại trừ được, tính theo % của $\bar y$.
- Kết quả v2 của C4 (+0,178) nhỏ hơn $\Delta_{C4}$ (0,213). Một kết quả "+" ở C4 vì vậy vẫn được viết là "có ý nghĩa thống kê, độ lớn dưới ngưỡng đáng kể".

### 6.3 TOST và hệ số đòn bẩy κ
$CI^{90}_C=\hat\theta_C\pm1{,}645\cdot sd^{adj}_C$, với $sd^{adj}_C=sd_r(\theta^*_{C,r})\times\max(1,\kappa_C)$. TOST đạt ⇔ $CI^{90}_C\subset(-\Delta_C,\Delta_C)$.

$\kappa_C=\sqrt{\mathrm{median}_r(RSS^*_{x,r})/RSS_x}$, trong đó $RSS_x$ là phần biến thiên của cột $H\times FS10$ còn lại sau khi khử FE, controls và các cột nhiệt khác. Lý do [I]: sd hoán vị đo độ phân tán của $\hat\theta$ khi nhiệt là một hoán vị điển hình; nếu nhiệt thật có ít biến thiên hữu ích hơn (κ > 1) thì sd hoán vị thấp hơn sai số thật của $\hat\theta$ và TOST sẽ quá dễ đạt. κ chỉ dùng ma trận thiết kế, không dùng outcome. Giả định [A]: sai số gần iid cho bước hiệu chỉnh này. $p^{RI}$ và $p^{WY}$ **không** chỉnh theo κ.

Báo thêm bản phi tham số: $[\hat\theta-\kappa q_{0,95}(\theta^*),\ \hat\theta-\kappa q_{0,05}(\theta^*)]$. Nếu hai bản cho kết luận khác nhau, ghi "nhạy với giả định phân phối".

### 6.4 Phân loại mỗi θ
- `+` / `−`: $p^{WY}<0{,}05$ và dấu của $\hat\theta$.
- `0`: không phát hiện và TOST đạt với Δ chính.
- `?`: không phát hiện và TOST không đạt.

Kết quả với Δ phụ được báo kèm, không đổi phân loại.

---

## 7. MDE

- 7.1 Dạng chuẩn: $MDE_{80}=2{,}8016\times sd^{adj}$.
- 7.2 Dạng RI: ngưỡng $c_{0,95}$ từ các hoán vị lẻ, power trên các hoán vị chẵn, lưới bước 0,01 sd; nhân max(1, κ).

Báo MDE cho từng θ và từng (k, h), kèm tỷ lệ MDE/Δ và MDE/$\bar y$.

---

## 8. Quy tắc diễn giải (viết trước)

Ký hiệu $s_1,s_2,s_3$ là phân loại của C1, C2, C3 theo §6.4.

### 8.1 RQ-A
- $s_1=+$: nhiệt đi kèm tổn thất cộng dồn cao hơn ở ngân hàng nông nghiệp. $s_1=-$: thấp hơn.
- $s_1=0$: tổn thất cộng dồn tương đương 0 trong ngưỡng $\Delta_{C1}$.
- $s_1=?$: không kết luận được. Báo $CI^{90}$ và câu "loại trừ được tác động lớn hơn X% tổn thất bình quân 7 năm". **Không viết "quiet" hay "không có tổn thất".**

### 8.2 RQ-B
Thành phần mô tả của C2 (cùng mẫu, cùng π): E = trung bình $\beta_2^{A,0},\beta_2^{A,1}$; L = trung bình $\beta_2^{A,3..6}$.

Xét theo thứ tự, dừng ở dòng đầu tiên thoả:

| # | Kết luận | Điều kiện |
| --- | --- | --- |
| 1 | **Quiet thật**: không thấy căng thẳng sớm, tổn thất cộng dồn hay dự phòng muộn vượt ngưỡng | $s_1=0,\ s_2=0,\ s_3=0$ |
| 2 | **Căng thẳng sớm, ghi nhận muộn** (phù hợp với forbearance theo nghĩa của Lu & Nikolaev) | $s_3=+,\ s_2=+$, và L > 0 với $p^{RI}_L<0{,}10$ |
| 3 | **Ghi nhận trễ không kèm căng thẳng sớm** (kiểu Lu & Nikolaev) | $s_2=+$, L > 0 với $p^{RI}_L<0{,}10$, $s_3\in\{0,-\}$ |
| 4 | **Dự phòng giảm sớm rồi hồi về**, không phải ghi nhận tổn thất muộn | $s_2=+$ nhưng không thoả điều kiện về L, và E < 0 với $p^{RI}_E<0{,}10$ |
| 5 | **Căng thẳng và tổn thất, không phát hiện dự phòng dồn về sau** | $s_3=+,\ s_1=+,\ s_2\ne+$ |
| 6 | **Không kết luận được về thời điểm** | mọi trường hợp còn lại |

- Dòng 4 có vì phần sớm của C2 đã thấy âm ở v2 (§0).
- Nhãn dòng 2 và 3 theo khung v3 và tài liệu của Mai. Bản nháp của Thịnh gán hai nhãn này ngược lại; ở đây "forbearance" hiểu theo Lu & Nikolaev: ngân hàng để khoản vay quá hạn mà chưa ghi nhận tổn thất [I].
- "Forbearance" chỉ được viết là "phù hợp với". Không có dữ liệu cấp khoản vay.
- Chỉ $s_1,s_2,s_3$ và điều kiện ghi trong bảng quyết định dòng; mọi chỉ báo khác chỉ để minh hoạ.
- Dòng 1 chỉ xảy ra được nếu TOST của cả ba θ khả thi (§6.2).

### 8.3 RQ-C
- C4: `+` → "thanh khoản tăng trong năm nóng, tái lập kết quả v2". Kèm quy tắc ổn định R2 (§9.2).
- C5: `−` → dư nợ NN giảm so với tổng dư nợ; `+` → tăng. C4 `+` và C5 `−` cùng lúc phù hợp với H4 (cầu vay giảm) [I], không chứng minh cơ chế.

### 8.4 Cờ nhận dạng
- **Placebo:** outcome trước cú sốc, m ∈ {2, 3}: $y_{t-m}-y_{t-1}$ (tồn) hoặc tổng NCO các năm t−m..t−2 (dòng), cùng vế phải. Nếu $p^{RI}<0{,}025$ ở m = 2 hoặc m = 3 (Bonferroni trên hai phép thử) thì mọi kết luận về C đó hạ xuống "gợi ý".
- **Attrition:** $E^h_{b,t}$ = 1 nếu ngân hàng có số ở t nhưng thiếu ở một năm trong t+1..t+h. Nếu $\beta_2$ của $E^h$ có $p^{RI}<0{,}05$ tại h của θ (h = 6 cho C1, C2; h = 1 cho C3; h = 2 cho C5) thì ghi rõ θ đó có thể lệch do chọn mẫu sống sót. Không ước lượng cận Lee.

### 8.5 Câu kết luận tối đa được phép
- Nếu dòng 1: "pre-registered evidence that extreme heat does not generate credit losses, early distress or delayed provisioning above the stated thresholds over a six-year horizon".
- Nếu C1 `?`: chỉ được viết về các tác động đã loại trừ ("we rule out cumulative losses above X"), không viết "no losses".
- Mọi kết quả khác viết theo đúng dòng của §8.2.

---

## 9. Phân tích phụ đã đăng ký (không thuộc họ xác nhận)

Tất cả dùng cùng dãy $\pi_r$, báo $\hat\theta$, sd, $p^{RI}$, không hiệu chỉnh đa kiểm định, và được dán nhãn "độ vững" hoặc "mô tả".

### 9.1 R1 — Nhiệt hay hạn hán (`SPEC=dr`)
Thêm $Dr$, $Dr\times FS10$, $Dr\times z$ vào vế phải, cho cả năm θ. Trong RI, nhiệt và hạn hán được hoán vị **cùng nhau** theo cùng $\pi_r$.

Lý do hoán vị chung [I]: sau FE, tương quan giữa $H\times FS10$ và $Dr\times FS10$ là 0,55 [F]. Nếu giữ hạn hán cố định, nhiệt hoán vị không còn tương quan với hạn hán, nên phân phối hoán vị hẹp hơn sai số thật của $\hat\beta_2$. Hoán vị chung giữ nguyên cấu trúc tương quan; nếu hạn hán có tác động riêng thì phép thử thiên về bảo thủ.

Quy tắc: với θ có phân loại `+` hoặc `−`, nếu $\hat\theta^{dr}$ cùng dấu, $|\hat\theta^{dr}|\ge0{,}5|\hat\theta|$ và $p^{RI,dr}<0{,}10$ thì viết "nhiệt, sau khi tính đến hạn hán". Nếu không thì chỉ được viết "mùa nóng–khô". Với θ `0` hoặc `?`: chỉ báo số.

### 9.2 R2 — Độ ổn định của C4
Bỏ lần lượt từng division (9) và từng năm cú sốc (18). C4 "ổn định" nếu: cùng dấu ở ≥ 7/9 division và ở cả 18 năm, và độ lớn trong 0,5–2 lần ở ≥ 7/9 division và ≥ 16/18 năm (tiêu chí division lấy từ PAP v2). Nếu không: viết "không ổn định theo vùng hoặc năm" và hạ C4 xuống phát hiện phụ. Đã biết từ v2: bỏ West South Central làm hệ số giảm còn 0,54 lần.

### 9.3 R3 — Định nghĩa khác của C3
`C3_ag`: thêm vay sản xuất NN, mẫu số dư nợ NN (chỉ ngân hàng có báo cáo). `C3_fl`: mẫu số dư nợ đất NN.

### 9.4 R4 — Định nghĩa khác của C1, C5
`C1_fl`: NCO của nợ đất NN trên dư nợ đất NN. `C5_ag`: tăng trưởng % của sổ nông nghiệp.

### 9.5 Mô tả
- LP h = 0..6 cho cả năm outcome, mỗi h trên mẫu riêng (hình có dải RI).
- `C1_early` = $\beta_2^{NCO,1}$; `C1_late` = $\beta_2^{NCO,6}-\beta_2^{NCO,2}$ (mẫu chung); `C2_early`, `C2_late` (E và L ở §8.2).

### 9.6 Không chạy trong đợt này
Hiệu chỉnh Teulings–Zubanov, distributed lag kiểu Lu & Nikolaev, bỏ ba năm đầu của mỗi ngân hàng, tách C3 thành 30–89 ngày và nonaccrual, bảng hoà giải tài liệu (S6), hiệu chỉnh đa kiểm định toàn họ v2–v3 (S8). Nếu chạy sau thì là thăm dò và phải ghi rõ là làm sau khi đã biết kết quả v3.

---

## 10. Nghiệm thu code trên dữ liệu giả (trước đóng băng)

Outcome hoán vị trong từng năm × nhóm FarmShare ≥ 25%; nhiệt và thiết kế giữ nguyên.

| Kiểm tra | Kết quả | Ngưỡng |
| --- | --- | --- |
| Đồng nhất thức §4.3 (C1, mẫu chung h = 0..6) | sai lệch 4,5e−14 | < 1e−8 |
| `V3Design.beta` = `fit_lp` (nhiệt hoán vị cố định) | sai lệch ≤ 1e−12 | < 1e−8 |
| Kích cỡ: tỷ lệ p_RI < 0,05 qua 5 θ × 20 seed giả, R = 99 | 3,0% (C5: 2/20, C3: 1/20, còn lại 0) | 2–9% |
| FWER của Westfall–Young, 20 seed giả, R = 99 | 0% (lượt R = 49: 5,0%) | ≲ 7% |
| Power khi gài tác động = MDE80, 20 lần, R = 49 | 55–85% theo θ | ≈ 80% |
| Chạy thật khi chưa có `hashes_frozen_v3.json` | dừng | phải dừng |

Power ở 4/5 θ thấp hơn mục tiêu. Tác động gài được ước lượng không chệch (θ̂/β gài = 0,93–1,15), nên nguyên nhân khả dĩ là R = 49 làm ngưỡng thô và 20 lần lặp có sai số khoảng 9 điểm % [I]. Hệ quả: MDE ở §6.2 có thể lạc quan. Code sau khi thêm κ được kiểm lại ở bước 1 của `RUN_v3.sh` trước khi đóng băng.

---

## 11. Quyết định cho các câu hỏi của Thịnh và Mai; chỗ khác với tài liệu trước

| Câu | Quyết định |
| --- | --- |
| Thịnh Q1 | θ_C1 tại h = 6. Dòng "kiểm định chính h=0..3" trong HANDOFF §1 là lỗi của bản bàn giao |
| Thịnh Q2, Mai Q4 | NCO tổng trên tổng dư nợ |
| Thịnh Q3, Mai Q9 | C2: cửa sổ ≤ 2022, bỏ ngân hàng áp dụng CECL sớm trong cửa sổ, allowance không điều kiện hoá. Không chạy bản kéo đến 2024 |
| Thịnh Q4 | C3: nợ đất NN, 30–89 ngày + nonaccrual, không gồm ≥ 90 ngày, trung bình β⁰ và β¹ |
| Thịnh Q5, Mai Q5 | C5: AG = đất NN + vay sản xuất NN, mẫu số tổng dư nợ t−1, θ = β² cộng dồn. Mọi outcome tính bằng điểm %, không log |
| Thịnh Q6, Mai Q7 | C4 giữ trong họ, khai báo là tái lập |
| Thịnh Q7 | Hạn hán: không có trong đặc tả xác nhận; R1 có đủ tương tác, hoán vị chung |
| Thịnh Q8 | Không tính sd hoán vị trên outcome thật trước đóng băng; đã dùng dữ liệu giả |
| Thịnh Q9 | Thêm trường hợp riêng (dòng 5, §8.2) |
| Thịnh Q10 | Giữ $\sigma_{GDD}$ của v1 |
| Thịnh Q11 | Lu & Nikolaev đưa 7 độ trễ vào cùng một hồi quy [F, Mai đọc Bảng 2]. Không chạy distributed lag ở đợt này |
| Thịnh Q12 | Placebo bằng outcome trước cú sốc, m = 2, 3 |
| Thịnh Q13 | R = 1000, seed 20261115 |
| Thịnh Q14 | Hai phía |
| Mai Q1, Q2 | Heat tính theo SD cấp ngân hàng; FS10 là FarmShare theo bước 10 điểm %, không phải biến giả |
| Mai Q3 | Được dùng trung bình không điều kiện theo nhiệt |
| Mai Q6 | Ghép cách A (năm 1 của Lu & Nikolaev ≈ h = 0) |
| Mai Q8 | Không dùng δ = 1 điểm %/năm; dùng quy ước 0,10 SD |
| Mai Q10 | Trọng số tiền gửi là của năm t−1 [F, `deposit_weight_l1`] |
| Mai Q11 | Tách C3 để sau, là thăm dò |
| Mai Q12 | Trích Lu & Nikolaev bản working paper 8/2024; Scott et al. RWP 22-06 bản 10/2025; Jaromczyk et al. chỉ trích sau khi có toàn văn |
| Mai: r của C1, C3 | C1: 0,126 chính, 0,063 phụ. C3: 0,092 chính, 0,25 phụ |

Khác với khung v3 (07/11): (i) outcome kéo đến 2025 vì Call Report 2025 đã đủ, thêm cú sốc 2019 cho h = 6; (ii) C3 chỉ gồm nợ đất NN; (iii) C5 chia tổng dư nợ; (iv) $\bar y$ của SESOI lấy ở nhóm FarmShare 15–35%; (v) hệ số κ; (vi) ngưỡng placebo 0,025.

---

## 12. Hạn chế đã biết

1. C2 chỉ có 10 năm sốc (2007–2016), gồm cả khủng hoảng 2008–2010. FE division × năm hấp thụ phần chung, nhưng công suất thấp.
2. Đến h = 6 mất khoảng 23% ngân hàng (sáp nhập, đóng cửa) [F]. Đây là chọn mẫu theo biến tương lai; chỉ có cờ attrition, không có hiệu chỉnh.
3. Năm áp dụng CECL suy từ RCONJJ30 (dự phòng tài sản PCD), có thể bỏ sót ngân hàng áp dụng sớm [F về định nghĩa mã, I về hệ quả].
4. C3 không gồm vay sản xuất NN, là phần nhạy với thời tiết nhất của sổ nông nghiệp.
5. FS10 và z dùng 3 quan sát đầu của mỗi ngân hàng: rò rỉ nhẹ với t trong hai năm đầu (đã nêu ở PAP v2).
6. Hạn hán dùng mùa 4–9 (khớp nhiệt); Brei et al. dùng 5–10 [theo Mai đọc, ? với bản thân người soạn].
7. Số neo SESOI đến từ bão (Lu & Nikolaev: holding company, 1994–2019) và hạn hán 2 năm (Özsoy: ngân hàng niêm yết). Chúng chỉ định cỡ, không dự báo cho mẫu này.
8. C2 và C4 có thành phần đã thấy ở v2 (§0).

---

## 13. File đóng băng và cách chạy

`PAP_v3.md`, `rq3_v3/_v3_spec.py`, `rq3_v3/run_v3.py`, `rq3_v3/build_v3.py`, `rq3_v3/sesoi_v3.py`, `rq3_v3/sesoi_v3.json`, `rq3_v3/data/build_drought.py`, `rq3_v3/data/fetch_usdm.py`. Hash dữ liệu: `panel_v3.parquet`, `county_year_drought.parquet`.

```bash
bash _claude_pap/rq3_v3/RUN_v3.sh     # từ thư mục repo: kiểm dữ liệu giả → hỏi xác nhận → đóng băng → chạy thật → gom kết quả
python3 _claude_pap/freeze_v3.py --verify
```

Mọi job trong danh sách đều chạy và đều được ghi. Kết quả viết vào `RESULTS_RQ3_v3.md` theo đúng §8, kể cả kết quả xấu hoặc mơ hồ.
