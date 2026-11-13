"""run_v3.py — chạy RQ3 v3 theo PAP_v3.md. Lệnh: prep | list | worker <w> <nw> <budget_s> [tiền tố id] | collect | check
SPEC=main (xác nhận + độ vững R2–R4 + placebo + attrition) | SPEC=dr (độ vững R1: hạn hán, hoán vị chung).
PAP_FAKE=1: outcome v3 hoán vị trong từng năm × ag25 (kiểm code, không diễn giải); FAKE_SEED, FAKE_BETA, R_FAKE tuỳ chọn.
Không có PAP_FAKE=1: chỉ chạy khi PAP v3 đã đóng băng (guard_real). Mọi job liệt kê đều chạy và đều được ghi; không chọn theo kết quả."""
import os, sys, time, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _v3_spec import *                                    # noqa: F401,F403
import scipy.sparse as sp
from _v2_ri import build_W, perm_heat, draw_pi, CACHE

FAKE = os.environ.get("PAP_FAKE", "0") == "1"
FSEED = int(os.environ.get("FAKE_SEED", "0")); FBETA = float(os.environ.get("FAKE_BETA", "0"))
if not FAKE: guard_real()
TAG = (f"fake_s{FSEED}" + (f"_b{FBETA:g}" if FBETA else "") if FAKE else "real") + ("" if SPEC == "main" else f"_{SPEC}")
R = int(os.environ.get("R_FAKE", "20")) if FAKE else CONFIG["R"]
RESD = f"{HERE}/results_{TAG}"; JOBD = f"{RESD}/jobs"; os.makedirs(JOBD, exist_ok=True)
CH = os.path.join(CACHE, f"v3_{TAG}"); os.makedirs(CH, exist_ok=True)
YEARS_PI = range(2006, 2025)


def designs():
    """Mỗi thiết kế = một hồi quy: dict(id, C, y, h, th (θ chứa nó, hoặc None), t0, opts, se).
    TH_<θ>_<h>: thành phần của θ (mẫu chung nếu θ ghép nhiều h). LP_<C>_<h>: LP mô tả h=0..6, mẫu riêng từng h.
    PL_<C>_m<m>: placebo outcome trước cú sốc. EX_<h>: attrition. se=True: tính thêm SE Conley và cụm-bang (mô tả)."""
    D = []
    for th in thetas():
        for h in th["hs"]:
            D.append(dict(id=f"TH_{th['name']}_{h}", C=th["C"], y=f"{th['var']}_h{h}", h=h, th=th, t0=None, opts=th["opts"], se=th["grp"] == "main"))
    if SPEC == "main":
        for C in FAMILY:
            for h in range(7):
                if t_last(C, h) >= CONFIG["T_FIRST"]:
                    D.append(dict(id=f"LP_{C}_{h}", C=C, y=f"{CONFIG['VAR'][C]}_h{h}", h=h, th=None, t0=None, opts={}, se=True))
            for m in (2, 3):
                D.append(dict(id=f"PL_{C}_m{m}", C=C, y=f"PRE_{CONFIG['VAR'][C]}_m{m}", h=0, th=None, t0=2005 + m, opts={}, se=False))
        for h in range(1, 7):
            D.append(dict(id=f"EX_{h}", C="C1", y=f"EXIT_h{h}", h=h, th=None, t0=None, opts={}, se=False))
    return D


_ROWS = {}
def frame_of(B, d):
    rows = None
    if d["th"] is not None and d["th"]["common"]:
        k = d["th"]["name"]
        if k not in _ROWS: _ROWS[k] = common_rows(B, d["th"])
        rows = _ROWS[k]
    return make_frame(B, d["C"], d["y"], d["h"], rows=rows, t0=d["t0"], opts=d["opts"])


def jobs():
    D = designs()
    J = [dict(id=f"RI_{d['id']}", kind="ri", d=d, di=i) for i, d in enumerate(D)]
    J += [dict(id=f"SE_{d['id']}", kind="se", d=d, di=i) for i, d in enumerate(D) if d["se"]]
    J.append(dict(id="CHK", kind="chk", di=0))
    return J


