"""_v21.py — PAP v2.1 (cung/cầu tín dụng). Dựng biến và định nghĩa job. Dùng nguyên đặc tả V2 + RI của PAP v2 (import, không sửa)."""
import sys, os, json, time, glob
sys.path.insert(0, os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v2"))
from _v2_ri import *
import scipy.sparse as sp
V21 = os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v21")
DRY = os.environ.get("DRYRUN", "0") == "1"
CHR = os.path.expanduser("~/rq3cache/real")                     # cache của PAP v2 (panel_run, W, G)
CH = os.path.join(CACHE, "v21dry" if DRY else "v21"); os.makedirs(CH, exist_ok=True)
RESD = f"{V21}/{'results_dry' if DRY else 'results'}"; JOBD = f"{RESD}/jobs"; os.makedirs(JOBD, exist_ok=True)

OUTS.update({
    "dYLD":     ("dYLD_h0", False, []),        # M1 giá: Δ lãi suất cho vay ngầm định (điểm %)
    "dLOAN":    ("dLOAN_q4", False, []),       # M2 lượng: Δ dư nợ / tổng tài sản t−1 (điểm %)
    "dAGP":     ("dAGP_q4", False, []),
})
for q in (1, 2, 3, 4):
    OUTS[f"dLOAN_q{q}"] = (f"dLOAN_q{q}", False, []); OUTS[f"dAGP_q{q}"] = (f"dAGP_q{q}", False, [])
LIN_CAP = ["FS10CAP", "FS10", "CAP"] + Z_INT
BASES_CAP = LIN + ["CAP"]

def build_panel():
    f = f"{CH}/panel_v21.parquet"
    if os.path.exists(f): return pd.read_parquet(f)
    b = pd.read_parquet(f"{CHR}/panel_run.parquet")
    if DRY:   # nhiệt hoán vị cố định (giống DRYRUN của v2)
        W = sp.load_npz(f"{CHR}/W.npz"); G = np.load(f"{CHR}/G.npy"); yrs = np.load(f"{CHR}/G_years.npy"); sd = float(open(f"{CHR}/sd.txt").read())
        pi0 = draw_pi(np.random.default_rng(999), range(2006, 2025)); b["heat"] = perm_heat(W, G, yrs, sd, np.arange(len(b)), b.year.to_numpy(), pi0)
    cols = ["idrssd", "year", "loan_interest_fees_ytd_kusd", "annual_avg_loans_and_leases_kusd", "q4_total_loans_kusd", "q4_ag_production_loans_kusd"] + \
           [f"q{q}_{c}" for q in (1, 2, 3) for c in ("total_loans_kusd", "ag_production_loans_kusd")]
    p = pd.read_parquet(P1, columns=cols).drop_duplicates(["idrssd", "year"])
    b = b.merge(p, on=["idrssd", "year"], how="left").sort_values(["idrssd", "year"]).reset_index(drop=True)
    def lag(v):
        x = b.groupby("idrssd")[v].shift(1); yr = b.groupby("idrssd")["year"].shift(1)
        return pd.Series(np.where(yr == b.year - 1, x, np.nan), index=b.index)
    yld = 100 * b.loan_interest_fees_ytd_kusd / b.annual_avg_loans_and_leases_kusd
    yld = yld.where(b.annual_avg_loans_and_leases_kusd > 0)
    b["YLD"] = yld; b["dYLD_h0"] = yld - lag("YLD")
    TA1 = lag("total_assets_kusd_p")
    L4m1, A4m1 = lag("q4_total_loans_kusd"), lag("q4_ag_production_loans_kusd")
    for q in (1, 2, 3, 4):
        b[f"dLOAN_q{q}"] = 100 * (b[f"q{q}_total_loans_kusd"] - L4m1) / TA1
        b[f"dAGP_q{q}"] = 100 * (b[f"q{q}_ag_production_loans_kusd"] - A4m1) / TA1
    u = b.drop_duplicates("idrssd").cap_pre
    lo, hi = u.quantile([.01, .99]); c = b.cap_pre.clip(lo, hi); uc = u.clip(lo, hi)
    b["CAP"] = (c - uc.mean()) / uc.std()
    b["FS10CAP"] = b.FS10 * b.CAP
    b.to_parquet(f, index=False)
    return b

def jobs():
    J = [dict(id="M1_dYLD", kind="fit", key="dYLD", mults="lin"),
         dict(id="M2_dLOAN_cap", kind="fit", key="dLOAN", mults="cap"),
         dict(id="CHK", kind="chk")]
    J += [dict(id=f"RI_{c:03d}", kind="ri", chunk=c) for c in range(2 if DRY else 30)]
    for q in (1, 2, 3, 4):
        J.append(dict(id=f"M3_dLOAN_q{q}", kind="fit", key=f"dLOAN_q{q}", mults="lin"))
        J.append(dict(id=f"M3_dAGP_q{q}", kind="fit", key=f"dAGP_q{q}", mults="lin"))
    J += [dict(id="S_dAGP_cap", kind="fit", key="dAGP", mults="cap"),
          dict(id="S_dYLD_L0", kind="fit", key="dYLD", mults="lin", level=0),
          dict(id="S_dYLD_PL", kind="fit", key="dYLD", mults="lin", placebo=True),
          dict(id="S_dLOAN_cap_PL", kind="fit", key="dLOAN", mults="cap", placebo=True)]
    return J

def sample(B, j):
    need = ["CAP"] if j.get("mults") == "cap" else []
    s = frame(B, j["key"], need=need, need_lead="heat_lead1" if j.get("placebo") else None)
    return s

def run_fit(j, B):
    s = sample(B, j); mk = j.get("mults", "lin")
    mults = LIN_CAP if mk == "cap" else LIN; bases = BASES_CAP if mk == "cap" else None; extra = []
    if j.get("placebo"):
        s = s.copy()
        for m in mults: s["L_x_" + m] = s["heat_lead1"] * s[m]; extra.append("L_x_" + m)
        extra.append("heat_lead1")
    rows = []
    for se in ("conley", "state"):
        r, xs = fit(s, j["key"], "heat", se=se, level=j.get("level", 2), mults=mults, bases=bases, extra=extra)
        keep = set(["x_" + m for m in mults] + ["heat"] + extra)
        for i, nm in enumerate(xs):
            if nm in keep:
                rows.append(dict(job=j["id"], key=j["key"], se_type=se, coef=nm, beta=float(r["beta"][i]), se=float(r["se"][i]), p=float(r["p"][i]),
                                 n=int(r["n"]), banks=int(r["n_units"]), sd_y=float(r["sd_y"])))
    return dict(rows=rows)

_D = {}
def designs(B):
    if not _D:
        for nm, key, mk in (("M1", "dYLD", "lin"), ("M2", "dLOAN", "cap")):
            f = f"{CH}/design_{nm}.npz"
            if not os.path.exists(f):
                j = dict(key=key, mults=mk); s = sample(B, j)
                Design.build(s, key, 2, mults=LIN_CAP if mk == "cap" else LIN, bases=BASES_CAP if mk == "cap" else None).save(f)
            _D[nm] = Design.load(f)
    return _D

def run_ri(j, B):
    D = designs(B); W = sp.load_npz(f"{CHR}/W.npz"); G = np.load(f"{CHR}/G.npy"); yrs = np.load(f"{CHR}/G_years.npy"); sd = float(open(f"{CHR}/sd.txt").read())
    # hàng của panel_v21 ↔ hàng của W (panel_run): ánh xạ theo (idrssd, year)
    pr = pd.read_parquet(f"{CHR}/panel_run.parquet", columns=["idrssd", "year"]); pr["r"] = np.arange(len(pr))
    mp = B[["idrssd", "year"]].merge(pr, on=["idrssd", "year"], how="left")["r"].to_numpy()
    rng = np.random.default_rng([20261107, j["chunk"]]); out = []
    for _ in range(10):
        pi = draw_pi(rng, range(2006, 2025))
        out.append([D[k].beta(perm_heat(W, G, yrs, sd, mp[D[k].rows], D[k].year, pi)).tolist() for k in ("M1", "M2")])
    return dict(perm=out)

def run_chk(B):
    D = designs(B); return dict(chk={k: D[k].beta(B.loc[D[k].rows, "heat"].to_numpy()).tolist() for k in ("M1", "M2")})

def worker(names):
    B = build_panel()
    for j in jobs():
        if names and j["id"] not in names: continue
        fn = f"{JOBD}/{j['id']}.json"
        if os.path.exists(fn): continue
        t0 = time.time()
        res = run_ri(j, B) if j["kind"] == "ri" else (run_chk(B) if j["kind"] == "chk" else run_fit(j, B))
        res["secs"] = time.time() - t0; json.dump(res, open(fn + ".tmp", "w")); os.replace(fn + ".tmp", fn); print(j["id"], round(res["secs"]), "s", flush=True)

def collect():
    rows = []; P = []
    for f in sorted(glob.glob(f"{JOBD}/*.json")):
        d = json.load(open(f))
        if "rows" in d: rows += d["rows"]
        if "perm" in d: P.append(np.array([[r[0][0], r[1][0]] for r in d["perm"]]))   # chỉ hệ số mục tiêu (cột 0) của M1, M2
    S = pd.DataFrame(rows); S.to_csv(f"{RESD}/specs_run_v21.csv", index=False)
    out = []
    if P:
        P = np.concatenate(P); R = len(P)
        for ik, (jid, coef, ci) in enumerate((("M1_dYLD", "x_FS10", 0), ("M2_dLOAN_cap", "x_FS10CAP", 0))):
            o = S[(S.job == jid) & (S.coef == coef)].set_index("se_type")
            dist = P[:, ik]; sdp = dist.std(ddof=1); b = o.loc["conley", "beta"]
            out.append(dict(test=jid, coef=coef, R=R, beta=b, sd_perm=sdp, p_RI=(1 + (np.abs(dist) >= abs(b)).sum()) / (1 + R),
                            ci90_lo=b - 1.6449 * sdp, ci90_hi=b + 1.6449 * sdp, se_conley=o.loc["conley", "se"], p_conley=o.loc["conley", "p"],
                            se_state=o.loc["state", "se"], p_state=o.loc["state", "p"], n=o.loc["conley", "n"], sd_y=o.loc["conley", "sd_y"]))
        sdv = np.array([x["sd_perm"] for x in out]); tobs = np.abs([x["beta"] for x in out]) / sdv; T = np.abs(P) / sdv
        order = np.argsort(-tobs); prev = 0
        for r_, idx in enumerate(order):
            p_ = (1 + (T[:, order[r_:]].max(axis=1) >= tobs[idx]).sum()) / (1 + R); prev = max(prev, p_); out[idx]["p_RI_WY"] = prev
    O = pd.DataFrame(out)
    if len(O):
        O["sesoi"] = np.where(O.test == "M1_dYLD", 0.10 / 2.5, np.nan)
        O["tost_pass"] = (O.ci90_lo > -O.sesoi) & (O.ci90_hi < O.sesoi)
    O.to_csv(f"{RESD}/v21_ri_results.csv", index=False)
    ck = f"{JOBD}/CHK.json"
    if os.path.exists(ck) and len(S):
        c = json.load(open(ck))["chk"]
        a1 = S[(S.job == "M1_dYLD") & (S.coef == "x_FS10") & (S.se_type == "conley")].beta.iloc[0]
        a2 = S[(S.job == "M2_dLOAN_cap") & (S.coef == "x_FS10CAP") & (S.se_type == "conley")].beta.iloc[0]
        print("CHK max diff", max(abs(c["M1"][0] - a1), abs(c["M2"][0] - a2)))
    pd.set_option("display.width", 250); print(O.round(5).to_string(index=False))
    return S, O

if __name__ == "__main__":
    import glob
    if sys.argv[1] == "worker": worker(sys.argv[2:])
    elif sys.argv[1] == "list": print([j["id"] for j in jobs()])
    elif sys.argv[1] == "collect": collect()
