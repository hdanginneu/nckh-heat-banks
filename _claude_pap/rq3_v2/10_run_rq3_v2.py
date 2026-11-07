"""10_run_rq3_v2.py — chạy RQ3 theo PAP v2 (CHỈ chạy sau khi PAP_v2.md + script đã đóng băng bằng freeze_v2.py).
Lệnh:  prep | list | worker <w> <nw> <budget_s> [tiền tố job ...] | collect
DRYRUN=1: thay nhiệt bằng nhiệt hoán vị (một π cố định) để kiểm tra mã end-to-end mà KHÔNG chạm hệ số nhiệt thật; kết quả vào results_dry/.
Nguyên tắc: không có lựa chọn nào phụ thuộc kết quả; mọi job liệt kê dưới đây đều chạy và đều được ghi vào specs_run_v2.csv."""
import sys, json, glob, hashlib, datetime
from _v2_ri import *
DRY = os.environ.get("DRYRUN", "0") == "1"
RESD = f"{V2}/{'results_dry' if DRY else 'results'}"; JOBD = f"{RESD}/jobs"; os.makedirs(JOBD, exist_ok=True)
CH = os.path.join(CACHE, "dry" if DRY else "real"); os.makedirs(CH, exist_ok=True)
SEED0 = 20261106
NCH2, NCH01 = (2, 1) if DRY else (60, 10)          # số khối hoán vị (10 hoán vị/khối): V2 → 600; V0, V1 → 100
NPERM = 10
SD = ["Z"]
MULTS = {"lin": LIN, "bins": ["bin2", "bin3", "bin4", "bin5"] + Z_INT, "ag15": ["ag15f"] + Z_INT, "ag25": ["ag25f"] + Z_INT, "ag35": ["ag35f"] + Z_INT,
         "cov": ["FS10Cov", "FS10", "Cov"] + Z_INT, "none": []}
DIVS = ["East North Central", "East South Central", "Middle Atlantic", "Mountain", "New England", "Pacific", "South Atlantic", "West North Central", "West South Central"]

def load_panel():
    b = pd.read_parquet(f"{CH}/panel_run.parquet")
    return b

def jobs():
    J = []
    for k in PRIMARY: J.append(dict(id=f"A_{k}", kind="fit", key=k, level=2, tag="main"))
    J.append(dict(id="CHK_design", kind="chk"))
    for c in range(NCH2): J.append(dict(id=f"RI_L2_{c:03d}", kind="ri", chunk=c, level=2))
    for k in ["dALLOW|raw", "prov|raw", "D1", "dALLOW_h1", "dLIQ_h1", "prov_h1"]: J.append(dict(id=f"S_{k}", kind="fit", key=k, level=2, tag="secondary"))
    for lv in (0, 1):
        for k in PRIMARY: J.append(dict(id=f"V{lv}_{k}", kind="fit", key=k, level=lv, tag=f"variant_L{lv}"))
    for k in PRIMARY:
        J.append(dict(id=f"PL2_{k}", kind="fit", key=k, level=2, placebo2=True, lead="heat_lead1", tag="placebo_twoway"))
        J.append(dict(id=f"BIN_{k}", kind="fit", key=k, level=2, mults="bins", tag="bins"))
        J.append(dict(id=f"COV_{k}", kind="fit", key=k, level=2, mults="cov", tag="heat_x_FS_x_Cov"))
        for t in ("ag15", "ag25", "ag35"): J.append(dict(id=f"TH{t}_{k}", kind="fit", key=k, level=2, mults=t, tag=f"threshold_{t}"))
        J.append(dict(id=f"Y0922_{k}", kind="fit", key=k, level=2, years=(2009, 2022), tag="years_2009_2022"))
        J.append(dict(id=f"W05_{k}", kind="fit", key=k, level=2, p=0.005, tag="winsor_0.5"))
        J.append(dict(id=f"W00_{k}", kind="fit", key=k, level=2, p=0.0, tag="no_winsor"))
        if k != "dLIQ": J.append(dict(id=f"Y0724_{k}", kind="fit", key=k, level=2, years=(2007, 2024), extra_ctrl=["cecl_post"], tag="years_2007_2024_cecl"))
        J.append(dict(id=f"CL_{k}", kind="fit", key=k, level=0, mults="none", group="ag25", tag="classic_ag25_heat_main"))
        J.append(dict(id=f"CLP_{k}", kind="fit", key=k, level=0, mults="none", group="ag25", hv="heat_lead1", lead="heat_lead1", tag="classic_ag25_placebo_lead"))
    for k in ("dALLOW|cond", "dLIQ"):
        for d in DIVS: J.append(dict(id=f"DD_{k}_{d}", kind="fit", key=k, level=2, drop_div=d, tag="drop_division"))
    for lv in (0, 1):
        for c in range(NCH01): J.append(dict(id=f"RI_L{lv}_{c:03d}", kind="ri", chunk=c, level=lv))
    return J

