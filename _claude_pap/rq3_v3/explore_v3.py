"""explore_v3.py — phân tích THĂM DÒ sau đóng băng E1–E4 (POST_FREEZE_ADDENDUM_v3.md). Không thuộc bộ file đóng băng.
Lệnh: python3 explore_v3.py worker <w> <nw> <budget_s> | collect
Cùng đặc tả V2, cùng R = 1000 và dãy hoán vị (SEED_V3) như run_v3; mỗi thiết kế ghi một file json (chạy lại được)."""
import os, sys, time, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SPEC", "main")
from _v3_spec import *                                   # noqa: F401,F403
import scipy.sparse as sp
from _v2_ri import build_W, perm_heat, draw_pi
from build_v3 import lookup

OUT = f"{HERE}/results_explore"; JOBD = f"{OUT}/jobs"; os.makedirs(JOBD, exist_ok=True)
R = int(os.environ.get("R_EXP", CONFIG["R"])); YEARS_PI = range(2006, 2025)
MAIN = {t["name"]: t for t in thetas() if t["grp"] == "main"}


def pis():
    out, c = [], 0
    while len(out) < R:
        rng = np.random.default_rng([CONFIG["SEED_V3"], c]); out += [draw_pi(rng, YEARS_PI) for _ in range(CONFIG["NPERM"])]; c += 1
    return out[:R]


_B = {}
def panel():
    if "B" in _B: return _B["B"]
    B = load_panel(False)
    P = lookup(B.idrssd.dtype)
    idx0 = pd.MultiIndex.from_arrays([B.idrssd.to_numpy(), B.year.to_numpy()])
    at = lambda col, k: pd.Series(P[col].reindex(pd.MultiIndex.from_arrays([idx0.get_level_values(0), idx0.get_level_values(1) + k])).to_numpy(), index=B.index)
    # E2b: mức quá hạn đất NN năm t−1 / dư nợ t−1
    Lt = B.totloans_l1 if "totloans_l1" in B else None
    raw = pd.read_parquet(PANEL, columns=["totloans_l1"]); Lt = raw.totloans_l1.where(raw.totloans_l1 > 0)
    B["pd_lag"] = 100 * at("pdna_fl", -1) / Lt
    # E3: các khoản mục bảng cân đối t và t−1 (theo đúng năm)
    p1 = pd.read_parquet(f"{ROOT}/_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet",
                         columns=["idrssd", "year", "total_assets_kusd", "cash_and_due_kusd", "fed_funds_sold_kusd", "htm_securities_kusd",
                                  "afs_securities_kusd", "total_deposits_kusd", "total_loans_kusd", "farmland_loans_kusd", "ag_production_loans_kusd"]).drop_duplicates(["idrssd", "year"])
    p1["idrssd"] = p1.idrssd.astype(B.idrssd.dtype); p1 = p1.set_index(["idrssd", "year"]).sort_index()
    p1["LA"] = p1[["cash_and_due_kusd", "fed_funds_sold_kusd", "htm_securities_kusd", "afs_securities_kusd"]].fillna(0).sum(axis=1)
    p1["SEC"] = p1[["htm_securities_kusd", "afs_securities_kusd"]].fillna(0).sum(axis=1)
    p1["CASH"] = p1[["cash_and_due_kusd", "fed_funds_sold_kusd"]].fillna(0).sum(axis=1)
    p1["AG"] = p1.farmland_loans_kusd + p1.ag_production_loans_kusd
    p1["NONAG"] = p1.total_loans_kusd - p1.AG
    g = lambda col, k: pd.Series(p1[col].reindex(pd.MultiIndex.from_arrays([idx0.get_level_values(0), idx0.get_level_values(1) + k])).to_numpy(), index=B.index)
    TA1 = g("total_assets_kusd", -1).where(lambda s: s > 0)
    for nm, col in (("dLA", "LA"), ("dTA", "total_assets_kusd"), ("dL", "total_loans_kusd"), ("dAG", "AG"), ("dNONAG", "NONAG"),
                    ("dDEP", "total_deposits_kusd"), ("dSEC", "SEC"), ("dCASH", "CASH")):
        B[f"E3_{nm}_h0"] = 100 * (g(col, 0) - g(col, -1)) / TA1
    B["liq_l1"] = raw.totloans_l1 * 0 + pd.read_parquet(PANEL, columns=["liquidity_ratio_l1"]).liquidity_ratio_l1
    # nhiệt t−1 của cùng ngân hàng (hàng t−1 trong panel)
    key = pd.Series(np.arange(len(B)), index=idx0)
    lag = key.reindex(pd.MultiIndex.from_arrays([idx0.get_level_values(0), idx0.get_level_values(1) - 1]))
    B["lagrow"] = lag.to_numpy(); B["heat_l1"] = np.where(lag.notna(), B.heat.to_numpy()[np.nan_to_num(lag.to_numpy(), nan=0).astype(int)], np.nan)
    # E1: ngân hàng có số liệu ở mọi năm 2006–2025
    yrs = B.groupby("idrssd").year.agg(["min", "max", "count"])
    full = yrs[(yrs["min"] == 2006) & (yrs["max"] == 2024) & (yrs["count"] == 19)].index
    last = B[(B.year == 2024) & (B.alive_h1 == 1)].idrssd if "alive_h1" in B else None
    al = pd.read_parquet(PANEL, columns=["idrssd", "year", "alive_h1"])
    ok25 = set(al[(al.year == 2024) & (al.alive_h1 == 1)].idrssd)
    B["balanced"] = B.idrssd.isin(set(full) & ok25)
    B["cecl_any_early"] = B.cecl_first.le(2022).fillna(False)
    _B["B"] = B
    return B


