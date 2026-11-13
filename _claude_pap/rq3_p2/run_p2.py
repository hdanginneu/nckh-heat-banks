"""run_p2.py — Giai đoạn 2 (PAP_P2.md). Lệnh:
  python3 run_p2.py worker <w> <nw> <budget_s> [--fake SEED]   chạy các thiết kế (mỗi thiết kế một json)
  python3 run_p2.py collect [--fake SEED]                       tổng hợp θ, p_RI, p_WY, TOST, phân loại
  python3 run_p2.py sesoi                                       tính Δ = 0,10·SD(y)/2,5 trên mẫu đủ điều kiện (không dùng nhiệt)
Dữ liệu thật chỉ chạy được khi mọi hash khớp hashes_frozen_p2.json (guard_real; đóng băng nội bộ).
--fake SEED: hoán vị các cột outcome giai đoạn 2 trong từng năm × ag25 (như kiểm thử v3), để kiểm tỷ lệ bác bỏ sai."""
import os, sys, json, glob, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "rq3_v3"))
os.environ.setdefault("SPEC", "main")
from _v3_spec import *                                   # noqa: F401,F403  (ROOT, load_panel, LIN, RAIN, BANK_CTRL, year_ints, winsor, codes, bank_frame...)
from _v2_ri import build_W, perm_heat, draw_pi
from build_v3 import lookup
HERE = os.path.dirname(os.path.abspath(__file__))   # đặt lại sau import * (_v3_spec cũng có HERE)

ARGS = sys.argv[1:]
FAKE = int(ARGS[ARGS.index("--fake") + 1]) if "--fake" in ARGS else None
R = int(os.environ.get("R_P2", 1000)); SEED = 20261120; YEARS_PI = range(2006, 2025)
OUT = f"{HERE}/results_{'fake_s%d' % FAKE if FAKE is not None else 'real'}"; JOBD = f"{OUT}/jobs"; os.makedirs(JOBD, exist_ok=True)
P1F = f"{ROOT}/_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet"
RIF = f"{ROOT}/_claude_feasibility/out/12_ffiec_ri_rce_bank_year.parquet"
ELIG_SH, ELIG_TA = 0.07, 3e5        # đủ điều kiện báo cáo xác định trước: vay sản xuất NN ≥ 7% dư nợ hoặc tài sản ≥ 300 triệu USD

# ---------- khoá chạy thật ----------
FROZEN = ["PAP_P2.md", "run_p2.py", "sesoi_p2.json"]
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
def guard_real():
    hf = f"{HERE}/hashes_frozen_p2.json"
    assert os.path.exists(hf), "Chưa đóng băng PAP_P2 (chạy freeze_p2.py)."
    H = json.load(open(hf))
    bad = [k for k, v in H.items() if sha(k if os.path.isabs(k) else f"{HERE}/{k}") != v]
    assert not bad, f"Hash không khớp: {bad}"