def run_fit(j, B):
    key = j["key"]; mk = j.get("mults", "lin"); mults = MULTS[mk]; hv = j.get("hv", "heat"); level = j.get("level", 2)
    need = ["Cov"] if mk == "cov" else []; bases = (LIN + ["Cov"]) if mk == "cov" else None
    s = frame(B, key, tuple(j.get("years", (2007, 2022))), need_lead=j.get("lead"), p=j.get("p", 0.01), extra_ctrl=j.get("extra_ctrl", []), need=need, group=j.get("group"))
    if j.get("drop_div"): s = s[s.division != j["drop_div"]]
    if mk == "cov": s = s.assign(FS10Cov=s.FS10 * s.Cov)
    extra = []
    if j.get("placebo2"):
        s = s.copy()
        for m in LIN: s["L_x_" + m] = s["heat_lead1"] * s[m]; extra.append("L_x_" + m)
        extra.append("heat_lead1")
    rows = []; y = OUTS[key][0]
    for se in ("conley", "state"):
        r, xs = fit(s, key, hv, se=se, level=level, mults=mults, bases=bases, extra=extra, extra_ctrl=j.get("extra_ctrl", []))
        rep = set(["x_" + m for m in mults] + [hv] + extra)
        for i, nm in enumerate(xs):
            if nm in rep:
                rows.append(dict(job=j["id"], tag=j["tag"], key=key, y=y, level=level, mults=mk, years=str(j.get("years", (2007, 2022))), sample=j.get("group") or "all",
                                 se_type=se, coef=nm, beta=float(r["beta"][i]), se=float(r["se"][i]), p=float(r["p"][i]), ci95_lo=float(r["ci95"][0][i]), ci95_hi=float(r["ci95"][1][i]),
                                 n=int(r["n"]), banks=int(r["n_units"]), clusters=int(r["n_clusters"]), sd_y=float(r["sd_y"]), allowlag_med=float(s["ALLOWlag"].median()), dist=r["dist"]))
    return dict(rows=rows)

_DC = {}
def get_design(key, level):
    k = (key, level)
    if k not in _DC: _DC[k] = Design.load(f"{CH}/design_{key.replace('|', '_')}_L{level}.npz")
    return _DC[k]

_WC = {}
def get_W():
    if "W" not in _WC:
        _WC["W"] = (sp.load_npz(f"{CH}/W.npz"), np.load(f"{CH}/G.npy"), np.load(f"{CH}/G_years.npy"), float(open(f"{CH}/sd.txt").read()))
    return _WC["W"]

def run_ri(j):
    W, G, yrs, sd = get_W(); level = j["level"]
    rng = np.random.default_rng([SEED0, j["chunk"]])
    des = {k: get_design(k, level) for k in PRIMARY}
    out = []
    for _ in range(NPERM):
        pi = draw_pi(rng, range(2006, 2025)); row = []
        for k in PRIMARY:
            D = des[k]; h = perm_heat(W, G, yrs, sd, D.rows, D.year, pi)
            row.append(D.beta(h).tolist())
        out.append(row)
    return dict(perm=out, keys=PRIMARY, level=level, chunk=j["chunk"])

