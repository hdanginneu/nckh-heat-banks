"""sizetest_v3.py — nghiệm thu code trên dữ liệu giả (Thịnh §12.1–12.2). Không đọc outcome thật theo cách có thể lộ hệ số:
outcome được hoán vị trong từng năm × ag25 với seed giả khác nhau. Chỉ các thiết kế cần cho θ_C1..θ_C5.
  size  : S seed giả, R hoán vị; tỷ lệ p_RI < 0,05 qua các C (kỳ vọng 2–9%) và tỷ lệ có ít nhất một p_WY < 0,05 (kỳ vọng ≲ 7%).
  power : gài β_C = MDE80_C (lấy từ sd hoán vị của lượt size) vào outcome của từng C; tỷ lệ phát hiện p_RI < 0,05 (kỳ vọng ≈ 80% ± 12%).
θ quan sát tính bằng V3Design.beta(heat) — trùng fit_lp đến 1e-11 (lệnh CHK của run_v3.py).
Lệnh: python3 sizetest_v3.py size|power <seed_đầu> <seed_cuối> <R> <ngân_sách_giây>  |  python3 sizetest_v3.py report"""
import os, sys, json, time, glob
os.environ["PAP_FAKE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_v3 import *          # noqa: F401,F403  (FAKE=True nên không qua guard)

OUTD = f"{HERE}/results_sizetest"; os.makedirs(OUTD, exist_ok=True)


def theta_designs():
    out = {}
    for C in FAMILY:
        th = THETA[C]
        out[C] = [d for d in designs() if d[0] in [f"{'TH' if th['common'] else 'LP'}_{C}_{h}" for h in th["hs"]()]]
    return out


def one(seed, R, mode, mde=None):
    B = load_panel(True, 1000 + seed, 0.0)
    if mode == "power":                      # gài tín hiệu riêng cho từng C, đúng bằng MDE80 của C đó
        for C in FAMILY:
            v = CONFIG["VAR"][C]
            hs = [3, 4, 5, 6] if C == "C2" else range(7)     # C2: chỉ h ≥ 3 để D dịch đúng β
            for h in hs:
                if f"{v}_h{h}" in B: B[f"{v}_h{h}"] = B[f"{v}_h{h}"] + mde[C] * B.heat * B.FS10
    w = get_W(); W, G, yrs, sd = w["W"]
    pis = []
    for c in range(max(1, R // CONFIG["NPERM"]) + 1):
        rng = np.random.default_rng([CONFIG["SEED_V3"], c])
        pis += [draw_pi(rng, YEARS_PI) for _ in range(CONFIG["NPERM"])]
    pis = pis[:R]
    res = {}
    for C, ds in theta_designs().items():
        wts = THETA[C]["w"](); obs = 0.0; ts = np.zeros(R)
        for wt, d in zip(wts, ds):
            D = V3Design(frame_of(B, d), d[2])
            obs += wt * D.beta(B.loc[D.rows, "heat"].to_numpy())[0]
            ts += wt * np.array([D.beta(perm_heat(W, G, yrs, sd, D.rows, D.year, pi))[0] for pi in pis])
        res[C] = dict(theta=obs, perm=ts.tolist())
    return res


def cmd_run(mode, s0, s1, R, budget):
    t0 = time.time(); mde = None
    if mode == "power":
        mde = json.load(open(f"{OUTD}/mde_from_size.json"))
    for s in range(s0, s1 + 1):
        f = f"{OUTD}/{mode}_seed{s:03d}.json"
        if os.path.exists(f): continue
        if time.time() - t0 > budget: break
        json.dump(dict(seed=s, R=R, res=one(s, R, mode, mde)), open(f + ".tmp", "w")); os.replace(f + ".tmp", f)
    print(mode, "xong đến", s, f"{time.time() - t0:.0f}s")


def summarize(mode):
    rows = []
    for f in sorted(glob.glob(f"{OUTD}/{mode}_seed*.json")):
        x = json.load(open(f)); R = x["R"]; TS = {}; th = {}
        for C, r in x["res"].items():
            ts = np.array(r["perm"]); TS[C] = ts; th[C] = r["theta"]
        sv = {C: TS[C].std(ddof=1) for C in FAMILY}
        p = {C: (1 + (np.abs(TS[C]) >= abs(th[C])).sum()) / (1 + R) for C in FAMILY}
        tobs = np.array([abs(th[C]) / sv[C] for C in FAMILY]); T = np.column_stack([np.abs(TS[C]) / sv[C] for C in FAMILY])
        order = np.argsort(-tobs); padj = np.zeros(5); prev = 0.0
        for k, i in enumerate(order):
            pp = (1 + (T[:, order[k:]].max(axis=1) >= tobs[i]).sum()) / (1 + R); prev = max(prev, pp); padj[i] = prev
        rows.append(dict(seed=x["seed"], **{f"p_{C}": p[C] for C in FAMILY}, **{f"pWY_{C}": padj[i] for i, C in enumerate(FAMILY)},
                         **{f"sd_{C}": sv[C] for C in FAMILY}))
    return pd.DataFrame(rows)


def cmd_report():
    out = {}
    S = summarize("size")
    if len(S):
        P = S[[f"p_{C}" for C in FAMILY]].to_numpy(); PW = S[[f"pWY_{C}" for C in FAMILY]].to_numpy()
        out["size"] = dict(n_seeds=len(S), reject_rate_pRI_all_C=float((P < .05).mean()), reject_rate_by_C={C: float((S[f"p_{C}"] < .05).mean()) for C in FAMILY},
                           fwer_WY=float((PW < .05).any(axis=1).mean()))
        mde = {C: float(2.8016 * S[f"sd_{C}"].mean()) for C in FAMILY}; out["mde80_from_size"] = mde
        json.dump(mde, open(f"{OUTD}/mde_from_size.json", "w"))
        S.to_csv(f"{OUTD}/size_by_seed.csv", index=False)
    W = summarize("power")
    if len(W):
        out["power"] = dict(n_reps=len(W), detect_rate_by_C={C: float((W[f"p_{C}"] < .05).mean()) for C in FAMILY})
        W.to_csv(f"{OUTD}/power_by_seed.csv", index=False)
    json.dump(out, open(f"{OUTD}/report.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "report": cmd_report()
    else: cmd_run(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]))