# ---------- dựng biến ----------
_B = {}
def panel():
    if "B" in _B: return _B["B"]
    B = load_panel(False).reset_index(drop=True)
    P = lookup(B.idrssd.dtype)
    p1 = pd.read_parquet(P1F, columns=["idrssd", "year", "total_assets_kusd", "total_loans_kusd", "ag_production_loans_kusd"] +
                         [f"q{q}_ag_production_loans_kusd" for q in (1, 2, 3, 4)]).drop_duplicates(["idrssd", "year"])
    p1["idrssd"] = pd.to_numeric(p1.idrssd).astype(B.idrssd.dtype)
    ri = pd.read_parquet(RIF); ri["idrssd"] = ri.idrssd.astype(B.idrssd.dtype)
    p1 = p1.merge(ri, on=["idrssd", "year"], how="left").set_index(["idrssd", "year"]).sort_index()
    qs = p1[[f"q{q}_ag_production_loans_kusd" for q in (1, 2, 3, 4)]]
    avg = qs.mean(axis=1).where((qs > 0).all(axis=1))
    p1["YLD"] = 100 * p1.ag_int_ytd / avg                                            # lãi suất hiệu dụng vay sản xuất NN (%/năm)
    p1["AGAVG"] = avg
    p1["elig"] = ((p1.ag_production_loans_kusd / p1.total_loans_kusd >= ELIG_SH) | (p1.total_assets_kusd >= ELIG_TA)) & (p1.ag_production_loans_kusd > 0)
    P = P.join(p1[["YLD", "AGAVG", "ag_int_ytd", "elig", "total_assets_kusd", "dep_trans", "dep_nontrans", "q4_ag_production_loans_kusd"]], how="left")
    perf = P.AGAVG - P.farm_nonaccrual.fillna(0)
    P["YLDp"] = 100 * P.ag_int_ytd / perf.where(perf > 0)                            # R-P1b: mẫu số = dư nợ đang sinh lãi
    P["npap"] = P.farm_pd90 + P.farm_nonaccrual                                      # nợ xấu vay sản xuất NN (90+ và ngừng dồn tích)
    ids, yrs = B.idrssd.to_numpy(), B.year.to_numpy()
    at = lambda col, k: P[col].reindex(pd.MultiIndex.from_arrays([ids, yrs + k])).to_numpy()
    pos = lambda a: np.where(a > 0, a, np.nan)
    # P1: Δ lãi suất t−1 → t+1, mẫu đủ điều kiện tại t−1
    e1 = at("elig", -1) == True                                                      # noqa: E712
    B["P1"] = np.where(e1, at("YLD", 1) - at("YLD", -1), np.nan)
    B["P1_h0"] = np.where(e1, at("YLD", 0) - at("YLD", -1), np.nan)
    B["P1_perf"] = np.where(e1, at("YLDp", 1) - at("YLDp", -1), np.nan)
    B["P1_pl"] = np.where(e1, at("YLD", -1) - at("YLD", -3), np.nan)                 # placebo: t−3 → t−1
    B["P1_exit"] = np.where(e1 & ~np.isnan(at("YLD", -1)), np.isnan(at("YLD", 1)).astype(float), np.nan)   # hao hụt
    agp1 = pos(at("ag_production_loans_kusd", -1))
    B["Q1"] = np.where(e1, 100 * (at("ag_production_loans_kusd", 1) - at("ag_production_loans_kusd", -1)) / agp1, np.nan)
    # P2: Δ nợ xấu vay sản xuất NN t−2 → t, chia dư nợ vay sản xuất NN t−2; mẫu đủ điều kiện tại t−2
    e2 = at("elig", -2) == True                                                      # noqa: E712
    d2 = pos(at("ag_production_loans_kusd", -2))
    B["P2"] = np.where(e2, 100 * (at("npap", 0) - at("npap", -2)) / d2, np.nan)
    d4 = pos(at("ag_production_loans_kusd", -4))
    B["P2_pl"] = np.where(at("elig", -4) == True, 100 * (at("npap", -2) - at("npap", -4)) / d4, np.nan)   # noqa: E712
    # P3: NCO tổng cộng dồn t−1..t+3, chia tổng dư nợ t−2
    L2 = pos(at("total_loans_kusd", -2))
    B["P3"] = 100 * sum(at("nco_tot", k) for k in (-1, 0, 1, 2, 3)) / L2
    L4 = pos(at("total_loans_kusd", -4))
    B["P3_pl"] = 100 * (at("nco_tot", -3) + at("nco_tot", -2)) / L4
    # S1 (mô tả): cơ cấu tiền gửi năm nóng, chia tổng tài sản t−1
    TA1 = pos(at("total_assets_kusd", -1))
    B["S1_trans"] = 100 * (at("dep_trans", 0) - at("dep_trans", -1)) / TA1
    B["S1_nontr"] = 100 * (at("dep_nontrans", 0) - at("dep_nontrans", -1)) / TA1
    # nhiệt và biến kiểm soát của hàng t−1 (cho thiết kế hai năm)
    key = pd.Series(np.arange(len(B)), index=pd.MultiIndex.from_arrays([ids, yrs]))
    lag = key.reindex(pd.MultiIndex.from_arrays([ids, yrs - 1])).to_numpy()
    ok = ~np.isnan(lag); li = np.nan_to_num(lag, nan=0).astype(int)
    B["lagrow"] = np.where(ok, lag, np.nan)
    B["heat_l1"] = np.where(ok, B.heat.to_numpy()[li], np.nan)
    for c in BANK_CTRL: B[c + "_m2"] = np.where(ok, B[c].to_numpy()[li], np.nan)   # giá trị t−2 (= _l1 của hàng t−1)
    if FAKE is not None:
        ycols = ["P1", "P1_h0", "P1_perf", "P1_pl", "P1_exit", "Q1", "P2", "P2_pl", "P3", "P3_pl", "S1_trans", "S1_nontr"]
        B = B.copy(); rng = np.random.default_rng(900 + FAKE)
        for _, g in B.groupby(["year", "ag25"]).groups.items():
            g = np.asarray(g); perm = rng.permutation(g)
            B.loc[g, ycols] = B.loc[perm, ycols].to_numpy()
    _B["B"] = B
    return B