def run_chk(B):
    """Kiểm tra nhất quán: β của Design.beta (dùng trong RI) tại nhiệt THẬT == β của fit_lp ở các job A_*."""
    out = {}
    for k in PRIMARY:
        D = get_design(k, 2); out[k] = D.beta(B.loc[D.rows, "heat"].to_numpy()).tolist()
    return dict(chk=out)

def cmd_prep():
    b = build()
    if DRY:
        W, G, yrs, sd = build_W(b); rng = np.random.default_rng(999); pi0 = draw_pi(rng, range(2006, 2025))
        rows = np.arange(len(b)); yr = b.year.to_numpy()
        b["heat"] = perm_heat(W, G, yrs, sd, rows, yr, pi0)
        for kk in (1, 2):
            pk = {t: pi0.get(t + kk, np.nan) for t in range(2006, 2025)}
            v = np.full(len(b), np.nan)
            for t in range(2006, 2025 - kk):
                sel = np.where(yr == t)[0]; v[sel] = (W[sel] @ G[:, int(pk[t]) - 1981]) / sd
            b[f"heat_lead{kk}"] = v
    b.to_parquet(f"{CH}/panel_run.parquet", index=False)
    W, G, yrs, sd = build_W(b); sp.save_npz(f"{CH}/W.npz", W); np.save(f"{CH}/G.npy", G); np.save(f"{CH}/G_years.npy", yrs); open(f"{CH}/sd.txt", "w").write(str(sd))
    h = hashlib.sha256(open(f"{CH}/panel_run.parquet", "rb").read()).hexdigest()
    open(f"{RESD}/prep_log.txt", "w").write(f"{datetime.datetime.now()} panel sha256={h} rows={len(b)} dry={DRY}\n")
    print("prep ok", len(b), h[:12])

def cmd_prep_design(key, level):
    B = load_panel(); s = frame(B, key); Design.build(s, key, int(level)).save(f"{CH}/design_{key.replace('|', '_')}_L{level}.npz"); print("design", key, level, len(s))

def cmd_worker(w, nw, budget, prefixes):
    t0 = time.time(); B = load_panel(); mx = 0.0
    mine = [j for i, j in enumerate(jobs()) if i % nw == w and (not prefixes or any(j["id"].startswith(p) for p in prefixes))]
    done = 0
    for j in mine:
        fn = f"{JOBD}/{j['id'].replace('|', '_').replace(' ', '_')}.json"
        if os.path.exists(fn): continue
        if time.time() - t0 + max(mx * 1.25, 45) > budget: break
        t1 = time.time()
        res = run_ri(j) if j["kind"] == "ri" else (run_chk(B) if j["kind"] == "chk" else run_fit(j, B))
        res["job"] = j["id"]; res["secs"] = time.time() - t1
        json.dump(res, open(fn + ".tmp", "w")); os.replace(fn + ".tmp", fn)
        mx = max(mx, time.time() - t1); done += 1
    pend = sum(1 for j in jobs() if not os.path.exists(f"{JOBD}/{j['id'].replace('|', '_').replace(' ', '_')}.json"))
    print(f"worker {w}: xong {done} job, còn {pend} job (toàn bộ) sau {time.time() - t0:.0f}s")

