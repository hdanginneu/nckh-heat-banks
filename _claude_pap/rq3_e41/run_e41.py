"""run_e41.py — ước lượng trên mẫu mở rộng E41 (năm sốc 1995–2006), theo PAP_E41.md. Cùng đặc tả V2/v3 của bài:
y = Heat×{FS10, Z} + Heat + mưa + biến kiểm soát t−1 + FE ngân hàng + FE division×năm + năm×{FS10, Z}; θ_C như PAP v3 (_T).
Suy luận: hoán vị năm thời tiết trong 1995–2006 (seed 20261116, khối 10, R = 1000), κ, Westfall–Young trên C1–C5, TOST với Δ của bài.
Lệnh:  python3 run_e41.py list
       python3 run_e41.py worker <w> <nw> <budget_s> [--fake SEED]
       python3 run_e41.py collect [--fake SEED]
Dữ liệu thật chỉ chạy khi hash khớp hashes_frozen_e41.json (freeze_e41.py). --fake: hoán vị outcome trong năm × ag25 (kiểm tỷ lệ bác bỏ sai)."""
import os, sys, json, glob, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
_argv = list(sys.argv); sys.argv = [sys.argv[0]]                       # run_rob/run_p2 đọc --fake từ argv: chặn lại, E41 tự đọc
sys.path.insert(0, os.path.join(HERE, "..", "rq3_rob"))
import run_rob as RB                                                    # dùng lại lớp G (FWL), holm, wy — đã kiểm khớp V3Design
sys.argv = _argv
from run_rob import G, wy, V, np, pd, LIN, Z_INT, RAIN, BANK_CTRL, CONFIG, FAMILY, winsor, bank_frame
from _v2_ri import perm_heat, draw_pi
import scipy.sparse as sp
from e41_common import OUT as DOUT, T_EXT

ARGS = sys.argv[1:]
FAKE = int(ARGS[ARGS.index("--fake") + 1]) if "--fake" in ARGS else None
R = int(os.environ.get("R_E41", 1000)); SEED = 20261116; NPERM = 10
RES = f"{HERE}/results_{'fake_s%d' % FAKE if FAKE is not None else 'real'}"; JOBD = f"{RES}/jobs"; os.makedirs(JOBD, exist_ok=True)
SES = json.load(open(os.path.join(HERE, "..", "rq3_v3", "sesoi_v3.json"))); DELTA = {C: SES[C]["primary"] for C in FAMILY}
MAIN = pd.read_csv(os.path.join(HERE, "..", "rq3_v3", "results_real", "v3_confirmatory.csv")).set_index("name")
FROZEN = ["PAP_E41.md", "run_e41.py", "e41_common.py", "01_extract_cr.py", "03_sod_weights.py", "04_build_panel_ext.py"]

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def guard_real():
    hf = f"{HERE}/hashes_frozen_e41.json"
    assert os.path.exists(hf), "Chưa đóng băng (chạy freeze_e41.py)."
    H = json.load(open(hf)); bad = [k for k, v in H.items() if sha(f"{HERE}/{k}") != v]
    assert not bad, f"Hash không khớp: {bad}"

_B = {}
def panel():
    if "B" in _B: return _B["B"]
    B = pd.read_parquet(f"{DOUT}/panel_e41.parquet")
    if FAKE is not None:
        yc = [c for c in B.columns if V._YRE.match(c)]; rng = np.random.default_rng(4100 + FAKE)
        for _, g in B.groupby(["year", "ag25"]).groups.items():
            g = np.asarray(g); p = rng.permutation(g); B.loc[g, yc] = B.loc[p, yc].to_numpy()
    _B["B"] = B; return B

_W = {}
def get_W():
    if not _W:
        W = sp.load_npz(f"{DOUT}/W_e41.npz").tocsr(); g = np.load(f"{DOUT}/G_e41.npz")
        _W.update(W=W, G=g["G"], gy=g["gy"], sd=float(g["sd"]))
    return _W["W"], _W["G"], _W["gy"], _W["sd"]

