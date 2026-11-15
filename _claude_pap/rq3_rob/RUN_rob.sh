#!/bin/bash
# Chạy toàn bộ R1–R12 trên dữ liệu thật, rồi kiểm số liệu. Từ thư mục repo: bash _claude_pap/rq3_rob/RUN_rob.sh
# NW = số worker chạy song song (mặc định 3; giảm xuống 2 nếu máy thiếu RAM).
set -e
cd "$(dirname "$0")"
NW=${NW:-3}
python3 - <<'PY'
import os
R = os.path.expanduser("~/mnt/NCKH - NEU")
need = ["_claude_pap/out/county_panel.parquet", "_claude_eda/out/tab/ppt_county_year.parquet", "_claude_eda/out/tab/heat_county_year.parquet",
        "_claude_feasibility/out/02_bank_exposure_group.parquet", "_claude_pap/out/rma_coverage_ratio.csv", "_claude_pap/out/bank_scales.json",
        "_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet",
        "_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet",
        "_claude_feasibility/out/12_ffiec_ri_rce_bank_year.parquet", "_claude_pap/rq3_v3/out/panel_v3.parquet"]
miss = [p for p in need if not os.path.exists(os.path.join(R, p))]
print("Thiếu file:\n  " + "\n  ".join(miss) if miss else "Đủ file dữ liệu."); assert not miss
PY
mkdir -p results_real
for w in $(seq 0 $((NW-1))); do python3 -W ignore run_rob.py worker $w $NW 100000 > results_real/log_w$w.txt 2>&1 & done
wait
cat results_real/log_w*.txt
python3 -W ignore run_rob.py collect > results_real/collect_log.txt 2>&1 || true
python3 -W ignore checks_d.py > results_real/checks_log.txt 2>&1 || true
tail -40 results_real/collect_log.txt
echo "Xong. Gửi lại: results_real/rob_verdicts.md, results_real/rob_results.csv, results_real/checks_d.json, results_real/collect_log.txt"
