"""_v24.py — PAP v2.4. Lệnh: build | worker <job ...> | collect"""
import sys, os, json, time, glob
sys.path.insert(0, os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v2"))
from _v2_ri import *
import scipy.sparse as sp
ROOT = os.path.expanduser("~/mnt/NCKH - NEU"); V24 = f"{ROOT}/_claude_pap/rq3_v24"; JOBD = f"{V24}/results/jobs"
CHR = os.path.expanduser("~/rq3cache/real"); CH = os.path.join(CACHE, "v24"); os.makedirs(CH, exist_ok=True)
KEYS = ["NCO", "NPL", "prov|raw", "dALLOW|raw"]
OUTS.update({"NCO": ("NCO_h0", False, ["cecl_adopt_year"]), "NPL": ("S_npl_total_h0", False, []), "dAGP": ("dAGP_q4", False, [])})
MU = ["CROPX", "LIVX", "LIV"] + Z_INT; BA = ["CROPX", "LIVX", "LIV"] + Z_INT

def bea_base():
    L = []
    for f in sorted(glob.glob(f"{ROOT}/_claude_feasibility/external/bea/extracted/CAINC45_[A-Z][A-Z]_1969_2022.csv")):
        d = pd.read_csv(f, encoding="latin1", dtype=str); d["fips"] = d.GeoFIPS.str.strip().str.strip('"'); d["line"] = pd.to_numeric(d.LineCode.str.strip(), errors="coerce")
        d = d[d.line.isin([20, 60]) & ~d.fips.str.endswith("000")]
        v = d[[str(y) for y in range(2001, 2006)]].apply(lambda s: pd.to_numeric(s.str.strip(), errors="coerce"))
        d["base"] = v.mean(axis=1).where(v.notna().all(axis=1)); L.append(d[["fips", "line", "base"]])
    B = pd.concat(L).pivot_table(index="fips", columns="line", values="base").rename(columns={20: "liv", 60: "crop"}).reset_index()
    return B

def build():
    f = f"{CH}/panel_v24.parquet"
    if os.path.exists(f): return pd.read_parquet(f)
    b = pd.read_parquet(os.path.join(CACHE, "v21", "panel_v21.parquet"))
    B = bea_base(); B = B[(B.liv >= 0) & (B.crop >= 0) & ((B.liv + B.crop) > 0)]
    W = pd.read_parquet(f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet", columns=["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"])
    W = W[(W.deposit_weight_l1 > 0) & (W.analysis_year >= 2006)]; W = W.merge(W.groupby("idrssd").analysis_year.min().rename("y0"), on="idrssd"); W = W[W.analysis_year == W.y0]
    m = W.merge(B, left_on="county_fips", right_on="fips", how="inner")
    g = m.groupby("idrssd").apply(lambda d: pd.Series({"LIV": (d.deposit_weight_l1 * d.liv).sum() / (d.deposit_weight_l1 * (d.liv + d.crop)).sum()}), include_groups=False).reset_index()
    g["idrssd"] = g.idrssd.astype(b.idrssd.dtype)
    b = b.merge(g, on="idrssd", how="left"); b["CROPX"] = b.FS10 * (1 - b.LIV); b["LIVX"] = b.FS10 * b.LIV
    b.to_parquet(f, index=False); return b

def jobs():
    J = [dict(id=f"F_{k.replace('|','_')}", key=k) for k in KEYS] + [dict(id="CHK")] + [dict(id=f"RI_{c:03d}", chunk=c) for c in range(30)]
    J += [dict(id=f"S_{k.replace('|','_')}", key=k) for k in ["prov_h1", "dALLOW_h1", "dAGP", "dLIQ", "dALLOW|cond"]]
    J += [dict(id="PL_NCO", key="NCO", pl=1), dict(id="PL_NPL", key="NPL", pl=1)]
    return J

def sample(B, j): return frame(B, j["key"], need=["LIV"], need_lead="heat_lead1" if j.get("pl") else None)

def run_fit(j, B):
    s = sample(B, j); extra = []
    if j.get("pl"):
        s = s.copy()
        for m in MU: s["L_x_" + m] = s.heat_lead1 * s[m]; extra.append("L_x_" + m)
        extra.append("heat_lead1")
    rows = []
    for se in ("conley", "state"):
        r, xs = fit(s, j["key"], "heat", se=se, level=2, mults=MU, bases=BA, extra=extra)
        iC, iL = xs.index("x_CROPX"), xs.index("x_LIVX"); dif = r["beta"][iL] - r["beta"][iC]; sed = float(np.sqrt(r["V"][iL, iL] + r["V"][iC, iC] - 2 * r["V"][iL, iC]))
        rows.append(dict(job=j["id"], key=j["key"], se_type=se, coef="DIFF_L_minus_C", beta=float(dif), se=sed, p=float(2 * (1 - stats.norm.cdf(abs(dif / sed)))), n=int(r["n"]), sd_y=float(r["sd_y"])))
        for i, nm in enumerate(xs):
            if nm in set(["x_" + m for m in MU] + ["heat"] + extra):
                rows.append(dict(job=j["id"], key=j["key"], se_type=se, coef=nm, beta=float(r["beta"][i]), se=float(r["se"][i]), p=float(r["p"][i]), n=int(r["n"]), sd_y=float(r["sd_y"])))
        if j.get("pl"):
            a, c = xs.index("L_x_LIVX"), xs.index("L_x_CROPX"); d2 = r["beta"][a] - r["beta"][c]; s2 = float(np.sqrt(r["V"][a, a] + r["V"][c, c] - 2 * r["V"][a, c]))
            rows.append(dict(job=j["id"], key=j["key"], se_type=se, coef="L_DIFF", beta=float(d2), se=s2, p=float(2 * (1 - stats.norm.cdf(abs(d2 / s2)))), n=int(r["n"]), sd_y=float(r["sd_y"])))
    return dict(rows=rows)

_D = {}
def designs(B):
    if not _D:
        for k in KEYS:
            f = f"{CH}/design_{k.replace('|','_')}.npz"
            if not os.path.exists(f): Design.build(sample(B, dict(key=k)), k, 2, mults=MU, bases=BA).save(f)
            _D[k] = Design.load(f)
    return _D

def run_ri(j, B):
    D = designs(B); W = sp.load_npz(f"{CHR}/W.npz"); G = np.load(f"{CHR}/G.npy"); yrs = np.load(f"{CHR}/G_years.npy"); sd = float(open(f"{CHR}/sd.txt").read())
    pr = pd.read_parquet(f"{CHR}/panel_run.parquet", columns=["idrssd", "year"]); pr["r"] = np.arange(len(pr))
    mp = B[["idrssd", "year"]].merge(pr, on=["idrssd", "year"], how="left")["r"].to_numpy()
    rng = np.random.default_rng([20261109, j["chunk"]]); out = []
    for _ in range(10):
        pi = draw_pi(rng, range(2006, 2025)); row = []
        for k in KEYS:
            bb = D[k].beta(perm_heat(W, G, yrs, sd, mp[D[k].rows], D[k].year, pi)); row.append(float(bb[1] - bb[0]))
        out.append(row)
    return dict(perm=out)

def worker(ids):
    B = build()
    for j in jobs():
        if ids and j["id"] not in ids: continue
        fn = f"{JOBD}/{j['id']}.json"
        if os.path.exists(fn): continue
        t0 = time.time()
        if j["id"] == "CHK": D = designs(B); res = dict(chk={k: (lambda bb: float(bb[1] - bb[0]))(D[k].beta(B.loc[D[k].rows, "heat"].to_numpy())) for k in KEYS})
        elif "chunk" in j: res = run_ri(j, B)
        else: res = run_fit(j, B)
        res["secs"] = time.time() - t0; json.dump(res, open(fn + ".tmp", "w")); os.replace(fn + ".tmp", fn); print(j["id"], round(res["secs"]), flush=True)

def collect():
    rows, P = [], []
    for f in sorted(glob.glob(f"{JOBD}/*.json")):
        d = json.load(open(f)); rows += d.get("rows", []); P += d.get("perm", [])
    S = pd.DataFrame(rows); S.to_csv(f"{V24}/results/specs_run_v24.csv", index=False); P = np.array(P); R = len(P); out = []
    ck = json.load(open(f"{JOBD}/CHK.json"))["chk"]
    for ik, k in enumerate(KEYS):
        o = S[(S.job == f"F_{k.replace('|','_')}") & (S.coef == "DIFF_L_minus_C")].set_index("se_type"); b = o.loc["conley", "beta"]; dist = P[:, ik]; sdp = dist.std(ddof=1)
        out.append(dict(key=k, diff=b, chk=abs(ck[k] - b), sd_perm=sdp, p_RI=(1 + (np.abs(dist) >= abs(b)).sum()) / (1 + R), ci90_lo=b - 1.6449 * sdp, ci90_hi=b + 1.6449 * sdp,
                        p_conley=o.loc["conley", "p"], p_state=o.loc["state", "p"], n=o.loc["conley", "n"], sd_y=o.loc["conley", "sd_y"], R=R))
    sdv = np.array([x["sd_perm"] for x in out]); tob = np.abs([x["diff"] for x in out]) / sdv; T = np.abs(P) / sdv; order = np.argsort(-tob); prev = 0
    for r_, i in enumerate(order):
        p_ = (1 + (T[:, order[r_:]].max(axis=1) >= tob[i]).sum()) / (1 + R); prev = max(prev, p_); out[i]["p_WY"] = prev
    O = pd.DataFrame(out); O.to_csv(f"{V24}/results/v24_ri_results.csv", index=False); pd.set_option("display.width", 230); print(O.round(4).to_string(index=False))
    T2 = S[S.coef.isin(["DIFF_L_minus_C", "x_CROPX", "x_LIVX", "x_LIV", "L_DIFF"])].pivot_table(index=["job", "coef"], columns="se_type", values=["beta", "p"]); print(T2.round(4).to_string())

if __name__ == "__main__":
    if sys.argv[1] == "build": b = build(); u = b.drop_duplicates("idrssd"); print(u.LIV.describe().round(3).to_dict(), "corr FS", u[["LIV", "farmshare_pre"]].corr().iloc[0, 1].round(3))
    elif sys.argv[1] == "worker": worker(sys.argv[2:])
    elif sys.argv[1] == "collect": collect()