def cmd_prep():
    t0 = time.time(); B = load_panel(FAKE, FSEED, FBETA)
    W, G, yrs, sd = build_W(B)
    sp.save_npz(f"{CH}/W.npz", W); np.save(f"{CH}/G.npy", G); np.save(f"{CH}/G_years.npy", yrs); open(f"{CH}/sd.txt", "w").write(str(sd))
    h = pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips"]); cty = np.sort(h.county_fips.unique())
    dr = pd.read_parquet(f"{ROOT}/data_external/usdm/county_year_drought.parquet")
    Gd = dr.pivot(index="county_fips", columns="year", values="dr_d2_wk").reindex(index=cty, columns=yrs).fillna(0).to_numpy()
    np.save(f"{CH}/Gd.npy", Gd)
    meta = []
    for d in designs():
        s = frame_of(B, d)
        meta.append(dict(id=d["id"], C=d["C"], y=d["y"], h=d["h"], theta=d["th"]["name"] if d["th"] else "", n=len(s), banks=s.idrssd.nunique(),
                         shock_years=s.year.nunique(), t_first=int(s.year.min()), t_last=int(s.year.max())))
    pd.DataFrame(meta).to_csv(f"{RESD}/designs.csv", index=False)
    print("prep:", len(meta), "thiết kế; SPEC =", SPEC, "; R =", R, f"| {time.time() - t0:.0f}s")


_W = {}
def get_W():
    if not _W:
        _W["W"] = (sp.load_npz(f"{CH}/W.npz"), np.load(f"{CH}/G.npy"), np.load(f"{CH}/G_years.npy"), float(open(f"{CH}/sd.txt").read()))
        _W["Gd"] = np.load(f"{CH}/Gd.npy")
    return _W


def perm_dr(W, Gd, yrs, rows, years, pi):
    out = np.empty(len(rows))
    for t in np.unique(years):
        sel = np.where(years == t)[0]; out[sel] = W[rows[sel]] @ Gd[:, int(pi[t]) - int(yrs[0])]
    return out


_PIS = []
def all_pis():
    """R hoán vị năm không điểm cố định; khối c dùng rng([SEED_V3, c]) → mọi thiết kế, mọi worker dùng CÙNG dãy π (PAP §5.1)."""
    if not _PIS:
        c = 0
        while len(_PIS) < R:
            rng = np.random.default_rng([CONFIG["SEED_V3"], c]); _PIS.extend(draw_pi(rng, YEARS_PI) for _ in range(CONFIG["NPERM"])); c += 1
    return _PIS[:R]


def run_ri(j, B):
    """β quan sát (nhiệt thật của panel đang nạp) và R β hoán vị, cùng một V3Design."""
    w = get_W(); W, G, yrs, sd = w["W"]; d = j["d"]
    s = frame_of(B, d); D = V3Design(s, d["y"])
    obs, rss0 = D.beta_rss(B.loc[D.rows, "heat"].to_numpy(), B.loc[D.rows, "Dr"].to_numpy() if D.joint else None)
    perm, prss = [], []
    for pi in all_pis():
        b_, r_ = D.beta_rss(perm_heat(W, G, yrs, sd, D.rows, D.year, pi), perm_dr(W, w["Gd"], yrs, D.rows, D.year, pi) if D.joint else None)
        perm.append(b_[[0, len(LIN)]].tolist()); prss.append(r_)
    return dict(did=d["id"], obs=[float(obs[0]), float(obs[len(LIN)])], perm=perm, obs_rss=rss0, perm_rss=prss, n=len(s), banks=int(s.idrssd.nunique()),
                shock_years=int(s.year.nunique()), sd_y=float(np.std(s[d["y"]].to_numpy(float))))


def run_se(j, B):
    d = j["d"]; s = frame_of(B, d); out = {}
    for se in os.environ.get("FIT_SE", "conley,state").split(","):
        r, xs = fit(s, d["y"], se=se, h=d["h"])
        out[se] = dict(beta2=float(r["beta"][0]), se2=float(r["se"][0]), p2=float(r["p"][0]), beta1=float(r["beta"][len(LIN)]), se1=float(r["se"][len(LIN)]), clusters=int(r["n_clusters"]))
    return dict(did=d["id"], se=out)


