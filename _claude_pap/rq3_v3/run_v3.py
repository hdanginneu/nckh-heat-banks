"""run_v3.py — chạy RQ3 v3 theo PAP_v3_formulas.md (Thịnh). Lệnh: prep | list | worker <w> <nw> <budget_s> [tiền tố] | collect | check
PAP_FAKE=1 : outcome v3 hoán vị trong từng năm × ag25 (kiểm code, không diễn giải). FAKE_SEED, FAKE_BETA, R_FAKE tuỳ chọn.
Không có PAP_FAKE=1: chỉ chạy khi PAP v3 đã đóng băng (guard_real). Mọi job liệt kê đều chạy và đều được ghi; không chọn theo kết quả."""
import os, sys, time, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _v3_spec import *                                    # noqa: F401,F403
import scipy.sparse as sp
from _v2_ri import build_W, perm_heat, draw_pi, CACHE
from _pap_common import TAB

FAKE = os.environ.get("PAP_FAKE", "0") == "1"
FSEED = int(os.environ.get("FAKE_SEED", "0")); FBETA = float(os.environ.get("FAKE_BETA", "0"))
if not FAKE: guard_real()
TAG = f"fake_s{FSEED}" + (f"_b{FBETA:g}" if FBETA else "") if FAKE else "real"
R = int(os.environ.get("R_FAKE", "20")) if FAKE else CONFIG["R"]
NCH = max(1, R // CONFIG["NPERM"])
RESD = f"{HERE}/results_{TAG}"; JOBD = f"{RESD}/jobs"; os.makedirs(JOBD, exist_ok=True)
CH = os.path.join(CACHE, f"v3_{TAG}"); os.makedirs(CH, exist_ok=True)
YEARS_PI = range(2006, 2025)


def designs():
    """Danh sách thiết kế: (id, C, cột y, h, loại mẫu, t0). LP_* mẫu riêng từng h; TH_* mẫu chung của θ; PL_* placebo; EX_* attrition."""
    D = []
    for C in FAMILY:
        v = CONFIG["VAR"][C]
        for h in range(7):
            if t_last(C, h) >= CONFIG["T_FIRST"]: D.append((f"LP_{C}_{h}", C, f"{v}_h{h}", h, "own", None))
        if THETA[C]["common"]:
            for h in THETA[C]["hs"](): D.append((f"TH_{C}_{h}", C, f"{v}_h{h}", h, "common", None))
    for C in ("C1", "C2", "C3"):
        for m in (2, 3): D.append((f"PL_{C}_m{m}", C, f"PRE_{CONFIG['VAR'][C]}_m{m}", 0, "own", 2005 + m))
    for h in range(1, 7): D.append((f"EX_{h}", "C1", f"EXIT_h{h}", h, "own", None))
    return D


def frame_of(B, d):
    did, C, y, h, kind, t0 = d
    rows = theta_rows(B, C) if kind == "common" else None
    return make_frame(B, C, y, h, rows=rows, t0=t0)


def jobs():
    J = [dict(id=f"F_{d[0]}", kind="fit", d=d) for d in designs()]
    J.append(dict(id="CHK", kind="chk"))
    for i, d in enumerate(designs()):
        for blk in range(0, NCH, 10):
            J.append(dict(id=f"RI_{d[0]}_{blk:03d}", kind="ri", did=d[0], d=d, chunks=list(range(blk, min(blk + 10, NCH))), di=i))
    return J


def cmd_prep(budget=1e9):
    t0 = time.time()
    B = load_panel(FAKE, FSEED, FBETA)
    W, G, yrs, sd = build_W(B)
    sp.save_npz(f"{CH}/W.npz", W); np.save(f"{CH}/G.npy", G); np.save(f"{CH}/G_years.npy", yrs); open(f"{CH}/sd.txt", "w").write(str(sd))
    if CONFIG["RI_DROUGHT"] == "joint":
        h = pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips"]); cty = np.sort(h.county_fips.unique())
        dr = pd.read_parquet(f"{ROOT}/data_external/usdm/county_year_drought.parquet")
        Gd = dr.pivot(index="county_fips", columns="year", values="dr_d2_wk").reindex(index=cty, columns=yrs).fillna(0).to_numpy()
        np.save(f"{CH}/Gd.npy", Gd)
    meta = []
    for d in designs():
        sm = frame_of(B, d)
        meta.append(dict(id=d[0], C=d[1], y=d[2], h=d[3], kind=d[4], n=len(sm), banks=sm.idrssd.nunique(), years=sm.year.nunique()))
    pd.DataFrame(meta).to_csv(f"{RESD}/designs.csv", index=False)
    print("prep:", len(meta), "thiết kế; R =", R, "| cache", CH, f"| {time.time() - t0:.0f}s")


def run_fit(j, B):
    d = j["d"]; s = frame_of(B, d); out = []
    for se in os.environ.get("FIT_SE", "conley,state").split(","):
        r, xs = fit(s, d[2], se=se, h=d[3])
        for i, nm in ((0, "x_FS10"), (len(LIN), "heat")):
            out.append(dict(id=d[0], C=d[1], y=d[2], h=d[3], kind=d[4], se_type=se, coef=nm, beta=float(r["beta"][i]), se=float(r["se"][i]),
                            p=float(r["p"][i]), n=int(r["n"]), banks=int(r["n_units"]), years=int(s.year.nunique()), clusters=int(r["n_clusters"]), sd_y=float(r["sd_y"])))
    return dict(rows=out)


_W = {}
def get_W():
    if not _W:
        _W["W"] = (sp.load_npz(f"{CH}/W.npz"), np.load(f"{CH}/G.npy"), np.load(f"{CH}/G_years.npy"), float(open(f"{CH}/sd.txt").read()))
        if os.path.exists(f"{CH}/Gd.npy"): _W["Gd"] = np.load(f"{CH}/Gd.npy")
    return _W


def perm_dr(W, Gd, yrs, rows, years, pi):
    out = np.empty(len(rows))
    for t in np.unique(years):
        sel = np.where(years == t)[0]; out[sel] = W[rows[sel]] @ Gd[:, int(pi[t]) - int(yrs[0])]
    return out


_DC = {}
def get_design(B, d):
    if d[0] not in _DC:
        _DC.clear(); _DC[d[0]] = V3Design(frame_of(B, d), d[2])
    return _DC[d[0]]


def run_ri(j, B):
    w = get_W(); W, G, yrs, sd = w["W"]
    D = get_design(B, j["d"]); out = []
    for c in j["chunks"]:
        rng = np.random.default_rng([CONFIG["SEED_V3"], c])            # cùng chunk → cùng π cho mọi thiết kế
        for _ in range(CONFIG["NPERM"]):
            pi = draw_pi(rng, YEARS_PI)
            h = perm_heat(W, G, yrs, sd, D.rows, D.year, pi)
            dr = perm_dr(W, w["Gd"], yrs, D.rows, D.year, pi) if D.joint else None
            out.append(D.beta(h, dr).tolist())
    return dict(perm=out, did=j["did"], chunk=j["chunks"][0])


def run_chk(B):
    """Design.beta và fit_lp phải cho cùng β (< 1e-8) — trên nhiệt hoán vị cố định π0, không trên nhiệt thật (Thịnh §5.4)."""
    w = get_W(); W, G, yrs, sd = w["W"]
    pi0 = draw_pi(np.random.default_rng(999), YEARS_PI); res = {}
    for d in [x for x in designs() if x[0] in ("LP_C1_6", "TH_C2_6", "LP_C5_2")]:
        s = frame_of(B, d)
        hp = perm_heat(W, G, yrs, sd, s.index.to_numpy(), s.year.to_numpy(), pi0)
        if CONFIG["RI_DROUGHT"] == "joint" and CONFIG["DROUGHT"] != "none":
            continue
        s2 = s.assign(heat=hp)
        r, _ = fit(s2, d[2], se="state", h=d[3])
        bd = V3Design(s, d[2]).beta(hp)
        res[d[0]] = max(abs(bd[0] - r["beta"][0]), abs(bd[len(LIN)] - r["beta"][len(LIN)]))
    return dict(chk=res)


def cmd_worker(w, nw, budget, prefixes):
    t0 = time.time(); B = None; mx = 0.0; done = 0
    mine = [j for i, j in enumerate(jobs()) if (j["di"] if j["kind"] == "ri" else i) % nw == w and (not prefixes or any(j["id"].startswith(p) for p in prefixes))]
    for j in mine:
        fn = f"{JOBD}/{j['id']}.json"
        if os.path.exists(fn): continue
        if time.time() - t0 + max(mx * 1.25, 20) > budget: break
        t1 = time.time()
        if B is None: B = load_panel(FAKE, FSEED, FBETA)
        res = run_ri(j, B) if j["kind"] == "ri" else (run_chk(B) if j["kind"] == "chk" else run_fit(j, B))
        res.pop("d", None)
        res["secs"] = time.time() - t1
        json.dump(res, open(fn + ".tmp", "w")); os.replace(fn + ".tmp", fn)
        mx = max(mx, time.time() - t1); done += 1
    pend = sum(1 for j in jobs() if not os.path.exists(f"{JOBD}/{j['id']}.json"))
    print(f"worker {w}: xong {done} job, còn {pend} (toàn bộ), {time.time() - t0:.0f}s")


def mde_ri(dist):
    """MDE80 RI phi tham số (Thịnh §6.2): c95 từ hoán vị lẻ, power trên hoán vị chẵn; lưới 0..6 sd, bước 0,01 sd."""
    a, bb = np.abs(dist[0::2]), dist[1::2]
    if len(a) < 5 or len(bb) < 5: return np.nan
    c = np.quantile(a, .95); s = dist.std(ddof=1)
    for k in np.arange(0, 6.001, .01):
        dlt = k * s
        if (np.abs(dlt + bb) >= c).mean() >= .8 and (np.abs(-dlt + bb) >= c).mean() >= .8: return dlt
    return np.nan


def cmd_collect():
    S = []; P = {}
    for f in sorted(glob.glob(f"{JOBD}/*.json")):
        x = json.load(open(f))
        if "rows" in x: S += x["rows"]
        if "perm" in x: P.setdefault(x["did"], []).append((x["chunk"], np.array(x["perm"])))
    S = pd.DataFrame(S)
    perm = {k: np.concatenate([a for _, a in sorted(v, key=lambda z: z[0])]) for k, v in P.items()}
    Rg = min((len(v) for v in perm.values()), default=0)
    perm = {k: v[:Rg] for k, v in perm.items()}
    SE0 = "conley" if (S.se_type == "conley").any() else "state"
    def est(did, se=None):
        x = S[(S.id == did) & (S.coef == "x_FS10") & (S.se_type == (se or SE0))]
        return x.iloc[0] if len(x) else S[(S.id == did) & (S.coef == "x_FS10")].iloc[0]
    lp = []
    for did in S.id.unique():
        o, st = est(did), est(did, "state"); dist = perm.get(did, np.zeros((0, 5)))[:, 0]
        sdp = dist.std(ddof=1) if len(dist) > 2 else np.nan
        lp.append(dict(id=did, C=o.C, y=o.y, h=o.h, kind=o.kind, beta2=o.beta, se_conley=o.se, p_conley=o.p, se_state=st.se, p_state=st.p,
                       R=len(dist), sd_perm=sdp, mean_perm=dist.mean() if len(dist) else np.nan,
                       p_RI=(1 + (np.abs(dist) >= abs(o.beta)).sum()) / (1 + len(dist)) if len(dist) else np.nan,
                       mde80=2.8016 * sdp, mde80_ri=mde_ri(dist) if len(dist) else np.nan, n=o.n, banks=o.banks, shock_years=o.years, sd_y=o.sd_y))
    LP = pd.DataFrame(lp).sort_values(["C", "kind", "h"]); LP.to_csv(f"{RESD}/v3_lp_long.csv", index=False)
    conf = []; TS = {}
    for C in FAMILY:
        th = THETA[C]; hs, wts = th["hs"](), th["w"]()
        ids = [f"{'TH' if th['common'] else 'LP'}_{C}_{h}" for h in hs]
        if not all(i in perm for i in ids) or not all((S.id == i).any() for i in ids): continue
        theta = sum(wt * est(i).beta for wt, i in zip(wts, ids))
        ts = sum(wt * perm[i][:, 0] for wt, i in zip(wts, ids)); TS[C] = ts; sdp = ts.std(ddof=1)
        d = CONFIG["SESOI"].get(C)
        q05, q95 = np.quantile(ts, [.05, .95])
        row = dict(C=C, theta=theta, R=len(ts), sd_perm=sdp, mean_perm=ts.mean(), p_RI=(1 + (np.abs(ts) >= abs(theta)).sum()) / (1 + len(ts)),
                   ci90_lo=theta - 1.6449 * sdp, ci90_hi=theta + 1.6449 * sdp, ci90q_lo=theta - q95, ci90q_hi=theta - q05,
                   mde80=2.8016 * sdp, mde80_ri=mde_ri(ts), sesoi=d, n=int(est(ids[0]).n), shock_years=int(est(ids[0]).years))
        if d:
            row.update(tost_pass=bool(row["ci90_lo"] > -d and row["ci90_hi"] < d), tostq_pass=bool(row["ci90q_lo"] > -d and row["ci90q_hi"] < d), mde_over_sesoi=row["mde80"] / d)
        conf.append(row)
    O = pd.DataFrame(conf)
    if len(O) == len(FAMILY):            # Westfall–Young step-down max-|t| (Thịnh §8.1)
        sv = O.sd_perm.to_numpy(); tobs = np.abs(O.theta.to_numpy()) / sv
        T = np.column_stack([np.abs(TS[C]) / s for C, s in zip(O.C, sv)])
        order = np.argsort(-tobs); padj = np.zeros(len(O)); prev = 0.0
        for k, i in enumerate(order):
            p_ = (1 + (T[:, order[k:]].max(axis=1) >= tobs[i]).sum()) / (1 + T.shape[0]); prev = max(prev, p_); padj[i] = prev
        O["p_WY"] = padj
        def status(r):
            if r.p_WY < .05: return "+" if r.theta > 0 else "-"
            if r.sesoi: return "0" if r.tost_pass else "?"
            return "? (chưa có SESOI)"
        O["status"] = O.apply(status, axis=1)
    O.to_csv(f"{RESD}/v3_confirmatory.csv", index=False)
    if perm: np.save(f"{RESD}/perm_beta2.npy", np.stack([perm[k][:, 0] for k in sorted(perm)], axis=1)); pd.Series(sorted(perm)).to_csv(f"{RESD}/perm_beta2_columns.csv", index=False)
    fchk = f"{JOBD}/CHK.json"
    if os.path.exists(fchk): print("CHK max|β_nhanh − β_fit_lp| =", max(json.load(open(fchk))["chk"].values()))
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(O.round(4).to_string(index=False) if len(O) else "chưa đủ RI cho θ"); print("LP:", len(LP), "dòng | R =", Rg)


def cmd_check():
    """Đồng nhất thức §3.3: trên mẫu chung h=0..6, không winsorize, β(cộng dồn h) = Σ_j β(từng năm j) — cho C1 (NCO)."""
    B = load_panel(FAKE, FSEED, FBETA); C = "C1"; v = CONFIG["VAR"][C]; Hm = 6
    rows = None
    for h in range(Hm + 1):
        r = sample(B, C, f"{v}_h{h}", h).index; rows = r if rows is None else rows.intersection(r)
    s = sample(B, C, f"{v}_h0", 0, rows=rows).copy()
    for h in range(Hm + 1): s[f"_flow{h}"] = s[f"{v}_h{h}"] - (s[f"{v}_h{h-1}"] if h else 0.0)
    cum = [fit(s, f"{v}_h{h}", se="state", h=h)[0]["beta"][0] for h in range(Hm + 1)]
    flw = [fit(s, f"_flow{h}", se="state", h=h)[0]["beta"][0] for h in range(Hm + 1)]
    dev = max(abs(cum[h] - sum(flw[: h + 1])) for h in range(Hm + 1))
    print(f"§3.3 đồng nhất thức trên {len(s)} dòng: max|β_cum − Σβ_flow| = {dev:.2e}")
    json.dump(dict(identity_dev=dev, n=len(s)), open(f"{RESD}/check_identity.json", "w"))


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "prep": cmd_prep(float(sys.argv[2]) if len(sys.argv) > 2 else 1e9)
    elif c == "list":
        J = jobs(); print(len(J), "job;", sum(j["kind"] == "ri" for j in J), "RI;", len(designs()), "thiết kế; R =", R)
    elif c == "worker": cmd_worker(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5:])
    elif c == "collect": cmd_collect()
    elif c == "check": cmd_check()
