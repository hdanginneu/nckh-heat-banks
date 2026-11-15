"""checks_d.py — kiểm số liệu cho bài (D33, D34, D35, D39, E46). Chỉ mô tả và chẩn đoán; không đổi kết quả chính nào.
Lệnh: python3 checks_d.py   → in ra màn hình và ghi results_real/checks_d.json"""
import os, sys, json
sys.argv = [sys.argv[0]]
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import run_rob as RR
from run_rob import np, pd, V, BANK_CTRL, RAIN, Z_INT, LIN, bank_frame, winsor, CONFIG
B = RR.panel(); out = {}

# D33: n của C1 (NCOc_h6) và C5 (AGLt_h2) theo từng điều kiện mẫu, để đối chiếu Bảng 1 và Bảng 2
for C, y, h in (("C1", "NCOc_h6", 6), ("C5", "AGLt_h2", 2)):
    t1 = V.t_last(C, h); yr = B.year.between(CONFIG["T_FIRST"], t1); r = {}
    r["y có số liệu, năm sốc %d–%d" % (CONFIG["T_FIRST"], t1)] = int((yr & B[y].notna()).sum())
    r["+ nhiệt, mưa"] = int((yr & B[y].notna() & B.heat.notna() & B.ppt_season_z.notna()).sum())
    r["+ ba biến kiểm soát t−1"] = int((yr & B[[y, "heat", "ppt_season_z"] + BANK_CTRL].notna().all(axis=1)).sum())
    r["+ FS10 và z (= mẫu ước lượng Bảng 2)"] = len(V.sample(B, C, y, h))
    r["mẫu ước lượng, chỉ FarmShare_pre ≥ 25%"] = int(V.sample(B, C, y, h).ag25.sum())
    r["y có số liệu, năm 2006–%d (khung v2)" % t1] = int((B.year.between(2006, t1) & B[y].notna()).sum())
    out[f"D33_{C}"] = r

# D33b: thống kê mô tả của biến kết quả TRÊN CHÍNH mẫu ước lượng (để dựng lại Bảng 1 cho khớp Bảng 2)
tb = {}
for C in V.FAMILY:
    for h in V._T[C]["hs"]:
        y = f"{CONFIG['VAR'][C]}_h{h}"; s_ = V.make_frame(B, C, y, h, rows=V.common_rows(B, dict(V._T[C], C=C, var=CONFIG["VAR"][C], opts={})))
        tb[f"{C} {y}"] = dict(n=len(s_), banks=int(s_.idrssd.nunique()), mean=float(s_[y].mean()), sd=float(s_[y].std()))
out["D33b_table1_from_estimation_samples"] = tb

# D34: dự phòng h = 0 — tách ảnh hưởng của mẫu (năm, bỏ năm áp dụng CECL) và đặc tả; chỉ ước lượng điểm
st = [s for s in RR.stats() if s["name"] == "M_C2"][0]
def b_allow(years, cecl):
    s = bank_frame(B, "ALLOW_h0", 0, group=None, years=years, extra_dropna=["FS10"] + Z_INT)
    if cecl: s = s[~s.cecl_first.between(s.year, s.year)]
    s = winsor(s.copy(), ["ALLOW_h0"], CONFIG["WINSOR"]); return RR.G(s, "ALLOW_h0", st).est(s.heat.to_numpy(float))[0], len(s)
out["D34"] = {f"năm {a}–{b}, bỏ CECL={c}": dict(zip(("beta", "n"), b_allow((a, b), c))) for (a, b) in ((2007, 2022), (2006, 2023), (2007, 2024)) for c in (True, False)}
out["D34"]["ghi chú"] = "v2 (rq3_v2/results/primary_ri_results.csv, dALLOW, level 2): β = −0,00188, p_RI = 0,49, n = 88.287, Δ_v2 = 0,0263"

# D35: FarmShare_pre chồng lên năm sốc
m = B[B.year.between(2007, 2024) & B.heat.notna()]
out["D35"] = dict(share_rows_window_contains_t_or_later=float((m.fs_pre_last >= m.year).mean()),
                  banks_window_ends_2007=int(B.drop_duplicates("idrssd").fs_pre_last.eq(2007).sum()),
                  banks_total=int(B.idrssd.nunique()))

# D39: độ lệch chuẩn của nhiệt (đơn vị SD chung) trước và sau khi khử FE ngân hàng + division×năm, trên mẫu C4
st4 = dict([s for s in RR.stats() if s["name"] == "M_C4"][0]); st4.update(ctrl=[], bases=[], mults=[])
s = V.sample(B, "C4", "LIQ_h0", 0); g = RR.G(s, "LIQ_h0", st4)
hr = g.resid(g.within(s.heat.to_numpy(float)[:, None]))[:, 0]
out["D39"] = dict(sd_heat_raw=float(s.heat.std()), sd_heat_after_FE=float(hr.std()), sd_gdd_bank=float(RR.get_W()[3]))

# E46: cận trên tổn thất (0,047 điểm % dư nợ ở FarmShare 25%) quy ra vốn cấp 1
p1 = pd.read_parquet(RR.P2.P1F, columns=["idrssd", "year", "tier1_capital_kusd", "tier1_leverage_ratio_robust", "total_loans_kusd", "total_assets_kusd"]).drop_duplicates(["idrssd", "year"])
p1["idrssd"] = pd.to_numeric(p1.idrssd).astype(B.idrssd.dtype)
ref = B[(B.farmshare_pre > .15) & (B.farmshare_pre <= .35) & B.year.between(2007, 2024)][["idrssd", "year"]].merge(p1, on=["idrssd", "year"], how="left")
la = (ref.total_loans_kusd / ref.total_assets_kusd).median()
t1f = (ref.tier1_capital_kusd / ref.total_assets_kusd).where(ref.tier1_capital_kusd > 0).median()       # vốn cấp 1 / tổng tài sản
out["E46"] = dict(n=len(ref), median_loans_to_assets=float(la), median_tier1_to_assets=float(t1f),
                  median_tier1_leverage_ratio_robust_raw=float(ref.tier1_leverage_ratio_robust.median()),
                  bound_pp_loans=0.047, bound_pct_of_tier1=float(0.047 / 100 * la / t1f * 100))

os.makedirs(f"{D}/results_real", exist_ok=True)
json.dump(out, open(f"{D}/results_real/checks_d.json", "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps(out, indent=1, ensure_ascii=False, default=float))
