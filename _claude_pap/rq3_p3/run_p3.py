"""run_p3.py — Vòng cuối (PAP_P3.md): bảo hiểm cây trồng có phải tấm đệm giữa cú sốc nhiệt và ngân hàng không?
So sánh tác động của nhiệt × FarmShare giữa ngân hàng có mức bảo hiểm thấp và cao (mức bảo hiểm cố định 2001–2005).
Lệnh:  python3 run_p3.py worker 0 1 <budget_s> [--fake SEED]   |   python3 run_p3.py collect [--fake SEED]
Dữ liệu thật chỉ chạy khi hash khớp hashes_frozen_p3.json (đóng băng nội bộ)."""
import os, sys, json, glob, time, hashlib
P3DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(P3DIR, "..", "rq3_p2"))
import run_p2 as P2                                       # dùng lại panel, bộ ước lượng D2, dãy hoán vị của giai đoạn 2
from run_p2 import np, pd, ROOT, BANK_CTRL, bank_frame, winsor, CONFIG, Z_INT, build_W, perm_heat

FAKE = P2.FAKE
OUT = f"{P3DIR}/results_{'fake_s%d' % FAKE if FAKE is not None else 'real'}"; JOBD = f"{OUT}/jobs"; os.makedirs(JOBD, exist_ok=True)
COVF = f"{ROOT}/_claude_pap/out/rma_coverage_ratio.csv"
FWF = f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet"
SESOI = json.load(open(os.path.join(P3DIR, "..", "rq3_v3", "sesoi_v3.json")))
SP2 = json.load(open(os.path.join(P3DIR, "..", "rq3_p2", "sesoi_p2.json")))
DELTA = {"I1": SESOI["C3"]["primary"], "I2": SP2["P1"], "I3": SESOI["C4"]["primary"]}   # Δ của biến gốc, dùng cho hiệu thấp − cao
PRED = {"I1": "+", "I2": "+", "I3": "-"}                  # dấu của (thấp − cao) nếu bảo hiểm là tấm đệm

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def guard_real():
    hf = f"{P3DIR}/hashes_frozen_p3.json"
    assert os.path.exists(hf), "Chưa đóng băng PAP_P3 (chạy freeze_p3.py)."
    H = json.load(open(hf)); path = lambda k: k.replace("ROOT:", ROOT) if k.startswith("ROOT:") else f"{P3DIR}/{k}"
    bad = [k for k, v in H.items() if sha(path(k)) != v]; assert not bad, f"Hash không khớp: {bad}"

def bank_coverage():
    """Mức bảo hiểm cấp ngân hàng = Σ_c w_c · CR_c / Σ_c w_c trên các hạt có CR; w = trọng số tiền gửi năm đầu tiên của ngân hàng.
    CR_c = liability RMA TB 2001–05 / doanh thu trồng trọt BEA TB 2001–05 (rma_coverage_ratio.csv), cắt trên ở phân vị 99% của hạt.
    Cần Σ w của các hạt có CR ≥ 0,5, nếu không → NaN."""
    cov = pd.read_csv(COVF, dtype={"fips": str}).set_index("fips")
    cr = cov.coverage_ratio_0105.clip(upper=cov.coverage_ratio_0105.quantile(.99))
    fw = pd.read_parquet(FWF, columns=["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"])
    fw = fw[fw.deposit_weight_l1 > 0]; fw = fw[fw.analysis_year == fw.groupby("idrssd").analysis_year.transform("min")]
    fw["cr"] = fw.county_fips.astype(str).str.zfill(5).map(cr)
    fw["wc"] = fw.deposit_weight_l1.where(fw.cr.notna(), 0.0); fw["wcr"] = fw.wc * fw.cr.fillna(0)
    g = fw.groupby("idrssd")[["wc", "wcr"]].sum()
    out = (g.wcr / g.wc).where(g.wc >= 0.5); out.index = pd.to_numeric(out.index); return out

_B = {}
def panel():
    if "B" in _B: return _B["B"]
    B = P2.panel()
    cr = bank_coverage(); B["cr"] = pd.to_numeric(B.idrssd).map(cr).to_numpy()
    fs = B.drop_duplicates("idrssd"); med = float(fs.loc[fs.farmshare_pre >= 0.10, "cr"].median())   # trung vị trong NH FarmShare ≥ 10%
    ag = B.farmshare_pre >= 0.10
    B["low"] = np.where(B.cr.isna(), np.nan, (B.cr < med).astype(float)); _B["cr_median"] = med
    # Chỉ ngân hàng nông nghiệp (FarmShare ≥ 10%) được chia theo mức bảo hiểm; ngân hàng FarmShare < 10% là nhóm so sánh chung của cả hai bên
    B["in_low"] = (~ag) | (ag & (B.low == 1.0)); B["in_high"] = (~ag) | (ag & (B.low == 0.0))
    B["I1"] = (B["PDNAflt_h0"] + B["PDNAflt_h1"]) / 2      # quá hạn sớm nợ đất NN, TB h = 0, 1 (như C3)
    B["I2"] = B["P1"]                                       # Δ lãi suất vay sản xuất NN t−1 → t+1 (như P1)
    B["I3"] = B["LIQ_h0"]                                   # Δ tỷ lệ thanh khoản năm nóng (như C4)
    if FAKE is not None:                                    # P1 đã được P2 hoán vị; hoán vị thêm I1, I3 cùng kiểu
        rng = np.random.default_rng(1900 + FAKE); B = B.copy()
        for _, g in B.groupby(["year", "ag25"]).groups.items():
            g = np.asarray(g); p = rng.permutation(g); B.loc[g, ["I1", "I3"]] = B.loc[p, ["I1", "I3"]].to_numpy()
    _B["B"] = B; return B