# ---------- thiết kế ----------
TWO = dict(ctrl=[c + "_m2" for c in BANK_CTRL], lag=True)
ONE = dict(ctrl=list(BANK_CTRL), lag=False)
def designs():
    D = [dict(id="P1", y="P1", t=(2007, 2023), **ONE, fam=True), dict(id="P2", y="P2", t=(2007, 2024), **TWO, fam=True),
         dict(id="P1_pl", y="P1_pl", t=(2009, 2024), **ONE), dict(id="P2_pl", y="P2_pl", t=(2009, 2024), **TWO),
         dict(id="P1_exit", y="P1_exit", t=(2007, 2023), **ONE, wins=False),
         dict(id="P1_h0", y="P1_h0", t=(2007, 2024), **ONE), dict(id="Q1", y="Q1", t=(2007, 2023), **ONE),
         dict(id="S1_trans", y="S1_trans", t=(2007, 2024), **ONE), dict(id="S1_nontr", y="S1_nontr", t=(2007, 2024), **ONE),
         dict(id="S1_trans_pre12", y="S1_trans", t=(2007, 2011), **ONE), dict(id="S1_trans_post12", y="S1_trans", t=(2012, 2024), **ONE),
         dict(id="P1_perf", y="P1_perf", t=(2007, 2023), **ONE),
         dict(id="P2_one", y="P2", t=(2007, 2024), ctrl=TWO["ctrl"], lag=False, same_as_lag=True)]
    return D

def frame(d):
    B = panel()
    s = bank_frame(B, d["y"], 0, group=None, years=d["t"], extra_dropna=["FS10"] + Z_INT + d["ctrl"] + (["heat_l1"] if d["lag"] or d.get("same_as_lag") else []))
    if d.get("wins", True): s = winsor(s.copy(), [d["y"]], CONFIG["WINSOR"])
    return s

class D2:
    """β nhanh: FE ngân hàng + division×năm + biến kiểm soát cố định (FWL); khối nhiệt t (và t−1) × {FS10, Z} + nhiệt."""
    def __init__(self, s, d):
        s = s.reset_index(); s2, yn = year_ints(s, 2)
        self.g = codes(s.idrssd); self.ng = int(self.g.max()) + 1; self.cnt = np.bincount(self.g, minlength=self.ng).astype(float)
        dy = codes(s.div_year); Dd = np.zeros((len(s), int(dy.max()) + 1)); Dd[np.arange(len(s)), dy] = 1.0
        F = self.within(np.column_stack([Dd, s2[RAIN + d["ctrl"] + yn].to_numpy(float)]))
        U, sv, _ = np.linalg.svd(F, full_matrices=False); self.Q = U[:, sv > sv[0] * 1e-11]
        self.yt = self.resid(self.within(s[d["y"]].to_numpy(float)[:, None]))[:, 0]
        self.M = np.column_stack([s[m].to_numpy(float) for m in LIN])
        self.rows, self.year, self.lag = s["index"].to_numpy(), s.year.to_numpy(), d["lag"]
        self.lagrows = s["lagrow"].to_numpy().astype(int) if self.lag else None
        self.h0, self.hl0 = s["heat"].to_numpy(float), (s["heat_l1"].to_numpy(float) if self.lag else None)
        self.n, self.banks = len(s), int(s.idrssd.nunique())
    def within(self, A):
        mu = np.column_stack([np.bincount(self.g, weights=A[:, j], minlength=self.ng) / self.cnt for j in range(A.shape[1])]); return A - mu[self.g]
    def resid(self, A): return A - self.Q @ (self.Q.T @ A)
    def beta(self, h, hl=None):
        cols = [h * self.M[:, j] for j in range(self.M.shape[1])] + [h]
        if self.lag: cols += [hl * self.M[:, j] for j in range(self.M.shape[1])] + [hl]
        b = np.linalg.lstsq(self.resid(self.within(np.column_stack(cols))), self.yt, rcond=None)[0]
        return [float(b[0])] + ([float(b[len(LIN) + 1])] if self.lag else [])           # [β(H_t×FS10)] (+ [β(H_{t−1}×FS10)])

def pis():
    out, c = [], 0
    while len(out) < R:
        rng = np.random.default_rng([SEED, c]); out += [draw_pi(rng, YEARS_PI) for _ in range(10)]; c += 1
    return out[:R]

def run(d, W):
    Wm, G, yrs, sd = W; s = frame(d); D = D2(s, d)
    obs = D.beta(D.h0, D.hl0); perm = []
    for pi in pis():
        h = perm_heat(Wm, G, yrs, sd, D.rows, D.year, pi)
        hl = perm_heat(Wm, G, yrs, sd, D.lagrows, D.year - 1, pi) if D.lag else None
        perm.append(D.beta(h, hl))
    return dict(id=d["id"], obs=obs, perm=perm, n=D.n, banks=D.banks, sd_y=float(s[d["y"]].std()), lag=D.lag)

