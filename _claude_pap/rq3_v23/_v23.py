"""_v23.py — PAP v2.3. Lệnh: worker <job ...> | list | collect"""
import sys, os, json, time, glob
sys.path.insert(0, os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v2"))
from _v2_ri import *
import scipy.sparse as sp
V23 = os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v23"); JOBD = f"{V23}/results/jobs"
CHR = os.path.expanduser("~/rq3cache/real"); CH = os.path.join(CACHE, "v23"); os.makedirs(CH, exist_ok=True)
FD = os.path.expanduser("~/mnt/NCKH - NEU/data_external/fdic_api/fdic_uc_smallfarm_2005_2024.parquet")
OUTS.update({"dUCO": ("dUCO", False, []), "dUC": ("dUC", False, []), "dAGP": ("dAGP_q4", False, []), "NCO": ("NCO_h0", False, ["cecl_adopt_year"]),
             "NPL": ("S_npl_total_h0", False, []), "dSMALLN": ("dSMALLN", False, [])})
LINC = ["FS10Cov", "FS10", "Cov"] + Z_INT; BASC = LIN + ["Cov"]

def panel():
    f = f"{CH}/panel_v23.parquet"
    if os.path.exists(f): return pd.read_parquet(f)
    b = pd.read_parquet(os.path.join(CACHE, "v21", "panel_v21.parquet"))
    F = pd.read_parquet(FD); F["year"] = F.REPDTE.str[:4].astype(int); F["md"] = F.REPDTE.str[4:]
    q4 = F[F.md == "1231"][["CERT", "year", "UC", "UCOTHER"]]; q2 = F[F.md == "0630"][["CERT", "year", "LNAG1N"]]
    b["cert_i"] = pd.to_numeric(b.cert, errors="coerce")
    b = b.merge(q4.rename(columns={"CERT": "cert_i"}), on=["cert_i", "year"], how="left")
    b = b.merge(q2.rename(columns={"CERT": "cert_i"}), on=["cert_i", "year"], how="left")
    n1 = q2.copy(); n1["year"] -= 1; b = b.merge(n1.rename(columns={"CERT": "cert_i", "LNAG1N": "LNAG1N_next"}), on=["cert_i", "year"], how="left")
    b = b.sort_values(["idrssd", "year"]).reset_index(drop=True)
    def lag(v):
        x = b.groupby("idrssd")[v].shift(1); yr = b.groupby("idrssd")["year"].shift(1)
        return pd.Series(np.where(yr == b.year - 1, x, np.nan), index=b.index)
    TA1 = lag("total_assets_kusd_p")
    b["dUCO"] = 100 * (b.UCOTHER - lag("UCOTHER")) / TA1; b["dUC"] = 100 * (b.UC - lag("UC")) / TA1
    b["dSMALLN"] = 100 * (np.log1p(b.LNAG1N_next) - np.log1p(b.LNAG1N))
    b["FS10Cov"] = b.FS10 * b.Cov
    b.to_parquet(f, index=False); return b

def jobs():
    J = [dict(id="U1_dUCO", key="dUCO", m="lin"), dict(id="U2_dAGP_cov", key="dAGP", m="cov"), dict(id="CHK")]
    J += [dict(id=f"RI_{c:03d}", chunk=c) for c in range(30)]
    J += [dict(id="S_dUC", key="dUC", m="lin"), dict(id="S_NCO_cov", key="NCO", m="cov"), dict(id="S_NPL_cov", key="NPL", m="cov"),
          dict(id="S_dSMALLN", key="dSMALLN", m="lin"), dict(id="S_dAGP_lin", key="dAGP", m="lin"),
          dict(id="PL_U1", key="dUCO", m="lin", pl=1), dict(id="PL_U2", key="dAGP", m="cov", pl=1)]
    return J

def sample(B, j):
    return frame(B, j["key"], need=["Cov"] if j["m"] == "cov" else [], need_lead="heat_lead1" if j.get("pl") else None)

def run_fit(j, B):
    s = sample(B, j); mults = LINC if j["m"] == "cov" else LIN; bases = BASC if j["m"] == "cov" else None; extra = []
    if j.get("pl"):
        s = s.copy()
        for m in mults: s["L_x_" + m] = s.heat_lead1 * s[m]; extra.append("L_x_" + m)
        extra.append("heat_lead1")
    rows = []
    for se in ("conley", "state"):
        r, xs = fit(s, j["key"], "heat", se=se, level=2, mults=mults, bases=bases, extra=extra)
        for i, nm in enumerate(xs):
            if nm in set(["x_" + m for m in mults] + ["heat"] + extra):
                rows.append(dict(job=j["id"], key=j["key"], se_type=se, coef=nm, beta=float(r["beta"][i]), se=float(r["se"][i]), p=float(r["p"][i]),
                                 n=int(r["n"]), banks=int(r["n_units"]), sd_y=float(r["sd_y"])))
    return dict(rows=rows)

_D = {}
def designs(B):
    if not _D:
        for nm, key, m in (("U1", "dUCO", "lin"), ("U2", "dAGP", "cov")):
            f = f"{CH}/design_{nm}.npz"
            if not os.path.exists(f):
                s = sample(B, dict(key=key, m=m)); Design.build(s, key, 2, mults=LINC if m == "cov" else LIN, bases=BASC if m == "cov" else None).save(f)
            _D[nm] = Design.load(f)
    return _D

def run_ri(j, B):
    D = designs(B); W = sp.load_npz(f"{CHR}/W.npz"); G = np.load(f"{CHR}/G.npy"); yrs = np.load(f"{CHR}/G_years.npy"); sd = float(open(f"{CHR}/sd.txt").read())
    pr = pd.read_parquet(f"{CHR}/panel_run.parquet", columns=["idrssd", "year"]); pr["r"] = np.arange(len(pr))
    mp = B[["idrssd", "year"]].merge(pr, on=["idrssd", "year"], how="left")["r"].to_numpy()
    rng = np.random.default_rng([20261108, j["chunk"]]); out = []
    for _ in range(10):
        pi = draw_pi(rng, range(2006, 2025))
        out.append([float(D[k].beta(perm_heat(W, G, yrs, sd, mp[D[k].rows], D[k].year, pi))[0]) for k in ("U1", "U2")])
    return dict(perm=out)

def worker(ids):
    B = panel()
    for j in jobs():
        if ids and j["id"] not in ids: continue
        fn = f"{JOBD}/{j['id']}.json"
        if os.path.exists(fn): continue
        t0 = time.time()
        if j["id"] == "CHK": D = designs(B); res = dict(chk={k: float(D[k].beta(B.loc[D[k].rows, "heat"].to_numpy())[0]) for k in D})
        elif "chunk" in j: res = run_ri(j, B)
        else: res = run_fit(j, B)
        res["secs"] = time.time() - t0; json.dump(res, open(fn + ".tmp", "w")); os.replace(fn + ".tmp", fn); print(j["id"], round(res["secs"]), flush=True)

def collect():
    rows, P = [], []
    for f in sorted(glob.glob(f"{JOBD}/*.json")):
        d = json.load(open(f)); rows += d.get("rows", []); P += d.get("perm", [])
    S = pd.DataFrame(rows); S.to_csv(f"{V23}/results/specs_run_v23.csv", index=False)
    P = np.array(P); R = len(P); out = []
    for ik, (jid, coef) in enumerate((("U1_dUCO", "x_FS10"), ("U2_dAGP_cov", "x_FS10Cov"))):
        o = S[(S.job == jid) & (S.coef == coef)].set_index("se_type"); b = o.loc["conley", "beta"]; dist = P[:, ik]; sdp = dist.std(ddof=1)
        out.append(dict(test=jid, coef=coef, R=R, beta=b, sd_perm=sdp, p_RI=(1 + (np.abs(dist) >= abs(b)).sum()) / (1 + R), ci90_lo=b - 1.6449 * sdp, ci90_hi=b + 1.6449 * sdp,
                        p_conley=o.loc["conley", "p"], p_state=o.loc["state", "p"], n=o.loc["conley", "n"], sd_y=o.loc["conley", "sd_y"]))
    sdv = np.array([x["sd_perm"] for x in out]); tob = np.abs([x["beta"] for x in out]) / sdv; T = np.abs(P) / sdv; order = np.argsort(-tob); prev = 0
    for r_, i in enumerate(order):
        p_ = (1 + (T[:, order[r_:]].max(axis=1) >= tob[i]).sum()) / (1 + R); prev = max(prev, p_); out[i]["p_WY"] = prev
    O = pd.DataFrame(out); O.to_csv(f"{V23}/results/v23_ri_results.csv", index=False)
    ck = json.load(open(f"{JOBD}/CHK.json"))["chk"]
    print("CHK", abs(ck["U1"] - out[0]["beta"]), abs(ck["U2"] - out[1]["beta"])); pd.set_option("display.width", 220); print(O.round(4).to_string(index=False))
    T2 = S[S.coef.isin(["x_FS10", "x_FS10Cov", "x_Cov", "L_x_FS10", "L_x_FS10Cov"])].pivot_table(index=["job", "coef"], columns="se_type", values=["beta", "p"])
    print(T2.round(4).to_string())

if __name__ == "__main__":
    if sys.argv[1] == "worker": worker(sys.argv[2:])
    elif sys.argv[1] == "collect": collect()