YRS = {"I1": (2007, 2024), "I2": (2007, 2023), "I3": (2007, 2024)}
def designs():
    return [dict(id=f"{k}_{grp}", k=k, y=k, grp=grp, t=YRS[k], ctrl=list(BANK_CTRL), lag=False) for k in ("I1", "I2", "I3") for grp in ("low", "high")]

def frame(d):
    B = panel(); b = B[B["in_" + d["grp"]]]
    s = bank_frame(b, d["y"], 0, group=None, years=d["t"], extra_dropna=["FS10"] + Z_INT + d["ctrl"])
    return winsor(s.copy(), [d["y"]], CONFIG["WINSOR"])

def cmd_worker(budget):
    if FAKE is None: guard_real()
    t0 = time.time(); W = build_W(panel()); Wm, G, yrs, sd = W; done = 0
    for d in designs():
        f = f"{JOBD}/{d['id']}.json"
        if os.path.exists(f): continue
        if time.time() - t0 > budget: break
        s = frame(d); D = P2.D2(s, d); obs = D.beta(D.h0)[0]
        perm = [D.beta(perm_heat(Wm, G, yrs, sd, D.rows, D.year, pi))[0] for pi in P2.pis()]
        json.dump(dict(id=d["id"], obs=obs, perm=perm, n=D.n, banks=D.banks, cr_median=_B["cr_median"]), open(f + ".tmp", "w")); os.replace(f + ".tmp", f); done += 1
    print(f"xong {done}, còn {sum(not os.path.exists(f'{JOBD}/{d[chr(105)+chr(100)]}.json') for d in designs())}, {time.time() - t0:.0f}s")

def cmd_collect():
    J = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f"{JOBD}/*.json")}
    rows, TS = [], {}
    for k in ("I1", "I2", "I3"):
        lo, hi = J.get(f"{k}_low"), J.get(f"{k}_high")
        if not (lo and hi): continue
        th = lo["obs"] - hi["obs"]; ts = np.array(lo["perm"]) - np.array(hi["perm"]); sdp = ts.std(ddof=1)
        r = dict(name=k, theta_low=lo["obs"], theta_high=hi["obs"], diff=th, sd_perm=sdp, p_RI=(1 + (np.abs(ts) >= abs(th)).sum()) / (1 + len(ts)),
                 ci90_lo=th - 1.6449 * sdp, ci90_hi=th + 1.6449 * sdp, delta=DELTA[k], pred=PRED[k], n_low=lo["n"], n_high=hi["n"],
                 p_low=(1 + (np.abs(lo["perm"]) >= abs(lo["obs"])).sum()) / (1 + len(lo["perm"])),
                 p_high=(1 + (np.abs(hi["perm"]) >= abs(hi["obs"])).sum()) / (1 + len(hi["perm"])), cr_median=lo["cr_median"], R=len(ts))
        r["tost"] = (r["ci90_lo"] > -DELTA[k]) & (r["ci90_hi"] < DELTA[k]); rows.append(r); TS[k] = ts
    O = pd.DataFrame(rows)
    if len(O) == 3:                                         # Westfall–Young step-down max-|t| trên ba hiệu
        sv = O.sd_perm.to_numpy(); tobs = np.abs(O["diff"].to_numpy()) / sv
        T = np.column_stack([np.abs(TS[n]) / s for n, s in zip(O.name, sv)])
        order = np.argsort(-tobs); padj = np.zeros(3); prev = 0.0
        for j, i in enumerate(order):
            p_ = (1 + (T[:, order[j:]].max(axis=1) >= tobs[i]).sum()) / (1 + T.shape[0]); prev = max(prev, p_); padj[i] = prev
        O["p_WY"] = padj
        O["status"] = [("+" if r.diff > 0 else "-") if r.p_WY < .05 else ("0" if r.tost else "?") for r in O.itertuples()]
    O.to_csv(f"{OUT}/p3_results.csv", index=False); pd.set_option("display.width", 250); print(O.round(4).to_string(index=False))

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "worker": cmd_worker(float(a[3]))
    elif a[0] == "collect": cmd_collect()
