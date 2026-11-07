"""02_conley_validate.py — kiểm định cài đặt Conley có trễ thời gian (`_pap_common.conley_vcov`).
Dữ liệu mô phỏng (không dùng outcome thật). Ba phép kiểm:
 (1) lát cắt ngang (T=1): khớp `fixest::vcov_conley` (nhân đều, khoảng cách cầu, tắt hiệu chỉnh mẫu nhỏ);
 (2) panel với hạt nhân thời gian đều, lag=T-1: tái tạo cách fixest coi mọi cặp quan sát trong cutoff là tương quan;
 (3) so với tính vét cạn O(N²) cho Bartlett-thời gian lag=2 (khẳng định bước cộng điểm số theo hạt×năm đúng).
Kết quả ghi `out/02_conley_validation.csv`.
"""
import subprocess, tempfile, os
import numpy as np
import pandas as pd
from _pap_common import *

rng = np.random.default_rng(SEED)
# fixest 'spherical' dùng bán kính hiệu dụng ≈ 6375,98 km (đo bằng bisection trên khoảng cách cặp điểm, tỉ lệ 1,00078 so với 6371,0088)
R_FIXEST = 6371.0088 * 1.000782
RSCRIPT = "/usr/local/bin/Rscript"
RLIB = os.path.expanduser("~/Library/R/arm64/4.5/library")


def simulate(C=150, T=8, per_county=3):
    lat = rng.uniform(26, 48, C); lon = rng.uniform(-122, -68, C)
    rows = []
    # lỗi tương quan không gian (theo năm) + tương quan thời gian (AR(1) theo hạt)
    D = haversine_matrix(lat, lon)
    Lc = np.linalg.cholesky(np.exp(-D / 500.0) + 1e-6 * np.eye(C))
    z = np.zeros((C, T)); z[:, 0] = Lc @ rng.standard_normal(C)
    for t in range(1, T):
        z[:, t] = 0.5 * z[:, t - 1] + Lc @ rng.standard_normal(C)
    xs = Lc @ rng.standard_normal((C, T))
    b = 0
    for c in range(C):
        for j in range(per_county):
            b += 1
            for t in range(T):
                if rng.random() < 0.9:
                    x1 = xs[c, t] + rng.standard_normal()
                    rows.append((b, c, t, lat[c], lon[c], x1, rng.standard_normal(), 0.3 * x1 + z[c, t] + rng.standard_normal()))
    df = pd.DataFrame(rows, columns=["bank", "cty", "yr", "lat", "lon", "x1", "x2", "y"])
    df["div"] = (df["cty"] % 5)
    return df, lat, lon


def fit(df, fe_cols, xcols=("x1", "x2")):
    gc = [codes(df[c]) for c in fe_cols]
    Xt = absorb(df[list(xcols)].to_numpy(), gc)
    yt = absorb(df["y"].to_numpy(), gc)[:, 0]
    beta = np.linalg.solve(Xt.T @ Xt, Xt.T @ yt)
    return Xt, yt - Xt @ beta, beta


def r_fixest(df, cutoff, panel_fe=True, fe="bank + div^yr"):
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, "d.csv"); df.to_csv(f, index=False)
        code = f"""suppressWarnings(library(fixest)); d <- read.csv("{f}")
m <- feols(y ~ x1 + x2 {'| ' + fe if panel_fe else ''}, d)
v <- vcov_conley(m, lat = ~lat, lon = ~lon, cutoff = {cutoff}, distance = "spherical", ssc = ssc(K.adj = FALSE, adj = FALSE, cluster.adj = FALSE))
cat(sprintf("%.10f %.10f\\n", coef(m)[1], sqrt(v[1,1]))); cat(sprintf("%.10f %.10f\\n", coef(m)[2], sqrt(v[2,2])))"""
        out = subprocess.run([RSCRIPT, "-e", code], capture_output=True, text=True, env={**os.environ, "R_LIBS_USER": RLIB}).stdout.split()
    return np.array(out, float).reshape(2, 2)  # [coef, se] por variable


res = []
# (1) lát cắt ngang
d1, lat, lon = simulate(C=400, T=1, per_county=1)
d1["yr"] = 0
Xt, e, beta = fit(d1, ["div"])
V = conley_vcov(Xt, e, d1["cty"].to_numpy(), d1["yr"].to_numpy(), lat, lon, cutoff=1000, lag=0, kernel="uniform", psd_fix=True, radius=R_FIXEST)
rf = r_fixest(d1, 1000, fe="div")
for j, nm in enumerate(["x1", "x2"]):
    res.append(dict(test="1_cross_section_vs_fixest", var=nm, beta_py=beta[j], beta_R=rf[j, 0], se_py=np.sqrt(V[j, j]), se_R=rf[j, 1]))

# (2) panel, uniform thời gian lag=T-1
d2, lat, lon = simulate(C=150, T=8, per_county=3)
d2["div_yr"] = d2["div"].astype(str) + "_" + d2["yr"].astype(str)
gc = [codes(d2["bank"]), codes(d2["div_yr"])]
Xt = absorb(d2[["x1", "x2"]].to_numpy(), gc); yt = absorb(d2["y"].to_numpy(), gc)[:, 0]
beta = np.linalg.solve(Xt.T @ Xt, Xt.T @ yt); e = yt - Xt @ beta
T = d2["yr"].max() + 1
V = conley_vcov(Xt, e, d2["cty"].to_numpy(), d2["yr"].to_numpy(), lat, lon, cutoff=1000, lag=T - 1, kernel="uniform", tkernel="uniform", psd_fix=True, radius=R_FIXEST)
rf = r_fixest(d2, 1000, fe="bank + div^yr")
for j, nm in enumerate(["x1", "x2"]):
    res.append(dict(test="2_panel_uniformtime_vs_fixest", var=nm, beta_py=beta[j], beta_R=rf[j, 0], se_py=np.sqrt(V[j, j]), se_R=rf[j, 1]))

# (3) vét cạn Bartlett-thời gian lag=2, hạt nhân đều không gian
cty, yr = d2["cty"].to_numpy(), d2["yr"].to_numpy()
D = haversine_matrix(lat, lon)
S = Xt * e[:, None]
meat = np.zeros((2, 2))
sub = np.arange(len(d2))
Dn = D[np.ix_(cty, cty)]
dy = np.abs(yr[:, None] - yr[None, :])
W = ((Dn <= 1000) * np.clip(1 - dy / 3.0, 0, None))
meat = S.T @ (W @ S)
bread = np.linalg.inv(Xt.T @ Xt)
Vb = bread @ meat @ bread
Va = conley_vcov(Xt, e, cty, yr, lat, lon, cutoff=1000, lag=2, kernel="uniform", tkernel="bartlett", psd_fix=False)
for j, nm in enumerate(["x1", "x2"]):
    res.append(dict(test="3_bartlett_lag2_vs_bruteforce", var=nm, beta_py=beta[j], beta_R=np.nan, se_py=np.sqrt(Va[j, j]), se_R=np.sqrt(Vb[j, j])))

r = pd.DataFrame(res)
r["rel_diff_se"] = (r["se_py"] / r["se_R"] - 1).abs()
r.to_csv(OUT / "02_conley_validation.csv", index=False)
print(r.to_string())
ok = (r["rel_diff_se"] < 1e-6).all()
print("PASS" if ok else "FAIL")
log_run(f"02_conley_validate: {'PASS' if ok else 'FAIL'} (max rel diff SE = {r['rel_diff_se'].max():.2e}) — `out/02_conley_validation.csv`")
