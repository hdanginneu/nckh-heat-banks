# rq3_v3: dữ liệu và khung code RQ3 v3 (trạng thái 12/11/2026)

PAP v3 **chưa đóng băng**. Mọi lệnh dưới đây chạy được trên dữ liệu giả (`PAP_FAKE=1`). Không có `PAP_FAKE=1`, `run_v3.py` dừng ngay nếu chưa có `_claude_pap/hashes_frozen_v3.json` khớp hash.

Đặc tả gốc: `PAP_v3_formulas.md` (Thịnh) và `PAP_v3_SESOI.md` (Mai) trên Drive, thư mục `outputs_v3`. Code ở đây theo đúng ký hiệu và số mục của file Thịnh.

## Thứ tự chạy (Mac/Linux; Windows dùng `set` thay `export`)

```bash
cd _claude_pap/rq3_v3
python3 data/fetch_usdm.py 10 160      # tải USDM theo bang × năm (chạy lại đến khi "còn thiếu: 0")
python3 data/build_drought.py          # số tuần D2+/D3+ có trọng số diện tích, tháng 4–9
python3 data/make_codebook.py          # codebook_v3.csv, tên mục lấy thẳng từ MDRM
python3 build_v3.py                    # panel_v3.parquet (giữ nguyên 145 cột v2, thêm 103 cột)
python3 qa_v3.py                       # nghiệm thu S2 + bảng QA trong qa/
export PAP_FAKE=1 FIT_SE=state         # FIT_SE=conley,state khi chạy thật (Conley chậm, ~30–80 s/thiết kế)
python3 run_v3.py prep
python3 run_v3.py worker 0 1 160 F_ CHK      # hồi quy LP (mỗi job một thiết kế)
python3 run_v3.py worker 0 2 160 RI_         # hoán vị; chạy song song worker 1 2 160 RI_
python3 run_v3.py collect                    # v3_lp_long.csv, v3_confirmatory.csv, perm_beta2.npy
python3 run_v3.py check                      # đồng nhất thức §3.3
python3 sizetest_v3.py size 1 20 49 160      # nghiệm thu §12.1; rồi: power 1 20 49 160; report
```

Máy chỉ có 3 GB RAM thì chạy tối đa 2 tiến trình song song (3 tiến trình đã bị hệ điều hành dừng vì hết bộ nhớ).

## File

| File | Việc |
| --- | --- |
| `data/fetch_usdm.py`, `data/build_drought.py` | Dữ liệu hạn hán USDM (Hữu Anh, S2) |
| `data/make_codebook.py`, `data/codebook_v3.csv` | Mã Call Report đối chiếu MDRM (Hữu Anh, S1a) |
| `build_v3.py`, `qa_v3.py`, `DATA_DICTIONARY_v3.md`, `QA_REPORT_v3.md`, `qa/` | Panel v3 và nghiệm thu (Hữu Anh, S2) |
| `_v3_spec.py` | CONFIG (các chỗ CHỜ CHỐT), mẫu S_{k,h}, mẫu chung, θ_C, ước lượng nhanh V3Design, chặn chạy thật |
| `run_v3.py` | Chạy LP, RI dùng chung π, WY, TOST, MDE (Khánh, S1 code) |
| `sizetest_v3.py`, `results_sizetest/` | Nghiệm thu code trên dữ liệu giả (§12) |
| `results_fake_s0/` | Một lượt chạy đầy đủ trên dữ liệu giả, R = 20. **Không diễn giải** |

## Nghiệm thu đã chạy (12/11/2026, dữ liệu giả)

| Kiểm tra (mục trong file Thịnh) | Kết quả | Ngưỡng |
| --- | --- | --- |
| §3.3 β cộng dồn = Σ β từng năm (C1, mẫu chung h=0..6, không winsorize) | sai lệch 4,5e−14 | < 1e−8 |
| §5.4 `V3Design.beta` = `fit_lp` (nhiệt hoán vị cố định π0) | sai lệch 8,3e−12 | < 1e−8 |
| §12.1 kích cỡ: tỷ lệ p_RI < 0,05 qua 5 C × 20 seed giả (R = 49) | 3,0% | 2–9% |
| §12.1 FWER của WY qua 20 seed giả | 5,0% | ≲ 7% |
| §12.2 power khi gài β = MDE80 (20 lần, R = 49) | C1 55%, C2 85%, C3 60%, C4 65%, C5 65% | ≈ 80% ± 12% |
| Chặn chạy thật khi chưa đóng băng | dừng với thông báo CHẶN | phải dừng |

Power ở §12.2 thấp hơn mục tiêu ở 4/5 C. Ước lượng θ khi gài tín hiệu không bị suy giảm (tỷ lệ θ̂/β gài = 0,93–1,15), nên nguyên nhân khả dĩ là R = 49 làm ngưỡng bác bỏ thô (p < 0,05 cần ≤ 1/49 hoán vị vượt) và 20 lần lặp có sai số chuẩn khoảng 9 điểm % [I]. Cần chạy lại với R ≥ 199 và 50 lần trước khi dùng MDE để ra quyết định.

## Chỗ CHỜ CHỐT trong `_v3_spec.CONFIG`

Biến outcome của từng C, `H_C1`, `OUT_LAST` (2024 hay 2025), cách đưa hạn hán (`DROUGHT`, `RI_DROUGHT`), R và seed, SESOI. Xem bảng quyết định trước khi đóng băng PAP v3 (Claude Doc) và `QA_REPORT_v3.md`.

## Chưa làm

- Teulings–Zubanov (§3.6) và distributed lag (§3.4): chưa có trong `run_v3.py` (chỉ là độ vững).
- Bỏ (b, t) có t < năm đầu + 3 (rò rỉ nhẹ của FS10, z; §10): chưa có tùy chọn.
- Tái tính độc lập bằng thư viện khác (§11, S3, việc của Thịnh).
