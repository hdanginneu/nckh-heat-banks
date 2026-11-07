"""E2_distlag.py — THĂM DÒ sau PAP v2.1: độ trễ phân phối nhiệt (t−2, t−1, t, t+1) × {FS10, Z} cho dLOAN, dAGP, dLIQ (V2; Conley + bang).
Mục đích: xem placebo lead hỏng của dư nợ có do đợt nóng/hạn nhiều năm (tự tương quan nhiệt) hay không. python3 E2_distlag.py <key>"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import E_run
from E_run import *
key = sys.argv[1]
b = E_run.panel()
v = b.groupby("idrssd")["heat"].shift(2); yr = b.groupby("idrssd")["year"].shift(2)
b["heat_lag2"] = np.where(yr == b.year - 2, v, np.nan)
OUTS["dLIQ"] = OUTS["dLIQ"]
s = frame(b, key, need_lead="heat_lag2").dropna(subset=["heat_lag1", "heat_lead1"]).copy()
ex = []
for pre, hv in (("G2_", "heat_lag2"), ("G1_", "heat_lag1"), ("L_", "heat_lead1")):
    for m in LIN: s[pre + "x_" + m] = s[hv] * s[m]; ex.append(pre + "x_" + m)
    ex.append(hv)
rc, rs, xs = fit2(s, key, "heat", extra=ex)
keep = {"x_FS10", "G1_x_FS10", "G2_x_FS10", "L_x_FS10"}
rows = rows_of(rc, xs, f"distlag:{key}", key, "conley", keep) + rows_of(rs, xs, f"distlag:{key}", key, "state", keep)
# tương quan (sau FE bank + div×năm) giữa các số hạng nhiệt×FS10
from _pap_common import absorb, codes
Z = absorb(np.column_stack([s[h].to_numpy() * s.FS10.to_numpy() for h in ("heat_lag2", "heat_lag1", "heat", "heat_lead1")]), [codes(s.idrssd), codes(s.div_year)])
C = np.corrcoef(Z.T).round(3).tolist()
json.dump(dict(task=f"distlag:{key}", rows=rows, corr_lag2_lag1_t_lead=C), open(f"{EX}/jobs/distlag_{key}.json", "w"))
for r in rows: print(r["se_type"], r["coef"], round(r["beta"], 4), round(r["se"], 4), round(r["p"], 4), r["n"])
print("corr heat×FS (lag2, lag1, t, lead1) sau FE:", C)
