"""run_rob.py — các phép chạy thêm R1–R12 theo RULES_R1_R7.md và RULES_R8_R12.md (quy tắc chốt trước khi viết file này).
Lệnh:  python3 run_rob.py list
       python3 run_rob.py worker <w> <nw> <budget_s> [--fake SEED]   chạy các hồi quy (mỗi hồi quy một json)
       python3 run_rob.py collect [--fake SEED]                       tổng hợp, áp quy tắc, ghi rob_results.csv và rob_verdicts.md
Dữ liệu thật chỉ chạy khi hash khớp hashes_frozen_rob.json (freeze_rob.py). --fake: outcome hoán vị trong năm × ag25.
Mọi phép có hoán vị dùng cùng dãy π của PAP v3 (seed 20261115, khối 10, năm 2006–2024)."""
import os, sys, json, glob, time, hashlib
RDIR = os.path.dirname(os.path.abspath(__file__))
for _d in ("rq3_p3", "rq3_p2", "rq3_v3"): sys.path.insert(0, os.path.join(RDIR, "..", _d))
import run_p2 as P2                                       # panel giai đoạn 2 (đọc --fake từ argv)
import run_p3 as P3                                       # mức bảo hiểm cấp ngân hàng
import _v3_spec as V
from _v2_ri import build_W, perm_heat, draw_pi
from _v3_spec import np, pd, ROOT, TAB, RAIN, BANK_CTRL, Z_INT, LIN, CONFIG, FAMILY, DIVS, codes, year_ints, winsor, bank_frame

FAKE = P2.FAKE
R = int(os.environ.get("R_ROB", 1000))
OUT = f"{RDIR}/results_{'fake_s%d' % FAKE if FAKE is not None else 'real'}"; JOBD = f"{OUT}/jobs"; os.makedirs(JOBD, exist_ok=True)
SES = json.load(open(os.path.join(RDIR, "..", "rq3_v3", "sesoi_v3.json")))
SP2 = json.load(open(os.path.join(RDIR, "..", "rq3_p2", "sesoi_p2.json")))
DELTA = {C: SES[C]["primary"] for C in FAMILY}; DELTA.update(P1=SP2["P1"], P2=SP2["P2"])
V3RES = os.path.join(RDIR, "..", "rq3_v3", "results_real" if FAKE is None else f"results_fake_s{FAKE}")
P2RES = os.path.join(RDIR, "..", "rq3_p2", "results_real")
EXPO = f"{ROOT}/_claude_feasibility/out/02_bank_exposure_group.parquet"
FROZEN = ["RULES_R1_R7.md", "RULES_R8_R12.md", "run_rob.py"]

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def guard_real():
    hf = f"{RDIR}/hashes_frozen_rob.json"
    assert os.path.exists(hf), "Chưa đóng băng (chạy freeze_rob.py)."
    H = json.load(open(hf)); bad = [k for k, v in H.items() if sha(f"{RDIR}/{k}") != v]
    assert not bad, f"Hash không khớp: {bad}"

# ---------------------------------------------------------------- dữ liệu
_C = {}
def get_W():
    if "W" not in _C: _C["W"] = build_W(panel())
    return _C["W"]

def county_matrix(path, col, cty, yrs):
    d = pd.read_parquet(path)
    fc = "county_fips" if "county_fips" in d.columns else "fips"
    d = d[[fc, "year", col]].copy(); d[fc] = pd.to_numeric(d[fc]).astype(int)
    return d.pivot_table(index=fc, columns="year", values=col).reindex(index=cty, columns=yrs).to_numpy()

def wmean_rows(W, Gm, rows, years, pimap=None):
    """Trung bình có trọng số W của ma trận hạt × năm Gm (năm π(t) nếu có pimap), chỉ trên hạt có số liệu; trả (giá trị, độ phủ)."""
    val, cov = np.full(len(rows), np.nan), np.zeros(len(rows))
    tot = np.asarray(W[rows].sum(axis=1)).ravel()
    for t in np.unique(years):
        sel = np.where(years == t)[0]; tt = int(pimap[t]) if pimap else int(t)
        col = Gm[:, tt - 1981]; av = ~np.isnan(col)
        num = W[rows[sel]] @ np.where(av, col, 0.0); den = W[rows[sel]] @ av.astype(float)
        val[sel] = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan); cov[sel] = den / np.where(tot[sel] > 0, tot[sel], 1)
    return val, cov