def designs():
    D = []
    for name in ("C1", "C2", "C3", "C4", "C5"):                      # E1 mẫu cân bằng
        th = MAIN[name]
        for h in th["hs"]: D.append(dict(id=f"E1_{name}_{h}", th=name, C=th["C"], y=f"{th['var']}_h{h}", h=h, sub="balanced", lagheat=False, ctrl=[], t0=None))
    th = MAIN["C3"]                                                   # E2 chẩn đoán placebo C3
    for tag, lh, ct in (("base", False, []), ("lagheat", True, []), ("meanrev", False, ["pd_lag"])):
        for h in th["hs"]: D.append(dict(id=f"E2_{tag}_C3_{h}", th=f"E2_{tag}_C3", C="C3", y=f"PDNAflt_h{h}", h=h, sub=None, lagheat=lh, ctrl=ct, t0=None))
        for m in (2, 3): D.append(dict(id=f"E2_{tag}_PL{m}", th=None, C="C3", y=f"PRE_PDNAflt_m{m}", h=0, sub=None, lagheat=lh, ctrl=ct, t0=2005 + m))
    for nm in ("dLA", "dTA", "dL", "dAG", "dNONAG", "dDEP", "dSEC", "dCASH"):   # E3 tách thanh khoản
        D.append(dict(id=f"E3_{nm}", th=None, C="C4", y=f"E3_{nm}_h0", h=0, sub=None, lagheat=False, ctrl=[], t0=None))
    th = MAIN["C2"]                                                   # E4 bỏ hẳn NH áp dụng CECL sớm
    for h in th["hs"]: D.append(dict(id=f"E4_C2_{h}", th="E4_C2", C="C2", y=f"ALLOW_h{h}", h=h, sub="nocecl", lagheat=False, ctrl=[], t0=None))
    return D


_ROWS = {}
def frame(B, d):
    b = B[B.balanced] if d["sub"] == "balanced" else (B[~B.cecl_any_early] if d["sub"] == "nocecl" else B)
    need = d["ctrl"] + (["heat_l1"] if d["lagheat"] else [])
    if need: b = b.dropna(subset=need)
    thn = d["th"] if d["th"] else None
    rows = None
    base = MAIN.get(d["th"].split("_")[-1] if d["th"] else "", None) if d["th"] else None
    tdef = MAIN.get(d["th"]) or (MAIN[d["th"].split("_")[-1]] if d["th"] else None)
    if tdef is not None and tdef["common"]:
        k = (d["th"], d["sub"], d["lagheat"], tuple(d["ctrl"]))
        if k not in _ROWS:
            idx = None
            for h in tdef["hs"]:
                r = sample(b, d["C"], f"{d['y'].rsplit('_h', 1)[0]}_h{h}", h).index; idx = r if idx is None else idx.intersection(r)
            _ROWS[k] = idx
        rows = _ROWS[k]
    return make_frame(b, d["C"], d["y"], d["h"], rows=rows, t0=d["t0"])


