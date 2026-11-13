"""Thăm dò, sau đóng băng: Westfall–Young step-down max-|t| cho họ 8 khoản mục bảng cân đối E3.
Dùng đúng ma trận hoán vị đã lưu trong results_explore/jobs (cùng π cho mọi khoản mục), cùng công thức với run_v3.py (PAP §5.3)."""
import json, os, numpy as np, pandas as pd
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_explore")
ITEMS = ["dL", "dAG", "dNONAG", "dDEP", "dTA", "dSEC", "dCASH", "dLA"]
J = {k: json.load(open(f"{D}/jobs/E3_{k}.json")) for k in ITEMS}
obs = np.array([float(np.ravel(J[k]["obs"])[0]) for k in ITEMS])
TS = np.column_stack([np.array(J[k]["perm"], dtype=float).reshape(len(J[k]["perm"]), -1)[:, 0] for k in ITEMS])
sv = TS.std(axis=0, ddof=1); tobs = np.abs(obs) / sv; T = np.abs(TS) / sv; R = T.shape[0]
p_ri = (1 + (np.abs(TS) >= np.abs(obs)).sum(axis=0)) / (1 + R)
order = np.argsort(-tobs); padj = np.zeros(len(ITEMS)); prev = 0.0
for k, i in enumerate(order):
    p_ = (1 + (T[:, order[k:]].max(axis=1) >= tobs[i]).sum()) / (1 + R); prev = max(prev, p_); padj[i] = prev
O = pd.DataFrame(dict(item=ITEMS, theta=obs, sd_perm=sv, p_RI=p_ri, p_WY=padj, R=R))
O.to_csv(f"{D}/e3_wy.csv", index=False); print(O.round(4).to_string(index=False))
