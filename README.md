# nckh-heat-banks — Nhiệt cực đoan và ngân hàng cộng đồng nông nghiệp Mỹ

Mã nguồn đầy đủ đến hết PAP v2.4 (07/11/2026). Bước tiếp theo: PAP v3 (xem `HANDOFF_v3.md`).

## 1. Cài đặt
```bash
cd ~/Projects/"NCKH NEU "        # quy ước: code để local, KHÔNG để trong OneDrive
git clone <repo-url> && cd nckh-heat-banks
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # Python 3.10
```

## 2. Dữ liệu (KHÔNG có trong git)
Quy ước: dữ liệu gốc và output để trên OneDrive/Drive; code, venv, cache, file tạm để trong `~/Projects`.
Output của v3 ghi vào thư mục output trên OneDrive (khai báo đường dẫn tuyệt đối ở khối cấu hình đầu mỗi script mới).
Tải thư mục `data_inputs/` từ Google Drive (thư mục "HANDOFF v3" của nhóm), rồi:
```bash
bash setup_paths.sh /đường/dẫn/tới/data_inputs
python verify_data.py /đường/dẫn/tới/data_inputs/MANIFEST.sha256   # phải báo Lỗi: 0
python verify_hashes.py                  # kiểm code đã đóng băng không bị sửa
```
Code cũ dùng đường dẫn cố định `~/mnt/NCKH - NEU/...`. `setup_paths.sh` tạo đúng cấu trúc đó bằng symlink,
nên **không sửa đường dẫn trong các file .py đã đóng băng** (sửa sẽ làm sai hash PAP).

## 3. Cấu trúc
| Thư mục | Nội dung |
|---|---|
| `_claude_pap/PAP_v2*.md`, `hashes_frozen_v2*.json`, `freeze_v2*.py` | Kế hoạch phân tích đăng ký trước và hash |
| `_claude_pap/scripts/` | Hàm dùng chung (`_pap_common.py`, `_pap_est.py`), dựng panel |
| `_claude_pap/rq3_v2/` | Thiết kế V2: build, spec, RI (`_v2_ri.py`), chạy chính `10_run_rq3_v2.py`, chẩn đoán T0–T6 |
| `_claude_pap/rq3_v21` … `rq3_v24` | Các PAP bổ sung v2.1–v2.4 |
| `_claude_pap/rq3_v2_explore/`, `rq3_explore/` | Phân tích thăm dò (không phải xác nhận) |
| `*/results/*.csv` | Kết quả đã chạy, để đối chiếu |
| `_claude_pap/RESULTS_RQ3_v2.md`, `DECISIONS.md` | Báo cáo kết quả và nhật ký quyết định |

## 4. Chạy lại kết quả v2 (kiểm tái lập)
```bash
export OMP_NUM_THREADS=1
cd _claude_pap/rq3_v2
python _v2_build.py                      # dựng panel -> out/panel_v2.parquet
python 10_run_rq3_v2.py jobs && python 10_run_rq3_v2.py worker 0 3 & python 10_run_rq3_v2.py worker 1 3 & python 10_run_rq3_v2.py worker 2 3; wait
python 10_run_rq3_v2.py collect
```
So `results/primary_ri_results.csv` mới với bản trong git: β phải trùng (sai khác < 1e-6); p_RI trùng vì seed cố định.
Lưu ý RAM: dựng panel chạy MỘT tiến trình; worker RI tối đa 3 tiến trình.
Cú pháp lệnh từng script: xem phần đầu file và `_claude_pap/run_log.md`.

## 5. Quy tắc
- Không sửa file đã có trong `hashes_frozen_*.json`. Code mới đặt trong thư mục mới (`rq3_v3/`).
- Không chạy kiểm định xác nhận v3 trước khi `PAP_v3.md` được đóng băng.
- Commit nhỏ, thông điệp rõ; không commit dữ liệu (.parquet, .pkl, .xlsx đã trong `.gitignore`).
