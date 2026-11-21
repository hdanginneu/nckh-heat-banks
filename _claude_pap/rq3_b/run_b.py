"""run_b.py — phân tích bổ sung B1–B4 theo RULES_B1_B4.md (quy tắc chốt trước khi chạy thật).
Lệnh:  python3 run_b.py b3      [--fake SEED]          B3: xu hướng của nhiệt (không dùng outcome)
       python3 run_b.py est     [--fake SEED] [--R n]  B1, B2, B2o, B4 (và B3b nếu B3 kích hoạt); mỗi hồi quy một json, chạy tiếp được
       python3 run_b.py collect [--fake SEED]          tổng hợp → b_results.csv, in bảng
Dữ liệu thật chỉ chạy khi hash của RULES_B1_B4.md và run_b.py khớp hashes_frozen_b.json (freeze_b.py) và PAP v3 còn nguyên (guard_real).
--fake SEED: outcome hoán vị trong năm × ag25 (kiểm code, không diễn giải). Cùng dãy π của PAP v3."""
import os, sys, json, glob, time, hashlib
BD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BD, "..", "rq3_v3"))
from _v3_spec import *                                    # noqa: F401,F403  (np, pd, CONFIG, FAMILY, thetas, sample, winsor, V3Design, ...)
import _v3_spec as V
import scipy.sparse as sp
from scipy import stats as sst
from _v2_ri import build_W, perm_heat, draw_pi

A = sys.argv[1:]
FAKE = int(A[A.index("--fake") + 1]) if "--fake" in A else None
R = int(A[A.index("--R") + 1]) if "--R" in A else (CONFIG["R"] if FAKE is None else 20)
TAG = "real" if FAKE is None else f"fake_s{FAKE}"
OUT = f"{BD}/results_{TAG}"; JOBD = f"{OUT}/jobs"; os.makedirs(JOBD, exist_ok=True)
YEARS_PI = range(2006, 2025)
DROP_B4 = (2008, 2009)
FROZEN = ["RULES_B1_B4.md", "run_b.py"]


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def guard_b():
    V.guard_real()
    hf = f"{BD}/hashes_frozen_b.json"
    assert os.path.exists(hf), "Chưa đóng băng B (chạy freeze_b.py)."
    H = json.load(open(hf)); bad = [k for k in FROZEN if H.get(k) != sha(f"{BD}/{k}")]
    assert not bad, f"Hash không khớp: {bad}"


