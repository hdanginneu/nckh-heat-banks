"""_pap_common.py — đường dẫn và hàm dùng chung cho _claude_pap/scripts.
Mọi script chạy độc lập từ thư mục này; hạt giống cố định SEED = 20261015.
"""
from pathlib import Path
import datetime as dt
import numpy as np
import pandas as pd
from scipy import sparse as sp
from scipy.sparse.linalg import lsmr

HERE = Path(__file__).resolve().parent
PAP = HERE.parent
ROOT = PAP.parent
OUT = PAP / "out"
EDA = ROOT / "_claude_eda"
TAB = EDA / "out" / "tab"
FEAS = ROOT / "_claude_feasibility"
DRIVE = ROOT / "_drive_latest"
RMA = Path.home() / "Projects" / "nckh_data" / "external" / "rma"
SEED = 20261015
RUN_LOG = PAP / "run_log.md"


def log_run(msg):
    """Thêm một dòng vào run_log.md (nhật ký chạy)."""
    with open(RUN_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n## {dt.datetime.now():%Y-%m-%d %H:%M}\n- {msg}\n")


def codes(s):
    return pd.factorize(pd.Series(s), sort=True)[0].astype(np.int64)


def absorb(M, group_codes, w=None, atol=1e-10, maxiter=5000):
    """Phần dư của M (n×k) sau khi hồi quy (có trọng số w) lên dummy nhóm (lsmr; không dùng phép chiếu luân phiên)."""
    M = np.asarray(M, dtype=float)
    if M.ndim == 1:
        M = M[:, None]
    n = len(M)
    w = np.ones(n) if w is None else np.asarray(w, dtype=float)
    if len(group_codes) == 1:
        g = group_codes[0]
        G = g.max() + 1
        sw = np.bincount(g, weights=w, minlength=G)
        return np.column_stack([M[:, j] - (np.bincount(g, weights=w * M[:, j], minlength=G) / sw)[g] for j in range(M.shape[1])])
    A = sp.hstack([sp.csr_matrix((np.ones(n), (np.arange(n), c)), shape=(n, c.max() + 1)) for c in group_codes]).tocsr()
    sw = np.sqrt(w)
    Aw = sp.diags(sw) @ A
    out = np.empty_like(M)
    for j in range(M.shape[1]):
        b = lsmr(Aw, sw * M[:, j], atol=atol, btol=atol, maxiter=maxiter)[0]
        out[:, j] = M[:, j] - A @ b
    return out


def haversine_matrix(lat, lon, R=6371.0088):
    """Ma trận khoảng cách cầu (km) giữa các điểm (độ)."""
    la = np.radians(np.asarray(lat, float))
    lo = np.radians(np.asarray(lon, float))
    dla = la[:, None] - la[None, :]
    dlo = lo[:, None] - lo[None, :]
    a = np.sin(dla / 2) ** 2 + np.cos(la)[:, None] * np.cos(la)[None, :] * np.sin(dlo / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def conley_meat(Xt, e, cty, yr, lat, lon, cutoff=1000.0, lag=2, kernel="uniform", tkernel="bartlett", radius=6371.0088):
    """Phần 'thịt' Conley có trễ thời gian.
    Xt: X đã khử FE (n×k); e: phần dư; cty: mã hạt trụ sở (0..C-1) của từng quan sát; yr: mã năm (0..T-1);
    lat/lon: tọa độ từng hạt (độ). Hạt nhân theo khoảng cách: 'uniform' (1 nếu d<=cutoff, giống fixest::vcov_conley)
    hoặc 'bartlett' (1-d/cutoff); hạt nhân theo thời gian: 'bartlett' 1-|t-s|/(lag+1) (lag=0 chỉ cùng năm) hoặc 'uniform' (1 với |t-s|<=lag;
    lag=T-1 tái tạo cách fixest coi mọi cặp quan sát trong cutoff là tương quan, bất kể năm).
    Điểm số x*e được cộng theo (hạt, năm) trước khi nhân hạt nhân."""
    n, k = Xt.shape
    C, T = int(cty.max()) + 1, int(yr.max()) + 1
    S = np.zeros((C, T, k))
    np.add.at(S, (cty, yr), Xt * e[:, None])
    D = haversine_matrix(lat[:C], lon[:C], R=radius)
    Kd = (D <= cutoff).astype(float) if kernel == "uniform" else np.clip(1.0 - D / cutoff, 0.0, None)
    meat = np.zeros((k, k))
    for l in range(0, lag + 1):
        wl = 1.0 - l / (lag + 1.0) if tkernel == "bartlett" else 1.0
        for t in range(0, T - l):
            St, Ss = S[:, t, :], S[:, t + l, :]
            if not (St.any() and Ss.any()):
                continue
            M = St.T @ (Kd @ Ss)
            meat += wl * (M if l == 0 else M + M.T)
    return meat


def conley_vcov(Xt, e, cty, yr, lat, lon, cutoff=1000.0, lag=2, kernel="uniform", tkernel="bartlett", ssc=1.0, psd_fix=True, radius=6371.0088):
    """V = ssc · bread · meat · bread; psd_fix cắt trị riêng âm về 0 (như vcov_fix của fixest)."""
    bread = np.linalg.inv(Xt.T @ Xt)
    V = ssc * bread @ conley_meat(Xt, e, cty, yr, lat, lon, cutoff, lag, kernel, tkernel, radius) @ bread
    V = (V + V.T) / 2
    if psd_fix:
        w, Q = np.linalg.eigh(V)
        if w.min() < 0:
            V = (Q * np.clip(w, 0, None)) @ Q.T
    return V


# ---------------- tra cứu địa lý / chia mẫu (đọc-chỉ từ _claude_eda) ----------------
STATE_FIPS = {"01": "AL", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA",
              "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA",
              "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
              "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
              "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY"}


def state_split():
    """state -> (division, half A/B). Chia A/B đã đóng băng từ EDA (SHA-256 trong DECISIONS_LOG)."""
    return pd.read_csv(TAB / "state_split.csv").set_index("state")


def county_centroids():
    """county_fips -> (lat, lon) tâm hạt TIGER (INTPTLAT/INTPTLON), đọc từ cache EDA."""
    import pickle
    g = pickle.loads((TAB / "_geo_cache.pkl").read_bytes())
    return pd.DataFrame({"county_fips": g["geoid"], "lat": g["lat"], "lon": g["lon"]}).drop_duplicates("county_fips")


def conley_se_ols(Xt, e, cty, yr, lat, lon, **kw):
    """SE Conley (vector) từ ma trận X đã khử FE; tiện cho gọi nhanh."""
    return np.sqrt(np.diag(conley_vcov(Xt, e, cty, yr, lat, lon, **kw)))