def run_chk(B):
    """V3Design.beta = fit_lp (< 1e-8) trên nhiệt (và hạn hán nếu SPEC=dr) hoán vị cố định π0 — không trên nhiệt thật (PAP §5.4).
    Kèm: dựng lại Dr từ W và ma trận hạn hán theo hạt (kiểm perm_dr)."""
    w = get_W(); W, G, yrs, sd = w["W"]; res = {}
    pi0 = draw_pi(np.random.default_rng(999), YEARS_PI); ident = {t: t for t in YEARS_PI}
    D = designs(); pick = [d for d in D if d["id"] in ("TH_C1_6", "TH_C2_6", "TH_C5_2")]
    for d in pick:
        s = frame_of(B, d); rows, yr = s.index.to_numpy(), s.year.to_numpy()
        hp = perm_heat(W, G, yrs, sd, rows, yr, pi0); s2 = s.assign(heat=hp); drp = None
        if CONFIG["RI_DROUGHT"] == "joint":
            drp = perm_dr(W, w["Gd"], yrs, rows, yr, pi0); s2["Dr"] = drp
            for z in ["FS10"] + Z_INT: s2[f"x_Dr_{z}"] = drp * s2[z]
        r, _ = fit(s2, d["y"], se="state", h=d["h"]); bd = V3Design(s, d["y"]).beta(hp, drp)
        res[d["id"]] = float(max(abs(bd[0] - r["beta"][0]), abs(bd[len(LIN)] - r["beta"][len(LIN)])))
        res["Dr_rebuild_" + d["id"]] = float(np.max(np.abs(perm_dr(W, w["Gd"], yrs, rows, yr, ident) - s.Dr.to_numpy()))) if s.Dr.notna().all() else -1.0
    return dict(chk=res)


def cmd_worker(w, nw, budget, prefixes):
    t0 = time.time(); B = None; mx = 0.0; done = 0
    mine = [j for j in jobs() if j["di"] % nw == w and (not prefixes or any(j["id"].startswith(p) for p in prefixes))]
    for j in mine:
        fn = f"{JOBD}/{j['id']}.json"
        if os.path.exists(fn): continue
        if time.time() - t0 + max(mx * 1.25, 30) > budget: break
        t1 = time.time()
        if B is None: B = load_panel(FAKE, FSEED, FBETA)
        res = run_ri(j, B) if j["kind"] == "ri" else (run_se(j, B) if j["kind"] == "se" else run_chk(B))
        res["secs"] = time.time() - t1
        json.dump(res, open(fn + ".tmp", "w")); os.replace(fn + ".tmp", fn)
        mx = max(mx, time.time() - t1); done += 1
    pend = sum(1 for j in jobs() if not os.path.exists(f"{JOBD}/{j['id']}.json"))
    print(f"worker {w}/{nw}: xong {done} job, còn {pend} (toàn bộ), {time.time() - t0:.0f}s")


def mde_ri(dist):
    """MDE80 RI phi tham số (PAP §7.2): c95 từ hoán vị lẻ, power trên hoán vị chẵn; lưới 0..6 sd, bước 0,01 sd."""
    a, bb = np.abs(dist[0::2]), dist[1::2]
    if len(a) < 20 or len(bb) < 20: return np.nan
    c = np.quantile(a, .95); s = dist.std(ddof=1)
    for k in np.arange(0, 6.001, .01):
        if (np.abs(k * s + bb) >= c).mean() >= .8 and (np.abs(-k * s + bb) >= c).mean() >= .8: return k * s
    return np.nan


def kappa_of(x):
    """κ = sqrt(trung vị RSS_x hoán vị / RSS_x thật): > 1 nghĩa là nhiệt thật có ít biến thiên hữu ích hơn nhiệt hoán vị điển hình (PAP §6.3)."""
    return float(np.sqrt(np.median(x["perm_rss"]) / x["obs_rss"])) if "obs_rss" in x else 1.0


def stat_row(name, obs, ts, kappa=1.0):
    """p_RI: chính xác theo hoán vị, không chỉnh. CI90, TOST, MDE dùng sd_adj = sd hoán vị × max(1, κ)."""
    sdp = ts.std(ddof=1); q05, q95 = np.quantile(ts, [.05, .95]); k = max(1.0, kappa); sda = sdp * k
    return dict(name=name, theta=obs, R=len(ts), sd_perm=sdp, kappa=kappa, sd_adj=sda, mean_perm=ts.mean(), p_RI=(1 + (np.abs(ts) >= abs(obs)).sum()) / (1 + len(ts)),
                ci90_lo=obs - 1.6449 * sda, ci90_hi=obs + 1.6449 * sda, ci90q_lo=obs - k * q95, ci90q_hi=obs - k * q05, mde80=2.8016 * sda, mde80_ri=k * mde_ri(ts))


