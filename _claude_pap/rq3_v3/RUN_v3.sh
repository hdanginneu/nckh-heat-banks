#!/bin/bash
# RUN_v3.sh — chạy toàn bộ RQ3 v3 trên máy của bạn (Mac). Chạy từ thư mục repo:  bash _claude_pap/rq3_v3/RUN_v3.sh
# Bị ngắt giữa chừng thì chạy lại đúng lệnh này: job nào xong rồi sẽ được bỏ qua.
# Thứ tự: (0) kiểm môi trường → (1) kiểm code trên dữ liệu GIẢ → (2) đóng băng (hỏi xác nhận) → (3) chạy thật → (4) gom kết quả.
set -e
cd "$(dirname "$0")"
ROOT="$HOME/mnt/NCKH - NEU"
NW=${NW:-2}                                   # số tiến trình song song (máy ≥ 16 GB RAM có thể đặt NW=3)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

say() { printf '\n=== %s ===\n' "$1"; }
workers() {   # workers <tiền tố...>: chạy NW tiến trình song song đến khi hết job
  for w in $(seq 0 $((NW - 1))); do python3 run_v3.py worker $w $NW 1e9 "$@" & done; wait
}

say "0. Kiểm môi trường"
[ -d "$ROOT" ] || { echo "Thiếu $ROOT. Chạy setup_paths.sh trong repo trước."; exit 1; }
python3 -c "import pandas, numpy, scipy, pyarrow" || { echo "Thiếu thư viện: pip install -r requirements.txt"; exit 1; }
python3 ../../verify_hashes.py | tail -1
if [ ! -f "$ROOT/data_external/usdm/county_year_drought.parquet" ]; then
  echo "Chưa có dữ liệu hạn hán: tải USDM (~5 phút)"; python3 data/fetch_usdm.py 10 3000; python3 data/build_drought.py
fi
if [ ! -f "$ROOT/_claude_pap/rq3_v3/out/panel_v3.parquet" ]; then
  echo "Chưa có panel_v3: dựng lại (~1 phút)"; python3 build_v3.py
fi

say "1. Kiểm code trên dữ liệu GIẢ (outcome hoán vị, không cho biết gì về kết quả thật)"
export PAP_FAKE=1 FAKE_SEED=7 R_FAKE=20 FIT_SE=state
python3 run_v3.py prep
SPEC=dr python3 run_v3.py prep
workers RI_ CHK SE_TH_C1_6
export SPEC=dr; workers RI_ CHK; unset SPEC
python3 run_v3.py collect > /dev/null
SPEC=dr python3 run_v3.py collect > /dev/null
python3 run_v3.py check
python3 - <<'EOF'
import json, sys
bad = []
for d in ("results_fake_s7", "results_fake_s7_dr"):
    s = json.load(open(f"{d}/collect_summary.json"))
    if s["n_ri"] != s["n_designs"]: bad.append(f"{d}: thiếu job RI")
    dev = [v for k, v in s["chk"].items() if not k.startswith("Dr_")]
    if not dev or max(dev) > 1e-8: bad.append(f"{d}: CHK {dev}")
i = json.load(open("results_fake_s7/check_identity.json"))["identity_dev"]
if i > 1e-8: bad.append(f"đồng nhất thức {i}")
print("KIỂM GIẢ:", "ĐẠT" if not bad else bad); sys.exit(1 if bad else 0)
EOF
unset PAP_FAKE FAKE_SEED R_FAKE FIT_SE

say "2. Đóng băng PAP v3"
if [ -f ../hashes_frozen_v3.json ]; then
  echo "Đã đóng băng từ trước:"; python3 ../freeze_v3.py --verify
else
  echo "Sau bước này KHÔNG sửa được PAP_v3.md và code nữa."
  read -r -p "Đã đọc PAP_v3.md (ít nhất §8 và §11)? Gõ DONG BANG để tiếp tục: " ans
  [ "$ans" = "DONG BANG" ] || { echo "Dừng, chưa đóng băng."; exit 1; }
  python3 ../freeze_v3.py
fi

say "3a. Chạy thật — đặc tả chính (R = 1000; khoảng 1–2 giờ)"
python3 run_v3.py prep
workers RI_ CHK SE_
python3 run_v3.py collect

say "3b. Chạy thật — độ vững R1 có hạn hán (khoảng 15 phút)"
export SPEC=dr
python3 run_v3.py prep
workers RI_ CHK
python3 run_v3.py collect
unset SPEC

say "4. Xong"
python3 ../freeze_v3.py --verify
python3 ../../verify_hashes.py | tail -1
echo "Gửi lại hai thư mục: $(pwd)/results_real  và  $(pwd)/results_real_dr  (bỏ thư mục jobs/ cũng được)"
