"""_pap_est.py — động cơ ước lượng dùng chung cho các script giai đoạn 2.
 - fit_lp(): hồi quy FE (hấp thụ bằng lsmr) trên panel không cân bằng, SE Conley (1.000 km, trễ 2 năm, hạt nhân đều theo
   khoảng cách, Bartlett theo thời gian) hoặc cluster (bang / ngân hàng / division×năm).
 - Chế độ DỮ LIỆU GIẢ: đặt PAP_FAKE=1 → mọi cột kết cục bị hoán vị ngẫu nhiên TRONG TỪNG NĂM (seed 20261015); kết quả ghi
   vào out/results_fake/ và specs_run_FAKE.csv. Dùng để kiểm tra code, không để diễn giải.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
from _pap_common import *

FAKE = os.environ.get("PAP_FAKE", "0") == "1"
RES = OUT / ("results_fake" if FAKE else "results")
RES.mkdir(parents=True, exist_ok=True)
SPECS = PAP / ("specs_run_FAKE.csv" if FAKE else "specs_run.csv")
Z90, Z95 = 1.6448536269514722, 1.959963984540054

BANK_OUTCOMES = None  # điền ở load_bank
COUNTY_OUTCOMES = ["y_lncrop", "crop_kusd", "y_govpay", "y_indem_hd", "y_indem_heat", "y_indem_total", "y_indem_hdwide"]


def _permute_within_year(df, cols, seed_offset=0, strata=()):
    """Hoán vị CẢ HÀNG kết cục trong từng năm (và từng tầng, nếu có), giữ quan hệ giữa các kết cục, phá quan hệ nhiệt–kết cục.
    Tầng 'ag25' giữ nguyên phân phối biên của mẫu nông nghiệp (không trộn ngân hàng nông nghiệp với ngân hàng phi nông nghiệp)."""
    rng = np.random.default_rng(SEED + seed_offset)
    out = df.copy()
    ci = [out.columns.get_loc(c) for c in cols]
    for _, idx in out.groupby(["year"] + list(strata)).indices.items():
        perm = rng.permutation(len(idx))
        out.iloc[idx, ci] = out.iloc[idx[perm], ci].to_numpy()
    return out


def load_county():
    d = pd.read_parquet(OUT / "county_panel.parquet")
    if FAKE:
        d = _permute_within_year(d, COUNTY_OUTCOMES, 1)
    return d


def load_bank():
    d = pd.read_parquet(OUT / "bank_panel.parquet")
    cols = [c for c in d.columns if c[:2] in ("C1", "C2", "C3", "C4", "D1", "D2") and "_h" in c or c.startswith(("LOSS_", "S_"))]
    cols += ["fail_t1", "crop_fp_kusd"]
    if FAKE:
        d = _permute_within_year(d, cols, 2, strata=("ag25",))
    return d


def tost(beta, se, delta, z=Z90):
    """Kiểm định tương đương: CI 90% nằm trong [−delta, +delta]."""
    lo, hi = beta - z * se, beta + z * se
    return bool((lo > -delta) and (hi < delta)), lo, hi


def fit_lp(df, y, xcols, fe, se="conley", cty=None, w=None, cluster=None, lag=2, cutoff=1000.0, kernel="uniform", keep=False, lat="lat", lon="lon"):
    """OLS với FE hấp thụ.
    df: DataFrame đã lọc mẫu (hàng có y, xcols, fe đều hợp lệ). xcols[0] là biến quan tâm (hoặc nhiều biến).
    fe: danh sách tên cột nhóm (ví dụ ['idrssd','div_year']). se: 'conley' | 'cluster' (dùng cluster=tên cột).
    cty: tên cột mã hạt dùng cho Conley (cùng lat/lon trong df). Trả về dict hệ số cho mọi xcols."""
    d = df.dropna(subset=[y] + list(xcols) + list(fe) + ([w] if w else [])).copy()
    n = len(d)
    gc = [codes(d[c]) for c in fe]
    yv = d[y].to_numpy(float)
    X = d[list(xcols)].to_numpy(float)
    wv = None if w is None else d[w].to_numpy(float)
    if wv is not None:
        wv = wv / wv.mean()   # chuẩn hóa trọng số về trung bình 1 (không đổi β; ổn định số học)
    Z = absorb(np.column_stack([yv, X]), gc, wv)
    yt, Xt = Z[:, 0], Z[:, 1:]
    sw = np.ones(n) if wv is None else wv
    XtWX = Xt.T @ (Xt * sw[:, None])
    beta = np.linalg.solve(XtWX, Xt.T @ (sw * yt))
    e = yt - Xt @ beta
    k = Xt.shape[1]
    out = {"n": n, "beta": beta, "k": k}
    # unit counts
    out["n_units"] = d[fe[0]].nunique()
    if se == "conley":
        cc = codes(d[cty])
        first = pd.DataFrame({"c": cc, "lat": d[lat].to_numpy(), "lon": d[lon].to_numpy()}).drop_duplicates("c").sort_values("c")
        yr = codes(d["year"])
        sc = np.sqrt(sw)
        V = conley_vcov(Xt * sc[:, None], e * sc, cc, yr, first.lat.to_numpy(), first.lon.to_numpy(), cutoff=cutoff, lag=lag, kernel=kernel, ssc=1.0)
        out["n_clusters"] = int(first.shape[0])
        out["dist"] = "z"
    else:
        cl = codes(d[cluster]); G = int(cl.max() + 1)
        S = np.zeros((G, k)); np.add.at(S, cl, (sw * e)[:, None] * Xt)
        inv = np.linalg.inv(XtWX)
        V = inv @ (S.T @ S) @ inv * (G / (G - 1)) * ((n - 1) / (n - k))
        out["n_clusters"] = G
        out["dist"] = f"t{G - 1}"
    se_v = np.sqrt(np.diag(V))
    out["se"] = se_v
    out["V"] = V
    crit95 = Z95 if out["dist"] == "z" else stats.t.ppf(0.975, out["n_clusters"] - 1)
    crit90 = Z90 if out["dist"] == "z" else stats.t.ppf(0.95, out["n_clusters"] - 1)
    out["ci95"] = (beta - crit95 * se_v, beta + crit95 * se_v)
    out["ci90"] = (beta - crit90 * se_v, beta + crit90 * se_v)
    out["p"] = 2 * (1 - (stats.norm.cdf(np.abs(beta / se_v)) if out["dist"] == "z" else stats.t.cdf(np.abs(beta / se_v), out["n_clusters"] - 1)))
    out["sd_y"] = float(np.std(yv))
    out["r2_within"] = float(1 - np.sum(sw * e ** 2) / np.sum(sw * (yt - np.average(yt, weights=sw)) ** 2))
    if keep:
        out["Xt"], out["e"], out["d"] = Xt, e, d
    return out


def null_se(df, y, xcols, fe, cty, lag=2, cutoff=1000.0, kernel="uniform", lat="lat", lon="lon"):
    """SE Conley của hệ số nhiệt dưới H0 (β=0): dùng phần dư của y sau FE + controls (không có nhiệt), không tính β.
    Dùng cho bảng MDE trước đóng băng. Trả về (se_heat, n)."""
    d = df.dropna(subset=[y] + list(xcols) + list(fe)).copy()
    gc = [codes(d[c]) for c in fe]
    ctrl = list(xcols[1:])
    Z = absorb(np.column_stack([d[y].to_numpy(float), d[list(xcols)].to_numpy(float)]), gc)
    yt, Xt = Z[:, 0], Z[:, 1:]
    if ctrl:
        Cc = Xt[:, 1:]
        b0 = np.linalg.lstsq(Cc, yt, rcond=None)[0]
        e0 = yt - Cc @ b0
    else:
        e0 = yt
    cc = codes(d[cty])
    first = pd.DataFrame({"c": cc, "lat": d[lat].to_numpy(), "lon": d[lon].to_numpy()}).drop_duplicates("c").sort_values("c")
    V = conley_vcov(Xt, e0, cc, codes(d["year"]), first.lat.to_numpy(), first.lon.to_numpy(), cutoff=cutoff, lag=lag, kernel=kernel)
    return float(np.sqrt(V[0, 0])), len(d)


SPEC_COLS = ["timestamp", "family", "outcome", "h", "spec", "sample", "beta", "se", "ci95_lo", "ci95_hi", "ci90_lo", "ci90_hi", "p", "n", "n_units",
             "n_clusters", "sd_y", "dist", "extra_json"]


def append_spec(row):
    """Ghi một dòng vào specs_run.csv với bộ cột cố định (các trường ngoài danh sách đi vào extra_json)."""
    import json
    base = {c: row.get(c, np.nan) for c in SPEC_COLS if c != "extra_json"}
    extra = {k: (v.item() if hasattr(v, "item") else v) for k, v in row.items() if k not in SPEC_COLS}
    base["extra_json"] = json.dumps(extra, default=str, ensure_ascii=False)
    pd.DataFrame([base], columns=SPEC_COLS).to_csv(SPECS, mode="a", header=not SPECS.exists(), index=False)


def record(family, outcome, h, spec, sample, r, j=0, extra=None):
    """Ghi một dòng vào specs_run.csv (mọi đặc tả đã chạy) và trả về dict đầy đủ."""
    row = dict(timestamp=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), family=family, outcome=outcome, h=h, spec=spec, sample=sample,
               beta=float(r["beta"][j]), se=float(r["se"][j]), ci95_lo=float(r["ci95"][0][j]), ci95_hi=float(r["ci95"][1][j]),
               ci90_lo=float(r["ci90"][0][j]), ci90_hi=float(r["ci90"][1][j]), p=float(r["p"][j]), n=r["n"], n_units=r["n_units"],
               n_clusters=r["n_clusters"], sd_y=r["sd_y"], dist=r["dist"])
    if extra:
        row.update(extra)
    append_spec(row)
    return row


# ---------------- ước lượng nhanh cho bootstrap (FE đơn vị + FE nhóm nhỏ, chính xác theo Frisch–Waugh–Lovell) ----------------
class FastFE:
    """Chuẩn bị một lần: y, X, mã đơn vị, mã nhóm (division×năm), mã cluster (bang). fit(w) trả về β (và SE cluster-bang) với trọng số w.
    Hoán vị khử FE đơn vị bằng trung bình có trọng số, rồi hồi quy trên X và dummy nhóm đã khử trung bình (chính xác)."""

    def __init__(self, d, y, xcols, unit, grp, cluster):
        d = d.dropna(subset=[y] + list(xcols) + [unit, grp, cluster])
        self.n = len(d)
        self.y = d[y].to_numpy(float)
        self.X = d[list(xcols)].to_numpy(float)
        self.u = codes(d[unit]); self.g = codes(d[grp]); self.c = codes(d[cluster])
        self.c_labels = sorted(d[cluster].unique())   # nhãn cụm theo mã (factorize sort=True)
        self.G = int(self.g.max()) + 1
        self.Dg = np.zeros((self.n, self.G - 1))
        m = self.g < self.G - 1
        self.Dg[np.where(m)[0], self.g[m]] = 1.0
        self.k = self.X.shape[1]
        self.C = int(self.c.max()) + 1

    def fit(self, w=None, se=False):
        w = np.ones(self.n) if w is None else w
        U = int(self.u.max()) + 1
        sw = np.bincount(self.u, weights=w, minlength=U)
        sw[sw == 0] = 1.0
        M = np.column_stack([self.y, self.X, self.Dg])
        mu = np.column_stack([np.bincount(self.u, weights=w * M[:, j], minlength=U) / sw for j in range(M.shape[1])])
        Md = M - mu[self.u]
        yd, Z = Md[:, 0], Md[:, 1:]
        A = Z.T @ (Z * w[:, None])
        A = A + np.eye(A.shape[0]) * 1e-10 * float(np.mean(np.diag(A)) + 1e-300)   # ridge cực nhỏ: ổn định khi một nhóm FE có trọng số 0
        b = np.linalg.solve(A, Z.T @ (w * yd))
        beta = b[: self.k]
        if not se:
            return beta
        e = yd - Z @ b
        Xk = Z[:, : self.k]
        # bread cho các cột X sau khi loại dummy nhóm: dùng khối nghịch đảo đầy đủ
        Ainv = np.linalg.inv(A)
        S = np.zeros((self.C, Z.shape[1]))
        np.add.at(S, self.c, Z * (w * e)[:, None])
        V = Ainv @ (S.T @ S) @ Ainv
        return beta, np.sqrt(np.diag(V)[: self.k])


# ---------------- định nghĩa mẫu / biến dùng chung (đăng ký trong kế hoạch) ----------------
RAIN = ["ppt_season_z", "ppt_z2"]
BANK_CTRL = ["log_total_assets_l1", "liquidity_ratio_l1", "loans_to_assets_l1"]
HALVES = {"full": None, "A": "A", "B": "B"}


def county_frame(d, y, years=(2006, 2022)):
    """Mẫu hạt cho họ A, B, E: năm 2006–2022, có y, nhiệt, mưa; FE hạt + division×năm."""
    s = d[d.year.between(*years)].dropna(subset=[y, "heat", "ppt_season_z"]).copy()
    s["div_year"] = s.division + "_" + s.year.astype(str)
    s["state_year"] = s.state + "_" + s.year.astype(str)
    return s


def bank_frame(d, y, h, group="ag25", extra_dropna=(), years=None):
    """Mẫu ngân hàng cho họ C, D, H5, pass-through: nhóm nông nghiệp (ag25 mặc định); t từ 2006 đến 2023 (h ≤ 2) hoặc 2022 (h = 3)."""
    y_max = 2022 if h >= 3 else 2023
    lo, hi = years if years else (2006, y_max)
    s = d[d.year.between(lo, hi)]
    if group:
        s = s[s[group]]
    s = s.dropna(subset=[y, "heat", "ppt_season_z"] + BANK_CTRL + list(extra_dropna)).copy()
    s["div_year"] = s.division + "_" + s.year.astype(str)
    s["state_year"] = s.hq_state + "_" + s.year.astype(str)
    return s


def halves(s):
    """Trả về dict tên cột -> DataFrame con (full, A, B); A/B theo bang trụ sở/hạt."""
    return {"full": s, "A": s[s.half == "A"], "B": s[s.half == "B"]}


def sd_in_sample(s, y):
    return float(s[y].std())


def state_draws(states, B, seed):
    """Ma trận đếm B × S: số lần mỗi bang được rút trong bootstrap theo cụm bang (rút S bang có hoàn lại). Cố định seed.
    Hồi quy có trọng số = số lần rút tương đương hồi quy trên mẫu bootstrap (cụm lặp là các đơn vị độc lập với cùng FE)."""
    rng = np.random.default_rng(seed)
    S = len(states)
    return rng.multinomial(S, np.full(S, 1.0 / S), size=B)