class ExD:
    """Như V3Design nhưng thêm biến kiểm soát cố định (ctrl) và tuỳ chọn khối nhiệt t−1 hoán vị CÙNG π với nhiệt t."""
    def __init__(self, s, y, ctrl, lagheat):
        s = s.reset_index(); s2, yn = year_ints(s, 2)
        self.g = codes(s.idrssd); self.ng = int(self.g.max()) + 1; self.cnt = np.bincount(self.g, minlength=self.ng).astype(float)
        dy = codes(s.div_year); Dd = np.zeros((len(s), int(dy.max()) + 1)); Dd[np.arange(len(s)), dy] = 1.0
        F = self.within(np.column_stack([Dd, s2[RAIN + BANK_CTRL + ctrl + yn].to_numpy(float)]))
        try: U, sv, _ = np.linalg.svd(F, full_matrices=False)
        except np.linalg.LinAlgError:
            import scipy.linalg as sla; U, sv, _ = sla.svd(F, full_matrices=False, lapack_driver="gesvd")
        self.Q = U[:, sv > sv[0] * 1e-11]
        self.yt = self.resid(self.within(s[y].to_numpy(float)[:, None]))[:, 0]
        self.M = np.column_stack([s[m].to_numpy(float) for m in LIN])
        self.rows, self.year, self.lag = s["index"].to_numpy(), s.year.to_numpy(), lagheat
        self.lagrows = s["lagrow"].to_numpy() if lagheat else None
        self.h0, self.hl0 = s["heat"].to_numpy(float), (s["heat_l1"].to_numpy(float) if lagheat else None)
    def within(self, A):
        mu = np.column_stack([np.bincount(self.g, weights=A[:, j], minlength=self.ng) / self.cnt for j in range(A.shape[1])]); return A - mu[self.g]
    def resid(self, A): return A - self.Q @ (self.Q.T @ A)
    def beta(self, h, hl=None):
        cols = [h * self.M[:, j] for j in range(self.M.shape[1])] + [h]
        if self.lag: cols += [hl * self.M[:, j] for j in range(self.M.shape[1])] + [hl]
        X = self.resid(self.within(np.column_stack(cols)))
        return float(np.linalg.lstsq(X, self.yt, rcond=None)[0][0])


_W = {}
def W_():
    if not _W:
        B = panel(); _W["w"] = build_W(B)
    return _W["w"]


def run(d):
    B = panel(); W, G, yrs, sd = W_()
    s = frame(B, d); D = ExD(s, d["y"], d["ctrl"], d["lagheat"])
    obs = D.beta(D.h0, D.hl0); perm = []
    for pi in pis():
        h = perm_heat(W, G, yrs, sd, D.rows, D.year, pi)
        hl = perm_heat(W, G, yrs, sd, D.lagrows.astype(int), D.year - 1, pi) if D.lag else None
        perm.append(D.beta(h, hl))
    return dict(id=d["id"], obs=obs, perm=perm, n=len(s), banks=int(s.idrssd.nunique()), years=int(s.year.nunique()), sd_y=float(s[d["y"]].std()))


def cmd_worker(w, nw, budget):
    t0 = time.time(); done = 0; mx = 0
    for i, d in enumerate(designs()):
        f = f"{JOBD}/{d['id']}.json"
        if i % nw != w or os.path.exists(f): continue
        if time.time() - t0 + max(mx * 1.2, 40) > budget: break
        t1 = time.time(); r = run(d); r["secs"] = time.time() - t1
        json.dump(r, open(f + ".tmp", "w")); os.replace(f + ".tmp", f); done += 1; mx = max(mx, time.time() - t1)
    left = sum(not os.path.exists(f"{JOBD}/{d['id']}.json") for d in designs())
    print(f"worker {w}: xong {done}, còn {left}, {time.time() - t0:.0f}s")


def row(name, obs, ts, extra=None):
    sdp = ts.std(ddof=1)
    r = dict(name=name, theta=obs, sd_perm=sdp, p_RI=(1 + (np.abs(ts) >= abs(obs)).sum()) / (1 + len(ts)), ci90_lo=obs - 1.6449 * sdp, ci90_hi=obs + 1.6449 * sdp, R=len(ts))
    r.update(extra or {}); return r


def cmd_collect():
    J = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f"{JOBD}/*.json")}
    out = []
    for d in designs():
        x = J.get(d["id"])
        if x: out.append(row(d["id"], x["obs"], np.array(x["perm"]), dict(n=x["n"], banks=x["banks"], years=x["years"], sd_y=x["sd_y"], kind="design")))
    for th, base in (("E1_C1", "C1"), ("E1_C2", "C2"), ("E1_C3", "C3"), ("E1_C4", "C4"), ("E1_C5", "C5"), ("E2_base_C3", "C3"), ("E2_lagheat_C3", "C3"),
                     ("E2_meanrev_C3", "C3"), ("E4_C2", "C2")):
        t = MAIN[base]; ids = [f"{th}_{h}" for h in t["hs"]]
        if all(i in J for i in ids):
            o = sum(w * J[i]["obs"] for w, i in zip(t["w"], ids)); ts = sum(w * np.array(J[i]["perm"]) for w, i in zip(t["w"], ids))
            out.append(row(th, o, ts, dict(n=J[ids[0]]["n"], banks=J[ids[0]]["banks"], years=J[ids[0]]["years"], kind="theta", sesoi=SESOI.get(base, {}).get("primary"))))
    O = pd.DataFrame(out); O.to_csv(f"{OUT}/explore_results.csv", index=False)
    pd.set_option("display.width", 220); print(O.round(5).to_string(index=False))


if __name__ == "__main__":
    if sys.argv[1] == "worker": cmd_worker(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]))
    elif sys.argv[1] == "collect": cmd_collect()
    elif sys.argv[1] == "list": print(len(designs()), [d["id"] for d in designs()])
