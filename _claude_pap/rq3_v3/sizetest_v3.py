"""sizetest_v3.py — nghiệm thu suy luận trên dữ liệu giả (PAP §10). Outcome hoán vị trong từng năm × ag25 với seed giả khác nhau;
chỉ các thiết kế của θ_C1..θ_C5 (SPEC=main). Không cho biết gì về hệ số thật.
  size  : tỷ lệ p_RI < 0,05 qua 5 C × S seed (kỳ vọng 2–9%); tỷ lệ có ít nhất một p_WY < 0,05 (kỳ vọng ≲ 7%); sd hoán vị → MDE80 dự kiến.
  power : gài β = MDE80 của từng C; tỷ lệ |θ̂|/sd > 1,96 (kỳ vọng ≈ 80%) và tỷ lệ p_RI < 0,05 (thấp hơn khi R nhỏ vì p rời rạc).
Lệnh: python3 sizetest_v3.py size|power <seed_đầu> <seed_cuối> <R> <ngân_sách_giây>  |  python3 sizetest_v3.py report"""
import os, sys, json, time, glob
os.environ["PAP_FAKE"] = "1"; os.environ["SPEC"] = "main"
if len(sys.argv) > 4: os.environ["R_FAKE"] = sys.argv[4]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_v3 as RV
from run_v3 import *          # noqa: F401,F403

OUTD = f"{HERE}/results_sizetest"; os.makedirs(OUTD, exist_ok=True)
MAIN = [t for t in thetas() if t["grp"] == "main"]


def one(seed, mode, mde=None):
    B = load_panel(True, 1000 + seed, 0.0); RV._ROWS.clear()
    if mode == "power":                      # gài tín hiệu riêng cho từng C, đúng bằng MDE80 của C đó
        for th in MAIN:
            for h in ([3, 4, 5, 6] if th["name"] == "C2" else range(7)):      # C2: chỉ h ≥ 3 để D dịch đúng β
                c = f"{th['var']}_h{h}"
                if c in B: B[c] = B[c] + mde[th["name"]] * B.heat * B.FS10
    w = get_W(); W, G, yrs, sd = w["W"]; pis = all_pis(); res = {}
    for th in MAIN:
        obs = 0.0; ts = np.zeros(len(pis))
        for wt, h in zip(th["w"], th["hs"]):
            d = [x for x in designs() if x["id"] == f"TH_{th['name']}_{h}"][0]
            D = V3Design(frame_of(B, d), d["y"])
            obs += wt * D.beta(B.loc[D.rows, "heat"].to_numpy())[0]
            ts += wt * np.array([D.beta(perm_heat(W, G, yrs, sd, D.rows, D.year, pi))[0] for pi in pis])
        res[th["name"]] = dict(theta=float(obs), perm=ts.tolist())
    return res


def cmd_run(mode, s0, s1, budget):
    t0 = time.time(); mde = json.load(open(f"{OUTD}/mde_from_size.json")) if mode == "power" else None
    for s in range(s0, s1 + 1):
        f = f"{OUTD}/{mode}_seed{s:03d}.json"
        if os.path.exists(f): continue
        if time.time() - t0 > budget: break
        json.dump(dict(seed=s, R=RV.R, res=one(s, mode, mde)), open(f + ".tmp", "w")); os.replace(f + ".tmp", f)
    print(mode, "đến seed", s, f"{time.time() - t0:.0f}s")


def summarize(mode):
    rows = []
    for f in sorted(glob.glob(f"{OUTD}/{mode}_seed*.json")):
        x = json.load(open(f)); R = x["R"]; TS = {C: np.array(r["perm"]) for C, r in x["res"].items()}; th = {C: r["theta"] for C, r in x["res"].items()}
        sv = {C: TS[C].std(ddof=1) for C in FAMILY}
        p = {C: (1 + (np.abs(TS[C]) >= abs(th[C])).sum()) / (1 + R) for C in FAMILY}
        tobs = np.array([abs(th[C]) / sv[C] for C in FAMILY]); T = np.column_stack([np.abs(TS[C]) / sv[C] for C in FAMILY])
        order = np.argsort(-tobs); padj = np.zeros(5); prev = 0.0
        for k, i in enumerate(order):
            pp = (1 + (T[:, order[k:]].max(axis=1) >= tobs[i]).sum()) / (1 + R); prev = max(prev, pp); padj[i] = prev
        rows.append(dict(seed=x["seed"], R=R, **{f"p_{C}": p[C] for C in FAMILY}, **{f"pWY_{C}": padj[i] for i, C in enumerate(FAMILY)},
                         **{f"sd_{C}": sv[C] for C in FAMILY}, **{f"z_{C}": tobs[i] for i, C in enumerate(FAMILY)}))
    return pd.DataFrame(rows)


def cmd_report():
    out = {}; S = summarize("size")
    if len(S):
        P = S[[f"p_{C}" for C in FAMILY]].to_numpy(); PW = S[[f"pWY_{C}" for C in FAMILY]].to_numpy()
        out["size"] = dict(n_seeds=len(S), R=int(S.R.iloc[0]), reject_rate_pRI_all_C=float((P < .05).mean()), reject_rate_by_C={C: float((S[f"p_{C}"] < .05).mean()) for C in FAMILY},
                           fwer_WY=float((PW < .05).any(axis=1).mean()))
        mde = {C: float(2.8016 * S[f"sd_{C}"].mean()) for C in FAMILY}; out["mde80_expected"] = mde
        if SESOI: out["mde80_over_sesoi_primary"] = {C: mde[C] / SESOI[C]["primary"] for C in FAMILY}
        json.dump(mde, open(f"{OUTD}/mde_from_size.json", "w")); S.to_csv(f"{OUTD}/size_by_seed.csv", index=False)
    Wp = summarize("power")
    if len(Wp):
        out["power"] = dict(n_reps=len(Wp), R=int(Wp.R.iloc[0]), detect_rate_z196_by_C={C: float((Wp[f"z_{C}"] > 1.96).mean()) for C in FAMILY},
                            detect_rate_pRI_by_C={C: float((Wp[f"p_{C}"] < .05).mean()) for C in FAMILY})
        Wp.to_csv(f"{OUTD}/power_by_seed.csv", index=False)
    json.dump(out, open(f"{OUTD}/report.json", "w"), indent=1); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "report": cmd_report()
    else: cmd_run(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[5]))