BASE = dict(mults=list(LIN), bases=list(LIN), ctrl=RAIN + BANK_CTRL, xctrl=[], lag=False, rain=False, hdiv=False, target=0, perm=True, fs=None, need=[])
def S(name, C, **kw):
    t = V._T[C]; st = dict(BASE); st.update(name=name, C=C, var=CONFIG["VAR"][C], hs=t["hs"], w=t["w"], common=t["common"]); st.update(kw); return st

def stats():
    L = [S(f"E_{C}", C) for C in FAMILY]                                            # E41-1, E41-2: đặc tả chính trên mẫu mở rộng
    for C in FAMILY:                                                                # E41-4: FarmShare tại t−1 (như R8), không hoán vị
        L.append(S(f"E8o_{C}", C, need=["FS10_l1"], perm=False)); L.append(S(f"E8a_{C}", C, need=["FS10_l1"], fs="FS10_l1", perm=False))
    return L

def designs(): return [dict(id=f"{st['name']}__h{h}", st=st, h=h) for st in stats() for h in st["hs"]]

def base_frame(B, st, h):
    y = f"{st['var']}_h{h}"
    s = bank_frame(B, y, 0, group=None, years=T_EXT, extra_dropna=["FS10"] + Z_INT + list(st["need"]))
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
    if st["fs"]: s["FS10"] = s[st["fs"]]
    return winsor(s, [f"{st['var']}_h{h}"], CONFIG["WINSOR"])

_PIS = []
def pis(years):
    if not _PIS:
        c = 0
        while len(_PIS) < R:
            rng = np.random.default_rng([SEED, c]); _PIS.extend(draw_pi(rng, years) for _ in range(NPERM)); c += 1
    return _PIS[:R]

def run(d):
    B = panel(); st, h = d["st"], d["h"]; W, Gm, gy, sd = get_W()
    s = frame(B, st, h); D = G(s, f"{st['var']}_h{h}", st)
    obs, rss0 = D.est(D.h0)
    out = dict(id=d["id"], obs=obs, obs_rss=rss0, n=D.n, banks=D.banks, sd_y=D.sd_y, shock_years=sorted(np.unique(D.year).tolist()))
    if st["perm"]:
        perm, prss = [], []
        for pi in pis(list(range(T_EXT[0], T_EXT[1] + 1))):
            b_, r_ = D.est(perm_heat(W, Gm, gy, sd, D.rows, D.year, pi)); perm.append(b_); prss.append(r_)
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
    print(f"worker {w}/{nw}: xong {done}, còn {left}, {time.time() - t0:.0f}s")