def cmd_collect():
    RI, SE = {}, {}
    for f in sorted(glob.glob(f"{JOBD}/RI_*.json")): x = json.load(open(f)); RI[x["did"]] = x
    for f in sorted(glob.glob(f"{JOBD}/SE_*.json")): x = json.load(open(f)); SE[x["did"]] = x["se"]
    D = {d["id"]: d for d in designs()}
    # 1) từng hồi quy
    lp = []
    for did, x in RI.items():
        d = D[did]; ts = np.array(x["perm"])[:, 0]; row = stat_row(did, x["obs"][0], ts, kappa_of(x))
        t1 = np.array(x["perm"])[:, 1]
        row.update(C=d["C"], y=d["y"], h=d["h"], theta=d["th"]["name"] if d["th"] else "", beta2=x["obs"][0], beta1=x["obs"][1],
                   p_RI_beta1=(1 + (np.abs(t1) >= abs(x["obs"][1])).sum()) / (1 + len(t1)), n=x["n"], banks=x["banks"], shock_years=x["shock_years"], sd_y=x["sd_y"])
        for se in ("conley", "state"):
            if did in SE and se in SE[did]: row.update({f"se_{se}": SE[did][se]["se2"], f"p_{se}": SE[did][se]["p2"], f"beta2_fitlp_{se}": SE[did][se]["beta2"]})
        lp.append(row)
    LP = pd.DataFrame(lp)
    if len(LP): LP.sort_values("name").to_csv(f"{RESD}/v3_lp_long.csv", index=False)
    # 2) thống kê θ
    rows, TS = [], {}
    for th in thetas():
        ids = [f"TH_{th['name']}_{h}" for h in th["hs"]]
        if not all(i in RI for i in ids): continue
        obs = sum(w * RI[i]["obs"][0] for w, i in zip(th["w"], ids)); ts = sum(w * np.array(RI[i]["perm"])[:, 0] for w, i in zip(th["w"], ids))
        TS[th["name"]] = ts; r = stat_row(th["name"], obs, ts, kappa_of(RI[ids[0]]))      # θ ghép nhiều h dùng mẫu chung → cùng ma trận X → cùng κ
        r.update(grp=th["grp"], C=th["C"], var=th["var"], n=RI[ids[0]]["n"], banks=RI[ids[0]]["banks"], shock_years=RI[ids[0]]["shock_years"], sd_y=RI[ids[0]]["sd_y"])
        S = SESOI.get(th["name"]) if th["grp"] == "main" else None
        if S:
            for k in ("primary", "alt"):
                dlt = S.get(k)
                if dlt: r.update({f"sesoi_{k}": dlt, f"tost_{k}": bool(r["ci90_lo"] > -dlt and r["ci90_hi"] < dlt), f"tostq_{k}": bool(r["ci90q_lo"] > -dlt and r["ci90q_hi"] < dlt)})
            r["mde_over_sesoi"] = r["mde80_ri"] / S["primary"]
        rows.append(r)
        if th["grp"] == "main" and min(th["w"]) < 0:                 # thành phần "sớm" và "muộn" của θ dạng hiệu (C2), mô tả (PAP §8.2)
            for lab, sel in (("early", [(w, i) for w, i in zip(th["w"], ids) if w < 0]), ("late", [(w, i) for w, i in zip(th["w"], ids) if w > 0])):
                tot = sum(w for w, _ in sel)
                o2 = sum(w / tot * RI[i]["obs"][0] for w, i in sel); t2 = sum(w / tot * np.array(RI[i]["perm"])[:, 0] for w, i in sel)
                r2 = stat_row(f"{th['name']}_{lab}", o2, t2, kappa_of(RI[ids[0]]))
                r2.update(grp="desc", C=th["C"], var=th["var"], n=RI[ids[0]]["n"], banks=RI[ids[0]]["banks"], shock_years=RI[ids[0]]["shock_years"], sd_y=RI[ids[0]]["sd_y"])
                rows.append(r2)
    O = pd.DataFrame(rows)
    main = O[O.grp == "main"].copy() if len(O) else O
    if len(main) == len(FAMILY):                       # Westfall–Young step-down max-|t| trên họ C1–C5 (PAP §5.3)
        sv = main.sd_perm.to_numpy(); tobs = np.abs(main.theta.to_numpy()) / sv
        T = np.column_stack([np.abs(TS[n]) / s for n, s in zip(main.name, sv)])
        order = np.argsort(-tobs); padj = np.zeros(len(main)); prev = 0.0
        for k, i in enumerate(order):
            p_ = (1 + (T[:, order[k:]].max(axis=1) >= tobs[i]).sum()) / (1 + T.shape[0]); prev = max(prev, p_); padj[i] = prev
        main["p_WY"] = padj
        if "tost_primary" in main:
            main["status"] = [("+" if r.theta > 0 else "-") if r.p_WY < .05 else ("0" if r.tost_primary else "?") for r in main.itertuples()]   # PAP §6.4
        main.to_csv(f"{RESD}/v3_confirmatory.csv", index=False)
    if len(O): O[O.grp != "main"].to_csv(f"{RESD}/v3_robust.csv", index=False)
    if TS: np.savez(f"{RESD}/perm_theta.npz", **TS)
    chk = json.load(open(f"{JOBD}/CHK.json"))["chk"] if os.path.exists(f"{JOBD}/CHK.json") else {}
    dev = [abs(SE[i][se]["beta2"] - RI[i]["obs"][0]) for i in SE if i in RI for se in SE[i]]
    summ = dict(spec=SPEC, tag=TAG, R=int(min((len(x["perm"]) for x in RI.values()), default=0)), n_designs=len(D), n_ri=len(RI), n_se=len(SE), chk=chk,
                max_abs_beta2_fast_minus_fitlp=max(dev) if dev else None)
    json.dump(summ, open(f"{RESD}/collect_summary.json", "w"), indent=1)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    cols = [c for c in ["name", "theta", "sd_perm", "kappa", "p_RI", "p_WY", "ci90_lo", "ci90_hi", "sesoi_primary", "tost_primary", "tost_alt", "mde80_ri", "mde_over_sesoi", "status", "n", "shock_years"] if c in main]
    print(main[cols].round(4).to_string(index=False) if len(main) else "chưa đủ RI cho họ C1–C5"); print(json.dumps(summ))