def cmd_worker(w, nw, budget):
    if FAKE is None: guard_real()
    t0 = time.time(); W = build_W(panel()); done = 0
    for i, d in enumerate(designs()):
        f = f"{JOBD}/{d['id']}.json"
        if i % nw != w or os.path.exists(f): continue
        if time.time() - t0 > budget: break
        r = run(d, W); json.dump(r, open(f + ".tmp", "w")); os.replace(f + ".tmp", f); done += 1
    print(f"worker {w}: xong {done}, còn {sum(not os.path.exists(f'{JOBD}/{d[chr(105)+chr(100)]}.json') for d in designs())}, {time.time()-t0:.0f}s")

def cmd_collect():
    S = json.load(open(f"{HERE}/sesoi_p2.json"))
    J = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f"{JOBD}/*.json")}
    rows, TS = [], {}
    for d in designs():
        x = J.get(d["id"])
        if not x: continue
        th = sum(x["obs"]); ts = np.array([sum(p) for p in x["perm"]]); sdp = ts.std(ddof=1)
        r = dict(name=d["id"], theta=th, beta_t=x["obs"][0], beta_t1=(x["obs"][1] if x["lag"] else np.nan), sd_perm=sdp,
                 p_RI=(1 + (np.abs(ts) >= abs(th)).sum()) / (1 + len(ts)), ci90_lo=th - 1.6449 * sdp, ci90_hi=th + 1.6449 * sdp,
                 n=x["n"], banks=x["banks"], sd_y=x["sd_y"], R=len(ts), fam=d.get("fam", False))
        if d["id"] in S: r["sesoi"] = S[d["id"]]; r["tost"] = (r["ci90_lo"] > -S[d["id"]]) & (r["ci90_hi"] < S[d["id"]])
        rows.append(r); TS[d["id"]] = ts
    O = pd.DataFrame(rows); fam = O[O.fam].copy()
    if len(fam) == 2:                                       # Westfall–Young step-down max-|t| trên {P1, P2}
        sv = fam.sd_perm.to_numpy(); tobs = np.abs(fam.theta.to_numpy()) / sv
        T = np.column_stack([np.abs(TS[n]) / s for n, s in zip(fam.name, sv)])
        order = np.argsort(-tobs); padj = np.zeros(len(fam)); prev = 0.0
        for k, i in enumerate(order):
            p_ = (1 + (T[:, order[k:]].max(axis=1) >= tobs[i]).sum()) / (1 + T.shape[0]); prev = max(prev, p_); padj[i] = prev
        fam["p_WY"] = padj
        fam["status"] = [("+" if r.theta > 0 else "-") if r.p_WY < .05 else ("0" if r.tost else "?") for r in fam.itertuples()]
        O = O.merge(fam[["name", "p_WY", "status"]], on="name", how="left")
    O.to_csv(f"{OUT}/p2_results.csv", index=False)
    pd.set_option("display.width", 250); print(O.round(4).to_string(index=False))

def cmd_sesoi():
    """Δ = 0,10·SD(y)/2,5 cho P1, P2; P3 = Δ của C1, SD trên mẫu đủ điều kiện, mọi năm, không điều kiện theo nhiệt (cùng quy ước C4/C5 của PAP v3)."""
    out = {}
    for d in designs():
        if d.get("fam"):
            s = frame(d); out[d["id"] + "_n"] = len(s)
            if d["id"] == "P3":                       # P3 dùng đúng neo của C1 (Lu và Nikolaev 2024): phần tổn thất của một năm, không phụ thuộc độ dài cửa sổ
                out["P3"] = json.load(open(os.path.join(HERE, "..", "rq3_v3", "sesoi_v3.json")))["C1"]["primary"]; out["P3_note"] = "= Δ của C1 (PAP v3)"
            else:
                out[d["id"]] = round(float(0.10 * s[d["y"]].std() / 2.5), 6); out[d["id"] + "_sd"] = round(float(s[d["y"]].std()), 6)
    json.dump(out, open(f"{HERE}/sesoi_p2.json", "w"), indent=1); print(out)

if __name__ == "__main__":
    c = ARGS[0]
    if c == "worker": cmd_worker(int(ARGS[1]), int(ARGS[2]), float(ARGS[3]))
    elif c == "collect": cmd_collect()
    elif c == "sesoi": cmd_sesoi()