# ---------------------------------------------------------------- dữ liệu
_C = {}
def panel():
    if "B" in _C: return _C["B"]
    B = load_panel(FAKE is not None, FAKE or 0, 0.0)
    ag = pd.read_parquet(PANEL, columns=["idrssd", "year", "NCOag_h6"])          # NCOag không thuộc OUTVARS của v3: nạp riêng
    assert (ag.idrssd.to_numpy() == B.idrssd.to_numpy()).all() and (ag.year.to_numpy() == B.year.to_numpy()).all()
    B["NCOag_h6"] = ag.NCOag_h6.to_numpy()
    if FAKE is not None:                                  # hoán vị NCOag_h6 như outcome khác (seed riêng)
        rng = np.random.default_rng(5300 + FAKE)
        for _, g in B.groupby(["year", "ag25"]).groups.items():
            g = np.asarray(g); B.loc[g, "NCOag_h6"] = B.loc[rng.permutation(g), "NCOag_h6"].to_numpy()
    W, G, yrs, sd = build_W(B)
    cty = np.sort(pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips"]).county_fips.unique())
    pos = {int(c): i for i, c in enumerate(cty)}                                   # thứ tự cột của G (build_W) = thứ tự cty
    hq = pd.to_numeric(B.hq_county_fips_l1, errors="coerce").to_numpy()
    ci = np.array([pos.get(int(v), -1) if np.isfinite(v) else -1 for v in hq]); ok = ci >= 0; ci = np.where(ok, ci, 0)
    r = np.where(ok)[0]
    Whq = sp.csr_matrix((np.ones(len(r)), (r, ci[r])), shape=(len(B), len(cty)))
    t = B.year.to_numpy(); tt = np.clip(t, yrs[0], yrs[-1]) - yrs[0]
    ghq = np.where(ok, G[ci, tt], np.nan)
    B["heat_hq"] = np.where(np.isfinite(ghq), ghq / sd, np.nan)
    B["hq_ok"] = np.isfinite(B.heat_hq.to_numpy())
    _C.update(B=B, W=W, G=G, yrs=yrs, sd=sd, Whq=Whq, cty=cty)
    return B


def detrended_G():
    """B3b: gdd_ex29 cấp hạt khử xu hướng tuyến tính riêng từng hạt trên 2006–2024, cộng lại trung bình hạt."""
    if "Gdt" in _C: return _C["Gdt"]
    G, yrs = _C["G"], _C["yrs"]; Gd = G.copy()
    j = np.where((yrs >= 2006) & (yrs <= 2024))[0]; x = yrs[j] - yrs[j].mean()
    Y = G[:, j]; okr = np.isfinite(Y).all(axis=1)
    b = (Y[okr] - Y[okr].mean(axis=1, keepdims=True)) @ x / (x @ x)
    Gd[np.ix_(np.where(okr)[0], j)] = Y[okr] - b[:, None] * x[None, :]
    _C["Gdt"] = Gd; return Gd


# ---------------------------------------------------------------- danh sách hồi quy
def main_thetas():
    T = [th for th in thetas() if th["grp"] == "main"]
    T.append(dict(name="C1_ag", C="C1", var="NCOag", grp="b1", opts={}, hs=[6], w=[1.0], common=False))
    return {th["name"]: th for th in T}

def variants(b3b=False):
    """(khối, θ, nguồn nhiệt, mặt nạ dòng, năm bỏ, có hoán vị)"""
    T = main_thetas(); L = []
    for C in FAMILY: L.append(("MAIN", T[C], "dep", None, (), False))          # kiểm: tái lập θ chính
    L.append(("B1", T["C1_ag"], "dep", None, (), True))
    L.append(("B1o", T["C1"], "dep", "ag_ok", (), True))
    for C in FAMILY:
        L.append(("B2", T[C], "hq", "hq_ok", (), True))
        L.append(("B2o", T[C], "dep", "hq_ok", (), True))
        L.append(("B4", T[C], "dep", None, DROP_B4, True))
        if b3b: L.append(("B3b", T[C], "dt", None, (), True))
    return L

def jobs(b3b=False):
    J = []
    for blk, th, src, mask, drop, perm in variants(b3b):
        for h in th["hs"]: J.append(dict(id=f"{blk}_{th['name']}_h{h}", blk=blk, th=th["name"], h=h, src=src, mask=mask, drop=list(drop), perm=perm))
    return J

_ROWS = {}
def frame(B, th, h, mask, drop):
    y = f"{th['var']}_h{h}"; rows = None
    if th["common"] and len(th["hs"]) > 1:
        k = (th["name"], mask, tuple(drop))
        if k not in _ROWS: _ROWS[k] = V.common_rows(B, th)
        rows = _ROWS[k]
    s = V.sample(B, th["C"], y, h, rows=rows, opts=th["opts"])
    if drop: s = s[~s.year.isin(drop)]
    if mask == "hq_ok": s = s[s.hq_ok]
    if mask == "ag_ok": s = s[B.loc[s.index, "NCOag_h6"].notna()]
    return winsor(s.copy(), [y], CONFIG["WINSOR"]), y


_PIS = []
def all_pis():
    if not _PIS:
        c = 0
        while len(_PIS) < R:
            rng = np.random.default_rng([CONFIG["SEED_V3"], c]); _PIS.extend(draw_pi(rng, YEARS_PI) for _ in range(CONFIG["NPERM"])); c += 1
    return _PIS[:R]

def heat_of(src, rows, years, pi):
    W = _C["Whq"] if src == "hq" else _C["W"]; G = detrended_G() if src == "dt" else _C["G"]
    return perm_heat(W, G, _C["yrs"], _C["sd"], rows, years, pi)

def run_job(j):
    B = panel(); th = main_thetas()[j["th"]]
    s, y = frame(B, th, j["h"], j["mask"], j["drop"]); D = V3Design(s, y)
    ident = {t: t for t in YEARS_PI}
    hobs = B.loc[D.rows, "heat"].to_numpy() if j["src"] == "dep" else heat_of(j["src"], D.rows, D.year, ident)
    chk = float(np.max(np.abs(heat_of("dep", D.rows, D.year, ident) - B.loc[D.rows, "heat"].to_numpy())))
    obs, rss0 = D.beta_rss(hobs)
    out = dict(id=j["id"], obs=float(obs[0]), obs_rss=rss0, n=len(s), banks=int(s.idrssd.nunique()), shock_years=int(s.year.nunique()),
               sd_y=float(s[y].std()), ybar=float(s[y].mean()), max_abs_heat_rebuild=chk,
               corr_heat=float(np.corrcoef(hobs, B.loc[D.rows, "heat"].to_numpy())[0, 1]), sd_heat=float(np.std(hobs)))
    if j["perm"]:
        perm, prss = [], []
        for pi in all_pis():
            b_, r_ = D.beta_rss(heat_of(j["src"], D.rows, D.year, pi)); perm.append(float(b_[0])); prss.append(r_)
        out.update(perm=perm, perm_rss=prss)
    return out


# ---------------------------------------------------------------- thống kê (chép từ run_v3.stat_row / kappa_of / mde_ri)
def mde_ri(dist):
    a, bb = np.abs(dist[0::2]), dist[1::2]
    if len(a) < 20 or len(bb) < 20: return np.nan
    c = np.quantile(a, .95); s = dist.std(ddof=1)
    for k in np.arange(0, 6.001, .01):
        if (np.abs(k * s + bb) >= c).mean() >= .8 and (np.abs(-k * s + bb) >= c).mean() >= .8: return k * s
    return np.nan

def kappa_of(x): return float(np.sqrt(np.median(x["perm_rss"]) / x["obs_rss"])) if "perm_rss" in x else 1.0

def stat_row(name, obs, ts, kappa=1.0):
    sdp = ts.std(ddof=1); q05, q95 = np.quantile(ts, [.05, .95]); k = max(1.0, kappa); sda = sdp * k
    return dict(name=name, theta=obs, R=len(ts), sd_perm=sdp, kappa=kappa, sd_adj=sda, p_RI=(1 + (np.abs(ts) >= abs(obs)).sum()) / (1 + len(ts)),
                ci90_lo=obs - 1.6449 * sda, ci90_hi=obs + 1.6449 * sda, mde80_ri=k * mde_ri(ts))

def wy(names, obs, TS, sds):
    tobs = np.abs(np.array(obs)) / np.array(sds); T = np.column_stack([np.abs(TS[n]) / s for n, s in zip(names, sds)])
    order = np.argsort(-tobs); padj = np.zeros(len(names)); prev = 0.0
    for k, i in enumerate(order):
        p_ = (1 + (T[:, order[k:]].max(axis=1) >= tobs[i]).sum()) / (1 + T.shape[0]); prev = max(prev, p_); padj[i] = prev
    return padj


# ---------------------------------------------------------------- lệnh
def cmd_b3():
    B = panel(); s = B[B.year.between(2006, 2024) & B.heat.notna()]
    rng = np.random.default_rng(20261121); NP = 20000
    def trend(m):
        x = m.index.to_numpy(float); y = m.to_numpy(float); lr = sst.linregress(x, y)
        P = np.array([sst.linregress(x, rng.permutation(y)).slope for _ in range(NP)])
        return dict(slope_sd_per_yr=float(lr.slope), p_ols=float(lr.pvalue), p_perm=float((1 + (np.abs(P) >= abs(lr.slope)).sum()) / (1 + NP)),
                    spearman=float(sst.spearmanr(x, y)[0]), ar1=float(np.corrcoef(y[:-1], y[1:])[0, 1]), n_years=len(y),
                    change_over_period_sd=float(lr.slope * (x.max() - x.min())))
    res = dict(national=trend(s.groupby("year").heat.mean()), division={})
    for d, g in s.groupby("division"): res["division"][d] = trend(g.groupby("year").heat.mean())
    dn = list(res["division"]); ps = np.array([res["division"][d]["p_perm"] for d in dn]); o = np.argsort(ps); m = len(ps); adj = np.zeros(m); prev = 0
    for k, i in enumerate(o): prev = max(prev, min(1.0, (m - k) * ps[i])); adj[i] = prev
    for d, a in zip(dn, adj): res["division"][d]["p_holm"] = float(a)
    res["trigger_B3b"] = bool(res["national"]["p_perm"] < .10 or (adj < .10).any())
    json.dump(res, open(f"{OUT}/b3_trend.json", "w"), indent=1); print(json.dumps(res, indent=1))

def b3b_on():
    f = f"{OUT}/b3_trend.json"
    assert os.path.exists(f), "Chạy b3 trước est."
    return json.load(open(f))["trigger_B3b"]

def cmd_est():
    t0 = time.time(); J = jobs(b3b_on()); done = 0
    for j in J:
        fn = f"{JOBD}/{j['id']}.json"
        if os.path.exists(fn): continue
        t1 = time.time(); res = run_job(j); res["secs"] = time.time() - t1
        json.dump(res, open(fn + ".tmp", "w")); os.replace(fn + ".tmp", fn); done += 1
        print(f"{j['id']}: θ_h={res['obs']:.5f} n={res['n']} ({res['secs']:.0f}s)", flush=True)
    print(f"est: xong {done}/{len(J)} job, {time.time() - t0:.0f}s")

def cmd_collect():
    T = main_thetas(); X = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f"{JOBD}/*.json")}
    rows, TS = [], {}
    blocks = sorted({j["blk"] for j in jobs(b3b_on())})
    for blk in blocks:
        for name, th in T.items():
            ids = [f"{blk}_{name}_h{h}" for h in th["hs"]]
            if not all(i in X for i in ids): continue
            x0 = X[ids[0]]; obs = sum(w * X[i]["obs"] for w, i in zip(th["w"], ids))
            r = dict(blk=blk, name=name, theta=obs, n=x0["n"], banks=x0["banks"], shock_years=x0["shock_years"], ybar=x0["ybar"],
                     corr_heat=x0["corr_heat"], sd_heat=x0["sd_heat"], max_abs_heat_rebuild=max(X[i]["max_abs_heat_rebuild"] for i in ids))
            if "perm" in x0:
                ts = sum(w * np.array(X[i]["perm"]) for w, i in zip(th["w"], ids)); TS[(blk, name)] = ts
                r.update(stat_row(name, obs, ts, kappa_of(x0))); r["blk"] = blk
            dl = SESOI.get(name, {}).get("primary") if name in FAMILY else None
            if name == "C1_ag":
                o = [i for i in X if i.startswith("B1o_C1_h")]
                dl = SESOI["C1"]["primary"] * x0["ybar"] / X[o[0]]["ybar"] if o else None
            r["delta"] = dl
            if dl and "ci90_lo" in r: r["tost"] = bool(r["ci90_lo"] > -dl and r["ci90_hi"] < dl)
            rows.append(r)
    O = pd.DataFrame(rows)
    for blk in ("B2", "B2o", "B4", "B3b"):
        m = (O.blk == blk) & O.name.isin(FAMILY) if len(O) else []
        if len(O) and m.sum() == len(FAMILY):
            sub = O[m]; O.loc[m, "p_WY"] = wy(list(sub.name), list(sub.theta), {n: TS[(blk, n)] for n in sub.name}, list(sub.sd_perm))
            O.loc[m, "status"] = [("+" if r.theta > 0 else "-") if r.p_WY < .05 else ("0" if r.tost else "?") for r in O[m].itertuples()]
    v3 = pd.read_csv(os.path.join(BD, "..", "rq3_v3", "results_real" if FAKE is None else f"results_fake_s{FAKE}", "v3_confirmatory.csv")) \
        if os.path.exists(os.path.join(BD, "..", "rq3_v3", "results_real" if FAKE is None else f"results_fake_s{FAKE}", "v3_confirmatory.csv")) else None
    if v3 is not None and len(O):
        mm = O.blk == "MAIN"; O.loc[mm, "theta_v3"] = O.loc[mm, "name"].map(v3.set_index("name").theta)
        O.loc[mm, "dev_vs_v3"] = (O.loc[mm, "theta"] - O.loc[mm, "theta_v3"]).abs()
    O.to_csv(f"{OUT}/b_results.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    cols = [c for c in ["blk", "name", "theta", "sd_perm", "kappa", "p_RI", "p_WY", "ci90_lo", "ci90_hi", "delta", "tost", "status", "n", "banks",
                        "shock_years", "corr_heat", "sd_heat", "max_abs_heat_rebuild", "dev_vs_v3"] if c in O]
    print(O[cols].round(5).to_string(index=False))


if __name__ == "__main__":
    if FAKE is None: guard_b()
    c = A[0]
    {"b3": cmd_b3, "est": cmd_est, "collect": cmd_collect}[c]()