def cmd_collect():
    rows = []; perms = {0: [], 1: [], 2: []}
    for f in sorted(glob.glob(f"{JOBD}/*.json")):
        d = json.load(open(f))
        if "rows" in d: rows += d["rows"]
        if "perm" in d: perms[d["level"]].append((d["chunk"], np.array(d["perm"])))
    S = pd.DataFrame(rows); S.to_csv(f"{RESD}/specs_run_v2.csv", index=False)
    out = []
    for lv in (2, 0, 1):
        if not perms[lv]: continue
        P = np.concatenate([a for _, a in sorted(perms[lv], key=lambda x: x[0])], axis=0)       # (R, nkeys, k)
        R = P.shape[0]
        for ik, k in enumerate(PRIMARY):
            jid = f"A_{k}" if lv == 2 else f"V{lv}_{k}"
            for coef_i, coef in ((0, "x_FS10"), (len(LIN), "heat")):
                o = S[(S.job == jid) & (S.coef == coef) & (S.se_type == "conley")]
                if o.empty: continue
                o = o.iloc[0]; st = S[(S.job == jid) & (S.coef == coef) & (S.se_type == "state")].iloc[0]
                dist = P[:, ik, coef_i]; sdp = dist.std(ddof=1)
                out.append(dict(level=lv, key=k, coef=coef, R=R, beta=o.beta, se_conley=o.se, p_conley=o.p, se_state=st.se, p_state=st.p, sd_perm=sdp, mean_perm=dist.mean(),
                                p_RI=(1 + (np.abs(dist) >= abs(o.beta)).sum()) / (1 + R), mde80=2.8016 * sdp, ci90_lo=o.beta - 1.6449 * sdp, ci90_hi=o.beta + 1.6449 * sdp,
                                ratio_sd_to_conley=sdp / o.se, ratio_sd_to_state=sdp / st.se, n=o.n, banks=o.banks, sd_y=o.sd_y, allowlag_med=o.allowlag_med))
        # Westfall–Young step-down (max-|t|) trên họ chính, riêng cho x_FS10
        sub = [x for x in out if x["level"] == lv and x["coef"] == "x_FS10"]
        if len(sub) == len(PRIMARY):
            sdv = np.array([x["sd_perm"] for x in sub]); tobs = np.abs(np.array([x["beta"] for x in sub])) / sdv; T = np.abs(P[:, :, 0]) / sdv
            order = np.argsort(-tobs); padj = np.zeros(len(sub)); prev = 0.0
            for r_, idx in enumerate(order):
                rem = order[r_:]; p_ = (1 + (T[:, rem].max(axis=1) >= tobs[idx]).sum()) / (1 + R); prev = max(prev, p_); padj[idx] = prev
            for x, pa in zip(sub, padj): x["p_RI_WY"] = pa
    O = pd.DataFrame(out)
    fchk = f"{JOBD}/CHK_design.json"
    if os.path.exists(fchk):
        ck = json.load(open(fchk))["chk"]; mx = 0.0
        for k in PRIMARY:
            a = S[(S.job == f"A_{k}") & (S.se_type == "conley")].set_index("coef").beta
            if len(a): mx = max(mx, abs(ck[k][0] - a["x_FS10"]), abs(ck[k][len(LIN)] - a["heat"]))
        print("CHK max|β_fast − β_fit_lp| =", mx)
    # TOST: SESOI (đơn vị β2 = pp/ +10pp FS/ +1 SD nhiệt): allowance & provision = 5% × trung vị allowance trễ / 2,5; dLIQ = 0,10·sd_y / 2,5
    if len(O):
        med = float(S[(S.job == "A_dALLOW|cond")].allowlag_med.iloc[0]) if (S.job == "A_dALLOW|cond").any() else np.nan
        O["sesoi"] = np.where(O.key.isin(["dALLOW|cond", "prov|cond"]), 0.05 * med / 2.5, 0.10 * O.sd_y / 2.5)
        O["tost_pass"] = (O.ci90_lo > -O.sesoi) & (O.ci90_hi < O.sesoi)
        O["mde_over_sesoi"] = O.mde80 / O.sesoi
    O.to_csv(f"{RESD}/primary_ri_results.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print(O.round(5).to_string(index=False) if len(O) else "chưa có RI"); print("số dòng spec:", len(S), "| job fit xong:", S.job.nunique() if len(S) else 0)

if __name__ == "__main__":
    c = sys.argv[1]
    if c == "prep": cmd_prep()
    elif c == "prep_design": cmd_prep_design(sys.argv[2], sys.argv[3])
    elif c == "list": print(len(jobs()), "job;", sum(1 for j in jobs() if j["kind"] == "ri"), "RI")
    elif c == "worker": cmd_worker(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5:])
    elif c == "collect": cmd_collect()