_B = {}
def panel():
    if "B" in _B: return _B["B"]
    B = P3.panel().copy()                                 # = P2.panel() + mức bảo hiểm (cr) + I1–I3
    _B["B"] = B                                           # build_W cần B; các cột mới thêm dưới đây
    ids, yrs = B.idrssd.to_numpy(), B.year.to_numpy()
    p1 = pd.read_parquet(P2.P1F, columns=["idrssd", "year", "farmland_loans_kusd", "ag_production_loans_kusd", "total_loans_kusd",
                                          "allowance_legacy_kusd"]).drop_duplicates(["idrssd", "year"])
    p1["idrssd"] = pd.to_numeric(p1.idrssd).astype(B.idrssd.dtype); p1 = p1.set_index(["idrssd", "year"]).sort_index()
    pos = lambda a: np.where(a > 0, a, np.nan)
    p1["fs"] = (p1.farmland_loans_kusd + p1.ag_production_loans_kusd) / pos(p1.total_loans_kusd)
    at = lambda c, k: p1[c].reindex(pd.MultiIndex.from_arrays([ids, yrs + k])).to_numpy()
    B["FS10_l1"] = 10 * at("fs", -1)                                                         # R8
    f5 = p1.fs.xs(2005, level="year"); f6 = p1.fs.xs(2006, level="year")
    B["FS10_0506"] = B.idrssd.map(10 * (f5 + f6) / 2).to_numpy()                             # R3 (NaN nếu thiếu 2005 hoặc 2006)
    for h in (0, 1):                                                                         # R5: dự phòng / dư nợ hiện tại
        r = 100 * (at("allowance_legacy_kusd", h) / pos(at("total_loans_kusd", h)) - at("allowance_legacy_kusd", -1) / pos(at("total_loans_kusd", -1)))
        B[f"ALLr_h{h}"] = np.where(B[f"ALLOW_h{h}"].notna(), r, np.nan)
    B["FS10sq"] = B.FS10 ** 2                                                                # R6
    bh = B[B.year.between(2006, 2024)].groupby("idrssd").heat.mean()                         # R7: nhiệt trung bình của chính ngân hàng
    B["hot"] = B.idrssd.map((bh > bh.median()).astype(float)).to_numpy(); B["cold"] = 1.0 - B.hot
    crb = B.drop_duplicates("idrssd").set_index("idrssd").cr                                 # R11b: mức bảo hiểm chuẩn hoá
    B["INS"] = (B.cr - crb.mean()) / crb.std(); B["FS10xINS"] = B.FS10 * B.INS
    W, G, gy, sd = get_W(); rows = np.arange(len(B))
    nn = np.diff(W.indptr); B["ncty_l1"] = np.where(nn > 0, nn, np.nan)                     # R12: số hạt có tiền gửi tại t−1
    B["multi"] = (B.ncty_l1 >= 2).astype(float); B["single"] = (B.ncty_l1 == 1).astype(float)
    cty = np.sort(pd.to_numeric(pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips"]).county_fips.unique()).astype(int))
    _C["Gp"] = county_matrix(TAB / "ppt_county_year.parquet", "ppt_season_z", cty, gy)       # R9: mưa cấp hạt
    rb, _ = wmean_rows(W, _C["Gp"], rows, yrs); B["rain_rb"] = rb
    Gy = county_matrix(f"{ROOT}/_claude_pap/out/county_panel.parquet", "y_lncrop", cty, gy)  # R1: ln doanh thu trồng trọt cấp hạt
    yb, cv = wmean_rows(W, Gy, rows, yrs); B["CROPb"] = np.where(cv >= 0.5, yb, np.nan)
    pre = pd.read_parquet(EXPO).reset_index(); pre["idrssd"] = pd.to_numeric(pre.idrssd).astype(B.idrssd.dtype)
    B["fs_pre_last"] = B.idrssd.map(pre.set_index("idrssd").pre_last_year).to_numpy()
    if FAKE is not None:                                  # hoán vị mọi outcome dùng ở đây trong năm × ag25 (như kiểm thử v3, P2)
        yc = [c for c in B.columns if V._YRE.match(c)] + ["ALLr_h0", "ALLr_h1", "CROPb"]
        rng = np.random.default_rng(2900 + FAKE)
        for _, g in B.groupby(["year", "ag25"]).groups.items():
            g = np.asarray(g); p = rng.permutation(g); B.loc[g, yc] = B.loc[p, yc].to_numpy()
    _B["B"] = B; return B

# ---------------------------------------------------------------- thống kê và biến thể
BASE = dict(mults=list(LIN), bases=list(LIN), ctrl=RAIN + BANK_CTRL, xctrl=[], lag=False, rain=False, hdiv=False, need=[], mask=None,
            fs=None, target=0, perm=True, kind="C", opts={})

def S(name, C=None, var=None, hs=None, w=None, common=None, **kw):
    base = V._T[C] if C in V._T else {}
    st = dict(BASE); st.update(name=name, C=C, var=var or (CONFIG["VAR"].get(C) if C else None),
                               hs=hs if hs is not None else base.get("hs", [0]), w=w if w is not None else base.get("w", [1.0]),
                               common=base.get("common", False) if common is None else common)
    st.update(kw); return st

def stats():
    L = []
    # R1: first stage cấp ngân hàng (mọi ngân hàng, chỉ nhiệt, mưa, FE)
    L.append(S("R1", kind="B", var="CROPb", hs=[0], w=[1.0], years=(2007, 2022), mults=[], bases=[], ctrl=list(RAIN)))
    for C in FAMILY:
        L.append(S(f"M_{C}", C, perm=False))                                                # kiểm: tái lập θ chính của v3
        L.append(S(f"R3o_{C}", C, need=["FS10_0506"], perm=False))                          # R3: FS gốc trên mẫu đã cắt
        L.append(S(f"R3a_{C}", C, need=["FS10_0506"], fs="FS10_0506", perm=False))          # R3: FS 2005–2006
        L.append(S(f"R8o_{C}", C, need=["FS10_l1"], perm=False))                            # R8: FS gốc trên cùng mẫu
        L.append(S(f"R8a_{C}", C, need=["FS10_l1"], fs="FS10_l1", perm=False))              # R8: FS tại t−1
        L.append(S(f"R9_{C}", C, ctrl=list(BANK_CTRL), rain=True, need=["rain_rb"]))        # R9: hoán vị cả nhiệt và mưa
        pre = f"PRE_{CONFIG['VAR'][C]}_m2"
        L.append(S(f"R10o_{C}", C, need=[pre, "heat_l1", "lagrow"], perm=False))            # R10: gốc trên cùng mẫu
        L.append(S(f"R10_{C}", C, xctrl=[pre], lag=True, need=[pre, "heat_l1", "lagrow"]))  # R10: thêm biến trễ và nhiệt t−1
    for C in ("C1", "C2", "C3", "C5"):                                                       # R4: bỏ từng division, từng năm sốc
        for i, d in enumerate(DIVS): L.append(S(f"R4_{C}_dd{i}", C, opts={"drop_div": d}, perm=False))
        for y in range(CONFIG["T_FIRST"], 2025):
            if y <= V.t_last(C, max(V._T[C]["hs"])): L.append(S(f"R4_{C}_dy{y}", C, opts={"drop_year": y}, perm=False))
    L.append(S("R5", "C2", var="ALLr", hs=[0, 1], w=[.5, .5], common=True, perm=False))   # R5: phần sớm, dự phòng/dư nợ hiện tại
    L.append(S("R5o", "C2", var="ALLOW", hs=[0, 1], w=[.5, .5], common=True, need=["ALLr_h0", "ALLr_h1"], perm=False))
    sq = dict(mults=LIN + ["FS10sq"], bases=LIN + ["FS10sq"], target=4)                     # R6: thêm nhiệt × FS10²
    L.append(S("R6_C1", "C1", **sq)); L.append(S("R6_C4", "C4", **sq))
    L.append(S("R6_P1", kind="B", var="P1", hs=[0], w=[1.0], years=(2007, 2023), **sq))
    for grp in ("hot", "cold"):                                                              # R7: vùng nóng và lạnh
        L.append(S(f"R7{grp}_C1", "C1", mask=grp)); L.append(S(f"R7{grp}_C4", "C4", mask=grp))
        L.append(S(f"R7{grp}_P1", kind="B", var="P1", hs=[0], w=[1.0], years=(2007, 2023), mask=grp))
    L.append(S("R11b", "C4", mults=LIN + ["INS", "FS10xINS"], bases=LIN + ["INS", "FS10xINS"], hdiv=True, need=["INS"], target=5))
    for grp in ("multi", "single"):                                                          # R12: một hạt / nhiều hạt
        L.append(S(f"R12{grp}_AGLt0", "C5", var="AGLt", hs=[0], w=[1.0], mask=grp))
        L.append(S(f"R12{grp}_LIQ0", "C4", mask=grp))
    return L

def designs():
    return [dict(id=f"{st['name']}__h{h}", st=st, h=h) for st in stats() for h in st["hs"]]

def ycol(st, h): return f"{st['var']}_h{h}" if st["kind"] == "C" else st["var"]

def base_frame(B, st, h):
    y = ycol(st, h)
    if st["kind"] == "C": s = V.sample(B, st["C"], y, h, opts=st["opts"])
    else: s = bank_frame(B, y, 0, group=None, years=st["years"], extra_dropna=(["FS10"] + Z_INT) if st["mults"] else [])
    need = list(st["need"]) + (["cr"] if "INS" in st["mults"] else [])
    if need: s = s.dropna(subset=need)
    if st["mask"]: s = s[s[st["mask"]] == 1.0]
    return s

_ROWS = {}
def frame(B, st, h):
    s = base_frame(B, st, h)
    if st["common"] and len(st["hs"]) > 1:
        if st["name"] not in _ROWS:
            idx = None
            for hh in st["hs"]:
                r = base_frame(B, st, hh).index; idx = r if idx is None else idx.intersection(r)
            _ROWS[st["name"]] = idx
        s = s.loc[s.index.intersection(_ROWS[st["name"]])]
    s = s.copy()
    if st["fs"]: s["FS10"] = s[st["fs"]]; s["FS10sq"] = s.FS10 ** 2
    return winsor(s, [ycol(st, h)], CONFIG["WINSOR"])

class G:
    """β nhanh theo FWL: FE ngân hàng + division×năm + biến cố định; cột nhiệt (×mults), [khối t−1], [nhiệt × division], [mưa] được hoán vị."""
    def __init__(self, s, y, st):
        s = s.reset_index(); self.st = st
        bases = st["bases"]; s2, yn = year_ints(s, 2 if bases else 0, bases if bases else None)
        fixed = list(st["ctrl"]) + list(st["xctrl"]) + yn
        self.g = codes(s.idrssd); self.ng = int(self.g.max()) + 1; self.cnt = np.bincount(self.g, minlength=self.ng).astype(float)
        dy = codes(s.div_year); Dd = np.zeros((len(s), int(dy.max()) + 1)); Dd[np.arange(len(s)), dy] = 1.0
        F = self.within(np.column_stack([Dd] + ([s2[fixed].to_numpy(float)] if fixed else [])))
        try: U, sv, _ = np.linalg.svd(F, full_matrices=False)
        except np.linalg.LinAlgError:
            import scipy.linalg as sla; U, sv, _ = sla.svd(F, full_matrices=False, lapack_driver="gesvd")
        self.Q = U[:, sv > sv[0] * 1e-11]
        self.yt = self.resid(self.within(s[y].to_numpy(float)[:, None]))[:, 0]
        self.M = np.column_stack([s[m].to_numpy(float) for m in st["mults"]]) if st["mults"] else np.zeros((len(s), 0))
        self.ML = np.column_stack([s[m].to_numpy(float) for m in LIN]) if st["lag"] else None
        if st["hdiv"]:
            dv = codes(s.division); self.Dv = np.zeros((len(s), int(dv.max()) + 1)); self.Dv[np.arange(len(s)), dv] = 1.0; self.Dv = self.Dv[:, 1:]
        self.rows, self.year = s["index"].to_numpy(), s.year.to_numpy()
        self.lagrows = s["lagrow"].to_numpy().astype(int) if st["lag"] else None
        self.h0 = s.heat.to_numpy(float); self.hl0 = s.heat_l1.to_numpy(float) if st["lag"] else None
        self.r0 = s.rain_rb.to_numpy(float) if st["rain"] else None
        self.n, self.banks, self.sd_y = len(s), int(s.idrssd.nunique()), float(s[y].std())
    def within(self, A):
        A = np.asarray(A, float)
        mu = np.column_stack([np.bincount(self.g, weights=A[:, j], minlength=self.ng) / self.cnt for j in range(A.shape[1])]); return A - mu[self.g]
    def resid(self, A): return A - self.Q @ (self.Q.T @ A)
    def est(self, h, hl=None, r=None):
        cols = [h * self.M[:, j] for j in range(self.M.shape[1])] + [h]
        if self.st["lag"]: cols += [hl * self.ML[:, j] for j in range(self.ML.shape[1])] + [hl]
        if self.st["hdiv"]: cols += [h * self.Dv[:, j] for j in range(self.Dv.shape[1])]
        if self.st["rain"]: cols += [r, r * r]
        Xt = self.resid(self.within(np.column_stack(cols))); k = self.st["target"]
        b = np.linalg.lstsq(Xt, self.yt, rcond=None)[0]
        return float(b[k]), float(1.0 / np.linalg.inv(Xt.T @ Xt)[k, k])

_PIS = []
def pis():
    if not _PIS:
        c = 0
        while len(_PIS) < R:
            rng = np.random.default_rng([CONFIG["SEED_V3"], c]); _PIS.extend(draw_pi(rng, range(2006, 2025)) for _ in range(CONFIG["NPERM"])); c += 1
    return _PIS[:R]

def run(d):
    B = panel(); st, h = d["st"], d["h"]; W, Gm, gy, sd = get_W()
    s = frame(B, st, h); D = G(s, ycol(st, h), st)
    obs, rss0 = D.est(D.h0, D.hl0, D.r0)
    out = dict(id=d["id"], obs=obs, obs_rss=rss0, n=D.n, banks=D.banks, sd_y=D.sd_y, shock_years=int(len(np.unique(D.year))))
    if st["perm"]:
        perm, prss = [], []
        for pi in pis():
            hp = perm_heat(W, Gm, gy, sd, D.rows, D.year, pi)
            hl = perm_heat(W, Gm, gy, sd, D.lagrows, D.year - 1, pi) if st["lag"] else None
            rp = wmean_rows(W, _C["Gp"], D.rows, D.year, pi)[0] if st["rain"] else None
            b_, r_ = D.est(hp, hl, rp); perm.append(b_); prss.append(r_)
        out.update(perm=perm, perm_rss=prss)
    return out

def cmd_worker(w, nw, budget):
    if FAKE is None: guard_real()
    t0 = time.time(); done = 0; mx = 0.0
    for i, d in enumerate(designs()):
        f = f"{JOBD}/{d['id']}.json"
        if i % nw != w or os.path.exists(f): continue
        if time.time() - t0 + max(1.25 * mx, 5) > budget: break
        t1 = time.time(); r = run(d); r["secs"] = time.time() - t1; mx = max(mx, r["secs"] if d["st"]["perm"] else 0)
        json.dump(r, open(f + ".tmp", "w")); os.replace(f + ".tmp", f); done += 1
    left = sum(not os.path.exists(f"{JOBD}/{d['id']}.json") for d in designs())
    print(f"worker {w}/{nw}: xong {done}, còn {left} (toàn bộ), {time.time() - t0:.0f}s")

# ---------------------------------------------------------------- tổng hợp và áp quy tắc
def holm(ps):
    ps = np.asarray(ps, float); o = np.argsort(ps); m = len(ps); adj = np.empty(m); prev = 0.0
    for k, i in enumerate(o): prev = max(prev, min(1.0, (m - k) * ps[i])); adj[i] = prev
    return adj

def wy(obs, TS):
    sv = np.array([t.std(ddof=1) for t in TS]); tobs = np.abs(np.asarray(obs)) / sv
    T = np.column_stack([np.abs(t) / s for t, s in zip(TS, sv)]); order = np.argsort(-tobs); padj = np.zeros(len(obs)); prev = 0.0
    for k, i in enumerate(order):
        p_ = (1 + (T[:, order[k:]].max(axis=1) >= tobs[i]).sum()) / (1 + T.shape[0]); prev = max(prev, p_); padj[i] = prev
    return padj

def cmd_collect():
    J = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f"{JOBD}/*.json")}
    STS = {st["name"]: st for st in stats()}
    def th(name):
        st = STS[name]; ids = [f"{name}__h{h}" for h in st["hs"]]
        if not all(i in J for i in ids): return None
        x = dict(theta=sum(w * J[i]["obs"] for w, i in zip(st["w"], ids)), n=J[ids[0]]["n"], banks=J[ids[0]]["banks"], shock_years=J[ids[0]]["shock_years"])
        if st["perm"]:
            ts = sum(w * np.array(J[i]["perm"]) for w, i in zip(st["w"], ids)); kap = max(1.0, float(np.sqrt(np.median(J[ids[0]]["perm_rss"]) / J[ids[0]]["obs_rss"])))
            sdp = ts.std(ddof=1); sda = sdp * kap
            x.update(ts=ts, sd_perm=sdp, kappa=kap, p=(1 + (np.abs(ts) >= abs(x["theta"])).sum()) / (1 + len(ts)),
                     ci90_lo=x["theta"] - 1.6449 * sda, ci90_hi=x["theta"] + 1.6449 * sda, ci95_lo=x["theta"] - 1.96 * sda, ci95_hi=x["theta"] + 1.96 * sda)
        return x
    rows, V_ = [], []
    def rec(rule, name, x, **kw):
        r = dict(rule=rule, stat=name); r.update({k: v for k, v in (x or {}).items() if k != "ts"}); r.update(kw); rows.append(r)
    main = pd.read_csv(f"{V3RES}/v3_confirmatory.csv").set_index("name") if os.path.exists(f"{V3RES}/v3_confirmatory.csv") else None
    # kiểm tái lập θ chính
    if main is not None:
        dv = {C: th(f"M_{C}")["theta"] - main.loc[C].theta for C in FAMILY if th(f"M_{C}")}
        for C, d_ in dv.items(): rec("CHK", C, th(f"M_{C}"), theta_v3=main.loc[C].theta, diff=d_)
        V_.append("Kiểm tái lập θ chính của v3: |lệch| lớn nhất = " + (f"{max(abs(v) for v in dv.values()):.2e}" if dv else "chưa có"))
    # R1
    x = th("R1")
    if x and "p" in x:
        A = (-0.25 <= x["theta"] <= -0.0625) and x["ci95_hi"] < 0
        br = "A" if A else ("A (lớn hơn cấp hạt)" if (x["theta"] < -0.25 and x["ci95_hi"] < 0) else "B")
        rec("R1", "R1", x, branch=br); V_.append(f"R1: β = {x['theta']:.4f}, CI95 [{x['ci95_lo']:.4f}; {x['ci95_hi']:.4f}], n = {x['n']} → nhánh {br}.")
    # R2
    if main is not None:
        for C in FAMILY:
            m = main.loc[C]; b = max(abs(m.ci90_lo), abs(m.ci90_hi)); rec("R2", C, None, theta=m.theta, min_equiv_bound=b, delta=DELTA[C], ratio=b / DELTA[C])
        if os.path.exists(f"{P2RES}/p2_results.csv"):
            p2 = pd.read_csv(f"{P2RES}/p2_results.csv").set_index("name")
            for C in ("P1", "P2"):
                m = p2.loc[C]; b = max(abs(m.ci90_lo), abs(m.ci90_hi)); rec("R2", C, None, theta=m.theta, min_equiv_bound=b, delta=DELTA[C], ratio=b / DELTA[C])
        V_.append("R2: xem các dòng R2 (biên tương đương nhỏ nhất loại trừ được, so với Δ).")
    # R3, R8, R10 (so cùng mẫu, ngưỡng 0,5Δ)
    for rule, o, a in (("R3", "R3o", "R3a"), ("R8", "R8o", "R8a"), ("R10", "R10o", "R10")):
        flag = []
        for C in FAMILY:
            xo, xa = th(f"{o}_{C}"), th(f"{a}_{C}")
            if not (xo and xa): continue
            dif = xa["theta"] - xo["theta"]; bad = abs(dif) > 0.5 * DELTA[C]
            rec(rule, C, xa, theta_same_sample_orig=xo["theta"], diff=dif, half_delta=0.5 * DELTA[C], problem=bad)
            if bad: flag.append(f"{C} (lệch {dif:+.4f} so với 0,5Δ = {0.5 * DELTA[C]:.4f})")
        V_.append(f"{rule}: " + ("VẤN ĐỀ THẬT ở " + "; ".join(flag) if flag else "không thống kê nào lệch quá 0,5Δ."))
    # R10 thêm: phân loại theo đặc tả có biến trễ
    # R4
    if main is not None:
        fl = []
        for C in ("C1", "C2", "C3", "C5"):
            ds = [n for n in STS if n.startswith(f"R4_{C}_")]
            xs = {n: th(n) for n in ds}; xs = {n: v for n, v in xs.items() if v}
            if not xs: continue
            base = th(f"M_{C}")["theta"]
            dev = {n: v["theta"] - base for n, v in xs.items()}; worst = max(dev, key=lambda n: abs(dev[n]))
            for n, v in xs.items(): rec("R4", n, v, diff=dev[n], half_delta=0.5 * DELTA[C], problem=abs(dev[n]) > 0.5 * DELTA[C])
            bad = [n for n in dev if abs(dev[n]) > 0.5 * DELTA[C]]
            if bad: fl.append(f"{C}: " + ", ".join(bad))
            V_.append(f"R4 {C}: lệch lớn nhất {dev[worst]:+.4f} ({worst}); 0,5Δ = {0.5 * DELTA[C]:.4f}.")
        V_.append("R4: " + ("VẤN ĐỀ THẬT — " + "; ".join(fl) if fl else "không division hay năm nào làm ước lượng điểm dịch chuyển quá nửa ngưỡng Δ."))
    # R5
    x, xo = th("R5"), th("R5o")
    if x:
        ok = x["theta"] <= -0.0065; rec("R5", "R5", x, theta_ALLOW_same_sample=(xo or {}).get("theta"), pass_rule=ok)
        V_.append(f"R5: θ_r = {x['theta']:.4f} ({'≤' if ok else '>'} −0,0065) → " + ("dự phòng giảm không chỉ do dư nợ co lại." if ok else "phần lớn mức giảm dự phòng đi cùng dư nợ co lại; sửa mục 6.2."))
    # R6, R7 (Holm trên ba thống kê)
    for rule, mk in (("R6", lambda C: th(f"R6_{C}")), ("R7", None)):
        res = []
        for C in ("C1", "C4", "P1"):
            if rule == "R6":
                x = mk(C)
                if x and "p" in x: res.append((C, x["theta"], x["p"], x))
            else:
                a, b = th(f"R7hot_{C}"), th(f"R7cold_{C}")
                if a and b and "ts" in a and "ts" in b:
                    d = a["theta"] - b["theta"]; ts = a["ts"] - b["ts"]; p = (1 + (np.abs(ts) >= abs(d)).sum()) / (1 + len(ts))
                    res.append((C, d, p, dict(theta=d, theta_hot=a["theta"], theta_cold=b["theta"], n_hot=a["n"], n_cold=b["n"], p=p)))
        if len(res) == 3:
            adj = holm([r[2] for r in res])
            for (C, t, p, x), pa in zip(res, adj): rec(rule, C, x, p_holm=pa)
            rej = [C for (C, *_), pa in zip(res, adj) if pa < .05]
            msg = {"R6": ("bác tuyến tính theo FarmShare ở " if rej else "không bác được giả định tuyến tính theo FarmShare."),
                   "R7": ("khác biệt vùng nóng – lạnh ở " if rej else "không thấy khác biệt giữa vùng nóng và lạnh.")}[rule]
            V_.append(f"{rule}: " + msg + (", ".join(rej) if rej else ""))
    # R9: phân loại với hoán vị cả mưa
    xs = {C: th(f"R9_{C}") for C in FAMILY}
    if all(v and "ts" in v for v in xs.values()):
        pw = wy([xs[C]["theta"] for C in FAMILY], [xs[C]["ts"] for C in FAMILY]); ch = []
        for C, p_ in zip(FAMILY, pw):
            x = xs[C]; tost = x["ci90_lo"] > -DELTA[C] and x["ci90_hi"] < DELTA[C]
            stt = ("+" if x["theta"] > 0 else "-") if p_ < .05 else ("0" if tost else "?"); old = main.loc[C].status if main is not None else ""
            rec("R9", C, x, p_WY=p_, tost=tost, status=stt, status_main=old)
            if stt != old: ch.append(f"{C}: {old} → {stt}")
        V_.append("R9: " + ("phân loại đổi — " + "; ".join(ch) if ch else "phân loại không đổi khi hoán vị cả nhiệt và mưa."))
    xs = {C: th(f"R10_{C}") for C in FAMILY}
    if all(v and "ts" in v for v in xs.values()):
        pw = wy([xs[C]["theta"] for C in FAMILY], [xs[C]["ts"] for C in FAMILY]); ch = []
        for C, p_ in zip(FAMILY, pw):
            x = xs[C]; tost = x["ci90_lo"] > -DELTA[C] and x["ci90_hi"] < DELTA[C]
            stt = ("+" if x["theta"] > 0 else "-") if p_ < .05 else ("0" if tost else "?"); old = main.loc[C].status if main is not None else ""
            rec("R10_status", C, x, p_WY=p_, tost=tost, status=stt, status_main=old)
            if stt != old: ch.append(f"{C}: {old} → {stt}")
        V_.append("R10 (phân loại): " + ("đổi — " + "; ".join(ch) if ch else "không đổi."))
    # R11b
    x = th("R11b")
    if x and "p" in x:
        rec("R11b", "C4", x); V_.append(f"R11b (thăm dò): hệ số H×FS10×INS = {x['theta']:.4f}, p = {x['p']:.3f} → " +
                                        ("bỏ câu 'không khác theo bảo hiểm'." if x["p"] < .05 else "vẫn không thấy khác biệt theo mức bảo hiểm sau khi cho nhiệt khác theo vùng."))
    # R12
    res = []
    for k in ("AGLt0", "LIQ0"):
        a, b = th(f"R12multi_{k}"), th(f"R12single_{k}")
        if a and b and "ts" in a and "ts" in b:
            d = a["theta"] - b["theta"]; ts = a["ts"] - b["ts"]; p = (1 + (np.abs(ts) >= abs(d)).sum()) / (1 + len(ts))
            res.append((k, d, p, dict(theta=d, theta_multi=a["theta"], theta_single=b["theta"], banks_multi=a["banks"], banks_single=b["banks"], p=p)))
    if len(res) == 2:
        adj = holm([r[2] for r in res])
        for (k, d, p, x), pa in zip(res, adj): rec("R12", k, x, p_holm=pa)
        dA, pA = res[0][1], adj[0]
        V_.append("R12 (thăm dò): " + (("dư nợ NN giảm mạnh hơn ở ngân hàng nhiều hạt, cùng chiều Islam & Singh (2025)." if dA < 0 else "ngược chiều Islam & Singh (2025).")
                                         if pA < .05 else "không thấy khác biệt giữa ngân hàng một hạt và nhiều hạt.") + f" (hiệu AGLt = {dA:+.4f}, p_Holm = {pA:.3f})")
    # mô tả cho R8, R9
    B = panel(); m = B[B.year.between(2007, 2024) & B.heat.notna()]
    ov = float((m.fs_pre_last >= m.year).mean()); dev = float(np.nanmax(np.abs(B.rain_rb - B.ppt_season_z)))
    V_.append(f"R8 mô tả: {ov:.1%} hàng (b, t) 2007–2024 có cửa sổ FarmShare_pre chứa năm t hoặc năm sau t.")
    V_.append(f"R9 mô tả: |mưa dựng lại − mưa trong panel| lớn nhất = {dev:.2e}.")
    O = pd.DataFrame(rows); O.to_csv(f"{OUT}/rob_results.csv", index=False)
    open(f"{OUT}/rob_verdicts.md", "w").write("# Kết luận theo quy tắc R1–R12\n\n" + "\n".join(f"- {v}" for v in V_) + "\n")
    pd.set_option("display.width", 250); print(O.drop(columns=[c for c in O.columns if c.endswith("_rss")], errors="ignore").round(4).to_string(index=False)); print("\n".join(V_))

if __name__ == "__main__":
    c = sys.argv[1]
    if c == "list":
        D = designs(); print(len(D), "hồi quy;", sum(d["st"]["perm"] for d in D), "có hoán vị; R =", R)
    elif c == "worker": cmd_worker(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]))
    elif c == "collect": cmd_collect()
