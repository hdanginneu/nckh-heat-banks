"""Hằng số và đường dẫn dùng chung cho phần mở rộng E41 (mẫu 1995–2006). Chỉ dựng dữ liệu; ước lượng nằm ở run_e41.py."""
import os
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
EXT = f"{ROOT}/data_external/ext_pre2005"
OUT = f"{ROOT}/_claude_pap/rq3_e41/out"; os.makedirs(OUT, exist_ok=True)     # dữ liệu dựng ra: không commit
TMP = os.path.expanduser("~/rq3cache/e41_unzip"); os.makedirs(TMP, exist_ok=True)
P1F = f"{ROOT}/_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet"
FW = f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet"
SODY = f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_sod_bank_year.parquet"
AG07 = f"{ROOT}/_claude_feasibility/out/07_ffiec_ag_bank_year.parquet"
TAB = f"{ROOT}/_claude_eda/out/tab"
CR_YEARS = range(1994, 2005)          # Call Report tự trích (Chicago Fed 1994–2000, FFIEC bulk 2001–2004); từ 2005 dùng Phase 1
T_EXT = (1995, 2006)                   # năm sốc của mẫu mở rộng; mẫu chính bắt đầu 2007 nên hai mẫu không chung năm sốc
CONUS_DC = {"AL", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI",
            "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX",
            "UT", "VT", "VA", "WA", "WV", "WI", "WY"}
