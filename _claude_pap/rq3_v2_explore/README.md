# rq3_v2_explore — THĂM DÒ SAU ĐÓNG BĂNG PAP v2 (06/11/2026)
Chạy SAU khi đã thấy kết quả xác nhận (rq3_v2/results/). Không thuộc phần xác nhận; dùng cùng đặc tả V2 (import _v2_spec đã đóng băng).
- E_run.py: phân rã bảng cân đối của ΔLIQ (mech:*), NCO/ΔNPL, jackknife năm (jack:*), placebo lead2/lead3/lag (plac:*), FE bang×năm (stfe:*), bỏ WSC×2011. Kết quả: jobs/*.json, gộp ở E_results_long.csv.
- E_ri.py: RI hoán vị năm thời tiết (R = 180, seed [20261106, 900+chunk]) cho dLOAN, dAGP, dNONAG, dDEP. Kết quả: jobs/ri_*.npy, ri_*_obs.json.
Tóm tắt và diễn giải: ../RESULTS_RQ3_v2.md §3.
