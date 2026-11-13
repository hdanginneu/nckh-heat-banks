#!/usr/bin/env bash
# Tạo cấu trúc ~/mnt/NCKH - NEU mà code đã đóng băng mong đợi.
set -e
DATA="$(cd "$1" && pwd)"; REPO="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HOME/mnt/NCKH - NEU"
if [ -e "$ROOT" ] && [ ! -L "$ROOT/_claude_pap" ]; then echo "Đã tồn tại $ROOT (không phải bản setup). Dừng để tránh ghi đè."; exit 1; fi
mkdir -p "$ROOT"
ln -sfn "$REPO/_claude_pap" "$ROOT/_claude_pap"
for d in _drive_latest data_external _claude_eda _claude_feasibility; do ln -sfn "$DATA/$d" "$ROOT/$d"; done
# file dữ liệu nằm trong _claude_pap (không có trong git)
mkdir -p "$REPO/_claude_pap/out" "$REPO/_claude_pap/rq3_explore"
ln -sfn "$DATA/_claude_pap/out/county_panel.parquet" "$REPO/_claude_pap/out/county_panel.parquet"
ln -sfn "$DATA/_claude_pap/out/bank_panel.parquet" "$REPO/_claude_pap/out/bank_panel.parquet"
ln -sfn "$DATA/_claude_pap/rq3_explore/bank_coverage_pre.parquet" "$REPO/_claude_pap/rq3_explore/bank_coverage_pre.parquet"
# _pap_common.py lấy ROOT theo đường dẫn THẬT của file (sau symlink) = repo → repo cũng cần các thư mục dữ liệu
for d in _drive_latest data_external _claude_eda _claude_feasibility; do ln -sfn "$ROOT/$d" "$REPO/$d"; done
# dữ liệu v3 (không có trong git)
mkdir -p "$REPO/_claude_pap/rq3_v3"
[ -e "$REPO/_claude_pap/rq3_v3/out" ] || ln -sfn "$DATA/_claude_pap/rq3_v3/out" "$REPO/_claude_pap/rq3_v3/out"
mkdir -p /tmp/g1   # script thăm dò rq3_explore/G*.py ghi vào đây
echo "OK: $ROOT -> repo + data_inputs"
