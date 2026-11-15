#!/bin/bash
# E41: dựng mẫu mở rộng 1995–2006 rồi chạy ước lượng theo PAP_E41.md. Từ thư mục repo: bash _claude_pap/rq3_e41/RUN_e41.sh
# NW = số worker song song (mặc định 3). Bước dựng dữ liệu bỏ qua nếu file đã có (xoá out/cr_parts, out/panel_e41.parquet để dựng lại).
set -e
cd "$(dirname "$0")"
NW=${NW:-3}
python3 - <<'PY'
import os
R = os.path.expanduser("~/mnt/NCKH - NEU")
need = ["data_external/ext_pre2005/chicagofed/call0012-zip.zip", "data_external/ext_pre2005/ffiec_bulk/FFIEC_CDR_Call_Bulk_All_Schedules_12312004.zip",
        "data_external/ext_pre2005/sod/sod_2005.parquet", "data_external/ext_pre2005/fdic_cb/cb_2004.parquet",
        "_claude_eda/out/tab/heat_county_year.parquet", "_claude_eda/out/tab/ppt_county_year.parquet", "_claude_pap/out/bank_scales.json",
        "_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet",
        "_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet", "_claude_feasibility/out/07_ffiec_ag_bank_year.parquet"]
miss = [p for p in need if not os.path.exists(os.path.join(R, p))]
print("Thiếu file:\n  " + "\n  ".join(miss) if miss else "Đủ file dữ liệu."); assert not miss
PY
O="$HOME/mnt/NCKH - NEU/_claude_pap/rq3_e41/out"
[ -f "$O/cr_1994_2004.parquet" ] || python3 -W ignore 01_extract_cr.py
python3 -W ignore 02_check_seam.py
[ -f "$O/fw_1995_2006.parquet" ] || python3 -W ignore 03_sod_weights.py
[ -f "$O/panel_e41.parquet" ] || python3 -W ignore 04_build_panel_ext.py
mkdir -p results_real
for w in $(seq 0 $((NW-1))); do python3 -W ignore run_e41.py worker $w $NW 100000 > results_real/log_w$w.txt 2>&1 & done
wait
cat results_real/log_w*.txt
python3 -W ignore run_e41.py collect > results_real/collect_log.txt 2>&1 || true
cp "$O"/check_02.txt "$O"/check_03.txt "$O"/panel_e41_flow.csv "$O"/cr_coverage.csv results_real/ 2>/dev/null || true
tail -30 results_real/collect_log.txt
echo "Xong. Gửi lại: results_real/e41_verdicts.md, results_real/e41_results.csv, results_real/collect_log.txt"
