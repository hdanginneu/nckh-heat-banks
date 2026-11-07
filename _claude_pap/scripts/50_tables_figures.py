"""50_tables_figures.py — bảng (CSV + Markdown) và hình từ results/*.csv. Không ước lượng thêm.
Đầu ra: out/<results|results_fake>/tables/*.csv|md, out/<…>/figs/*.png, out/<…>/numbers_registry.json (mọi số dùng trong báo cáo, để đối chiếu).
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from _pap_est import *

T = RES / "tables"; F = RES / "figs"
T.mkdir(exist_ok=True); F.mkdir(exist_ok=True)


def md(df, fn, floatfmt=3):
    df.to_csv(T / f"{fn}.csv", index=False)
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join((f"{v:.{floatfmt}f}" if isinstance(v, (float, np.floating)) and not pd.isna(v) else ("" if pd.isna(v) else str(v))) for v in r) + " |")
    (T / f"{fn}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def ci(r):
    return f"[{r.ci95_lo:.3f}; {r.ci95_hi:.3f}]"


def three(df, key, fmt_extra=None):
    """Bảng ba cột (toàn mẫu, A, B) cho mỗi hàng khóa."""
    out = []
    for k, g in df.groupby(key, sort=False):
        row = {"kết cục": k}
        for col in ("full", "A", "B"):
            r = g[g["sample"] == col]
            if len(r):
                r = r.iloc[0]
                row[f"{col}: β (SE)"] = f"{r.beta:.3f} ({r.se:.3f})"
                row[f"{col}: CI95"] = ci(r)
                row[f"{col}: N"] = int(r.n)
        out.append(row)
    return pd.DataFrame(out)


reg = {}
# ---- luồng mẫu
for nm, fn in (("county", "county_sample_flow.csv"), ("bank", "bank_sample_flow.csv")):
    md(pd.read_csv(OUT / fn), f"T01_sample_flow_{nm}")

# ---- họ A, B, E
ABE = pd.read_csv(RES / "familyABE.csv")
md(three(ABE.assign(k=ABE.family + ": " + ABE.label.fillna("")), "k"), "T02_family_A_B_E")
fs = json.load(open(RES / "first_stage_usd.json")); reg["first_stage_usd"] = fs

# ---- họ C (TOST)
C = pd.read_csv(RES / "familyC.csv")
full = C[C["sample"] == "full"].copy()
tc = full[["outcome", "beta", "se", "tost_ci90_lo", "tost_ci90_hi", "sesoi_y", "sesoi_pass", "sd_y", "sesoi_sd10_pass", "n", "n_units", "n_clusters"]].rename(
    columns={"tost_ci90_lo": "CI90 thấp", "tost_ci90_hi": "CI90 cao", "sesoi_y": "SESOI_y (điểm %)", "sesoi_pass": "tương đương (SESOI)", "sesoi_sd10_pass": "tương đương (±0,10 SD)"})
md(tc, "T03_family_C_main")
md(three(C.assign(k=C.outcome), "k"), "T03b_family_C_three_columns")
dec = json.load(open(RES / "H3_decision.json")); reg["H3_decision"] = dec

# ---- họ D
D = pd.read_csv(RES / "familyD.csv")
md(three(D.assign(k=D.outcome), "k"), "T04_family_D")

# ---- pass-through, H5, thất bại
PT = pd.read_csv(RES / "pass_through.csv"); md(PT, "T05_pass_through")
H5 = pd.read_csv(RES / "H5.csv"); md(H5[["outcome", "sample", "beta", "se", "ci95_lo", "ci95_hi", "predicted_sign", "n"]], "T06_H5")
FL = pd.read_csv(RES / "failures.csv"); md(FL[["sample", "odds_ratio", "or_lo", "or_hi", "n_events", "n", "n_units"]], "T07_failures")

# ---- robustness: tóm tắt theo kết cục
R = pd.read_csv(RES / "robustness.csv")
rob = []
for (fam, h), g in R.groupby(["outcome", "h"], sort=False):
    if fam in ("A", "B", "E1"):
        main = ABE[(ABE.family == fam) & (ABE["sample"] == "full")]
    else:
        src = C if fam.startswith("C") else D
        main = src[(src.outcome == f"{fam}_h{h}") & (src["sample"] == "full")]
    b0 = float(main.beta.iloc[0])
    row = dict(kết_cục=f"{fam}" + ("" if fam in ("A", "B", "E1") else f"_h{h}"), số_đặc_tả=len(g), β_chính=b0, β_min=g.beta.min(), β_max=g.beta.max(),
               cùng_dấu_với_chính=int((np.sign(g.beta) == np.sign(b0)).sum()), CI95_loại_0=int(((g.ci95_lo > 0) | (g.ci95_hi < 0)).sum()))
    if fam.startswith("C"):
        row["đạt_tương_đương_SESOI"] = int(g.sesoi_pass.sum())
    rob.append(row)
md(pd.DataFrame(rob), "T08_robustness_summary")
md(R[["outcome", "h", "spec", "beta", "se", "ci95_lo", "ci95_hi", "n"] + (["sesoi_pass"] if "sesoi_pass" in R.columns else [])], "T08b_robustness_full")

# ---- RW và MDE
if (RES / "romano_wolf.csv").exists():
    md(pd.read_csv(RES / "romano_wolf.csv")[["family", "outcome", "beta", "se", "p", "p_rw", "n_tests_in_family", "B"]], "T09_romano_wolf")
if (OUT / "mde_table.csv").exists():
    md(pd.read_csv(OUT / "mde_table.csv")[["family", "outcome", "n", "sd_y", "se0", "mde80", "mde80_in_sd_y", "equiv_margin_min", "equiv_margin_min_in_sd_y"]], "T10_mde")

# ---- hình: hệ số theo horizon (C, D) kèm vùng SESOI
fig, axes = plt.subplots(1, 4, figsize=(17, 3.8))
for ax, o in zip(axes, ("C1", "C2", "C3", "C4")):
    g = full[full.outcome.str.startswith(o)].sort_values("h")
    ax.errorbar(g.h, g.beta, yerr=[g.beta - g.tost_ci90_lo, g.tost_ci90_hi - g.beta], fmt="o", color="k", capsize=3)
    for h_, s_ in zip(g.h, g.sesoi_y):
        ax.fill_between([h_ - .25, h_ + .25], -s_, s_, color="#9ecae1", alpha=.35)
    ax.axhline(0, color="gray", lw=.7); ax.set_title(f"{o}: CI90 và vùng ±SESOI", fontsize=9); ax.set_xticks(g.h); ax.set_xlabel("h")
fig.tight_layout(); fig.savefig(F / "F1_family_C.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(5, 3.6))
g = D[(D.outcome.str.startswith("D1")) & (D["sample"] == "full")].sort_values("h")
ax.errorbar(g.h, g.beta, yerr=[g.beta - g.ci95_lo, g.ci95_hi - g.beta], fmt="o-", color="#d62728", capsize=3)
ax.axhline(0, color="gray", lw=.7); ax.set_xlabel("h"); ax.set_title("D1: Δ dư nợ vay sản xuất / tổng dư nợ t−1 (điểm %), CI95", fontsize=8); ax.set_xticks(g.h)
fig.tight_layout(); fig.savefig(F / "F2_family_D.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 3.6))
for i, (fam, g) in enumerate(ABE.groupby("family", sort=False)):
    for j, col in enumerate(("full", "A", "B")):
        r = g[g["sample"] == col].iloc[0]
        ax.errorbar(i + (j - 1) * 0.18, r.beta / r.sd_y, yerr=[[(r.beta - r.ci95_lo) / r.sd_y], [(r.ci95_hi - r.beta) / r.sd_y]], fmt="o", color=("k", "#1f77b4", "#ff7f0e")[j], capsize=2,
                    label=col if i == 0 else None)
ax.axhline(0, color="gray", lw=.7); ax.set_xticks(range(ABE.family.nunique())); ax.set_xticklabels(list(dict.fromkeys(ABE.family)))
ax.set_ylabel("β / SD(y)"); ax.legend(fontsize=8); ax.set_title("Họ A, B, E: +1 SD nhiệt, CI95 Conley (đã chia SD của y)", fontsize=8)
fig.tight_layout(); fig.savefig(F / "F3_family_ABE.png", dpi=130); plt.close(fig)

# ---- hình: rừng robustness cho C và D
fig, axes = plt.subplots(2, 5, figsize=(21, 9))
for ax, (o, h) in zip(axes.flat, [(f"C{k}", hh) for k in (1, 2, 3, 4) for hh in (1, 2)] + [("D1", 0), ("D1", 1)]):
    g = R[(R.outcome == o) & (R.h == h)].reset_index(drop=True)
    ax.errorbar(g.beta, range(len(g)), xerr=[g.beta - g.ci95_lo, g.ci95_hi - g.beta], fmt="o", ms=2, lw=.6, color="k")
    ax.axvline(0, color="gray", lw=.7); ax.set_title(f"{o} h={h}: {len(g)} đặc tả", fontsize=8); ax.set_yticks([])
fig.tight_layout(); fig.savefig(F / "F4_robustness_forest.png", dpi=110); plt.close(fig)

reg["files"] = sorted(p.name for p in T.glob("*.csv"))
json.dump(reg, open(RES / "numbers_registry.json", "w"), default=str, ensure_ascii=False, indent=1)
print(f"[{'FAKE' if FAKE else 'THẬT'}] đã tạo {len(reg['files'])} bảng và 4 hình tại {RES}")
log_run(f"50_tables_figures ({'FAKE' if FAKE else 'THẬT'}): {len(reg['files'])} bảng, 4 hình.")
