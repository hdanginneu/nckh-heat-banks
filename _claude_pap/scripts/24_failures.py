"""24_failures.py — outcome thất bại riêng lẻ (mô tả, chạy MỘT lần, kế hoạch mục 6.4).
Logit: 1{ngân hàng thất bại trong năm t+1} trên Nhiệt(t), mưa z, z², controls t−1, với dummy division×năm (loại các ô không có sự kiện, vì không mang thông tin).
Mẫu: mọi ngân hàng cộng đồng 48 bang + DC, t 2006–2023 (sự kiện FDIC đến 2024); hai phiên bản trong cùng một lần chạy: (a) toàn bộ; (b) bỏ năm thất bại 2009–2012.
SE cluster theo bang trụ sở. Ghi trước: bỏ 2009–2012 chỉ còn khoảng 50 sự kiện ⇒ phần này mô tả, không đủ lực thống kê. Báo cáo tỷ số odds mỗi +1 SD nhiệt.
"""
import statsmodels.api as sm
from _pap_est import *

b = load_bank()
s0 = b[b.year.between(2006, 2023)].dropna(subset=["fail_t1", "heat", "ppt_season_z"] + BANK_CTRL).copy()
s0["div_year"] = s0.division + "_" + s0.year.astype(str)
rows = []
for name, s in (("all_years", s0), ("excl_failyear_2009_2012", s0[~(s0.year + 1).between(2009, 2012)])):
    ev = s.groupby("div_year").fail_t1.sum()
    s = s[s.div_year.isin(ev[ev > 0].index)].copy()
    D = pd.get_dummies(s.div_year, drop_first=True, dtype=float)
    Xm = pd.concat([s[["heat"] + RAIN + BANK_CTRL].reset_index(drop=True), D.reset_index(drop=True)], axis=1)
    Xm = sm.add_constant(Xm)
    m = sm.Logit(s.fail_t1.reset_index(drop=True), Xm).fit(disp=0, maxiter=200, cov_type="cluster", cov_kwds={"groups": codes(s.hq_state)})
    beta, se = float(m.params["heat"]), float(m.bse["heat"])
    row = dict(timestamp=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), family="FAIL", outcome="fail_t1", h=1, spec="logit_divyear", sample=name, beta=beta, se=se,
               ci95_lo=beta - Z95 * se, ci95_hi=beta + Z95 * se, p=float(m.pvalues["heat"]), n=int(len(s)), n_units=int(s.idrssd.nunique()), n_clusters=int(s.hq_state.nunique()), dist="z",
               odds_ratio=float(np.exp(beta)), or_lo=float(np.exp(beta - Z95 * se)), or_hi=float(np.exp(beta + Z95 * se)), n_events=int(s.fail_t1.sum()), converged=bool(m.mle_retvals["converged"]))
    append_spec(row); rows.append(row)
pd.DataFrame(rows).to_csv(RES / "failures.csv", index=False)
print("[FAKE] xong thất bại" if FAKE else pd.DataFrame(rows)[["sample", "odds_ratio", "or_lo", "or_hi", "n_events", "n"]].round(3).to_string(index=False))
log_run(f"24_failures ({'FAKE' if FAKE else 'THẬT'}): {len(rows)} logit, sự kiện {[r['n_events'] for r in rows]}.")
