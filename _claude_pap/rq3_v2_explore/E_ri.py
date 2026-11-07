"""E_ri.py — RI (hoán vị năm thời tiết, như PAP v2) cho các outcome cơ chế THĂM DÒ. python3 E_ri.py <key> <chunk> <nperm>"""
import sys, os, json, time
sys.path.insert(0, os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v2"))
import E_run
from _v2_ri import *
import scipy.sparse as sp
key, chunk, nperm = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
CHD = os.path.expanduser("~/rq3cache/real")
fd = f"{CHD}/edesign_{key}.npz"
if not os.path.exists(fd):
    b = E_run.panel(); s = frame(b, key); Design.build(s, key, 2).save(fd)
D = Design.load(fd)
W = sp.load_npz(f"{CHD}/W.npz"); G = np.load(f"{CHD}/G.npy"); yrs = np.load(f"{CHD}/G_years.npy"); sd = float(open(f"{CHD}/sd.txt").read())
# W được dựng theo thứ tự hàng của panel_run; panel_explore được sắp xếp lại → ánh xạ theo (idrssd, year)
pr = pd.read_parquet(f"{CHD}/panel_run.parquet", columns=["idrssd", "year"]); pr["r"] = np.arange(len(pr))
pe = pd.read_parquet(f"{CHD}/panel_explore.parquet", columns=["idrssd", "year"])
mp = pe.merge(pr, on=["idrssd", "year"], how="left")["r"].to_numpy()
rows = mp[D.rows]
obs = D.beta(pd.read_parquet(f"{CHD}/panel_explore.parquet", columns=["heat"]).heat.to_numpy()[D.rows])
rng = np.random.default_rng([20261106, 900 + chunk]); out = []
for _ in range(nperm):
    pi = draw_pi(rng, range(2006, 2025)); out.append(D.beta(perm_heat(W, G, yrs, sd, rows, D.year, pi)))
np.save(f"{E_run.EX}/jobs/ri_{key}_{chunk}.npy", np.array(out)); json.dump(dict(key=key, obs=obs.tolist()), open(f"{E_run.EX}/jobs/ri_{key}_obs.json", "w"))
print(key, chunk, len(out), "obs x_FS10", round(float(obs[0]), 5))