def cmd_collect():
    J = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f"{JOBD}/*.json")}
    STS = {st["name"]: st for st in stats()}
    def th(name):
        st = STS[name]; ids = [f"{name}__h{h}" for h in st["hs"]]
        if not all(i in J for i in ids): return None
        x = dict(theta=sum(w * J[i]["obs"] for w, i in zip(st["w"], ids)), n=J[ids[0]]["n"], banks=J[ids[0]]["banks"],
                 years=f"{J[ids[0]]['shock_years'][0]}–{J[ids[0]]['shock_years'][-1]}")
        if st["perm"]:
            ts = sum(w * np.array(J[i]["perm"]) for w, i in zip(st["w"], ids))
            kap = max(1.0, float(np.sqrt(np.median(J[ids[0]]["perm_rss"]) / J[ids[0]]["obs_rss"]))); sda = ts.std(ddof=1) * kap
            x.update(ts=ts, sd_adj=sda, kappa=kap, p_RI=(1 + (np.abs(ts) >= abs(x["theta"])).sum()) / (1 + len(ts)),
                     ci90_lo=x["theta"] - 1.6449 * sda, ci90_hi=x["theta"] + 1.6449 * sda, ci95_lo=x["theta"] - 1.96 * sda, ci95_hi=x["theta"] + 1.96 * sda,
                     mde80=2.8 * sda)
        return x
    rows, V_ = [], []
    xs = {C: th(f"E_{C}") for C in FAMILY}
    have = [C for C in FAMILY if xs[C] and "ts" in xs[C]]
    if have:
        pw = dict(zip(have, wy([xs[C]["theta"] for C in have], [xs[C]["ts"] for C in have])))
        for C in have:
            x, m = xs[C], MAIN.loc[C]
            tost = x["ci90_lo"] > -DELTA[C] and x["ci90_hi"] < DELTA[C]
            stt = ("+" if x["theta"] > 0 else "-") if pw[C] < .05 else ("0" if tost else "?")
            z = (x["theta"] - m.theta) / np.sqrt(x["sd_adj"] ** 2 + m.sd_adj ** 2)
            rows.append(dict(rule="E41-2", stat=C, **{k: v for k, v in x.items() if k != "ts"}, p_WY=pw[C], delta=DELTA[C], tost=tost, status=stt,
                             theta_main=m.theta, sd_main=m.sd_adj, status_main=m.status, z_diff=z))
        V_.append("E41-2 (phân loại C1–C5 trên mẫu mở rộng, WY trên " + ", ".join(have) + "): " +
                  "; ".join(f"{r['stat']}: {r['status']} (bài: {r['status_main']})" for r in rows))
    # E41-1: C4
    r4 = [r for r in rows if r["stat"] == "C4"]
    if r4:
        r = r4[0]
        if r["theta"] > 0 and r["p_RI"] < .05: v = "TÁI LẬP"
        elif r["theta"] > 0 and abs(r["z_diff"]) < 1.96: v = "CÙNG CHIỀU, CHƯA ĐỦ CHẮC (không khác bài một cách có ý nghĩa)"
        else: v = "KHÔNG TÁI LẬP"
        V_.append(f"E41-1 (C4, kết quả chính): θ = {r['theta']:.4f} [CI95 {r['ci95_lo']:.4f}; {r['ci95_hi']:.4f}], p_RI = {r['p_RI']:.3f}; "
                  f"bài: {r['theta_main']:.4f}; z hiệu = {r['z_diff']:.2f} → {v}.")
    # E41-3: C3 chỉ có từ 2002
    if xs.get("C3"): V_.append(f"E41-3: C3 chỉ ước lượng được trên năm sốc {xs['C3']['years']} (thiếu quá hạn 30–89 ngày trước Call Report 2001).")
    # E41-4: FS tại t−1
    fl = []
    for C in FAMILY:
        xo, xa = th(f"E8o_{C}"), th(f"E8a_{C}")
        if not (xo and xa): continue
        dif = xa["theta"] - xo["theta"]; bad = abs(dif) > 0.5 * DELTA[C]
        rows.append(dict(rule="E41-4", stat=C, theta=xa["theta"], theta_same_sample_orig=xo["theta"], diff=dif, half_delta=0.5 * DELTA[C], problem=bad, n=xa["n"]))
        if bad: fl.append(f"{C} ({dif:+.4f})")
    if fl or any(r["rule"] == "E41-4" for r in rows):
        V_.append("E41-4 (FarmShare t−1): " + ("lệch quá 0,5Δ ở " + "; ".join(fl) if fl else "không thống kê nào lệch quá 0,5Δ."))
    O = pd.DataFrame(rows); O.to_csv(f"{RES}/e41_results.csv", index=False)
    open(f"{RES}/e41_verdicts.md", "w").write("# Kết luận E41 theo PAP_E41.md\n\n" + "\n".join(f"- {v}" for v in V_) + "\n")
    pd.set_option("display.width", 250); print(O.round(4).to_string(index=False)); print("\n".join(V_))

if __name__ == "__main__":
    c = ARGS[0]
    if c == "list":
        D = designs(); print(len(D), "hồi quy;", sum(d["st"]["perm"] for d in D), "có hoán vị; R =", R)
    elif c == "worker": cmd_worker(int(ARGS[1]), int(ARGS[2]), float(ARGS[3]))
    elif c == "collect": cmd_collect()