def cmd_check():
    """Đồng nhất thức (PAP §4.3): trên mẫu chung h=0..6, không winsorize, β(cộng dồn h) = Σ_j β(từng năm j) — NCO (C1)."""
    B = load_panel(FAKE, FSEED, FBETA); C = "C1"; v = CONFIG["VAR"][C]; rows = None
    for h in range(7):
        r = sample(B, C, f"{v}_h{h}", h).index; rows = r if rows is None else rows.intersection(r)
    s = sample(B, C, f"{v}_h0", 0, rows=rows).copy()
    for h in range(7): s[f"_flow{h}"] = s[f"{v}_h{h}"] - (s[f"{v}_h{h-1}"] if h else 0.0)
    D = {h: (V3Design(s, f"{v}_h{h}"), V3Design(s, f"_flow{h}")) for h in range(7)}
    w = get_W(); W, G, yrs, sd = w["W"]; hp = perm_heat(W, G, yrs, sd, s.index.to_numpy(), s.year.to_numpy(), draw_pi(np.random.default_rng(999), YEARS_PI))
    cum = [D[h][0].beta(hp)[0] for h in range(7)]; flw = [D[h][1].beta(hp)[0] for h in range(7)]
    dev = max(abs(cum[h] - sum(flw[: h + 1])) for h in range(7))
    print(f"đồng nhất thức trên {len(s)} dòng (nhiệt hoán vị π0): max|β_cum − Σβ_flow| = {dev:.2e}")
    json.dump(dict(identity_dev=float(dev), n=len(s)), open(f"{RESD}/check_identity.json", "w"))


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "prep": cmd_prep()
    elif c == "list":
        J = jobs(); print(len(designs()), "thiết kế;", sum(j["kind"] == "ri" for j in J), "job RI;", sum(j["kind"] == "se" for j in J), "job SE; SPEC =", SPEC, "; R =", R)
    elif c == "worker": cmd_worker(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5:])
    elif c == "collect": cmd_collect()
    elif c == "check": cmd_check()
