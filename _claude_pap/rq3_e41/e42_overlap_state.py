"""E42 – kiểm nhanh chồng lấn bão nhiệt đới × ngân hàng nông nghiệp (CẬN TRÊN, theo bang). Lệnh: python3 e42_overlap_state.py <thư mục storm_events>
Hạt được coi là 'có bão' trong năm t nếu BANG của hạt có ≥1 sự kiện bão nhiệt đới (Storm Events) năm t.
Cách này phóng đại phơi nhiễm (cả bang thay vì vùng bị bão), nên số đếm là cận trên."""
import os, sys, glob, re, numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rq3_rob")); import run_rob as R
SE = sys.argv[1]
TROP = ['Hurricane', 'Hurricane (Typhoon)', 'Tropical Storm', 'Tropical Depression', 'Storm Surge/Tide']
ev = []
for f in sorted(glob.glob(f"{SE}/*_d*_c*.csv.gz")):
    y = int(re.search(r'_d(\d{4})_c', f).group(1))
    if not 2005 <= y <= 2024: continue
    d = pd.read_csv(f, usecols=['EVENT_TYPE', 'STATE_FIPS'], low_memory=False)
    s = d[d.EVENT_TYPE.isin(TROP)].STATE_FIPS.dropna().astype(int).unique()
    ev += [(y, int(x)) for x in s]
ev = set(ev)
B = R.panel(); W, G, gy, sd = R.get_W()
cty = np.sort(pd.to_numeric(pd.read_parquet(R.TAB / "heat_county_year.parquet", columns=["county_fips"]).county_fips.unique()).astype(int))
assert W.shape[1] == len(cty), (W.shape, len(cty))
st = cty // 1000
yrs = B.year.to_numpy(); share = np.full(len(B), np.nan)
tot = np.asarray(W.sum(axis=1)).ravel()
for t in np.unique(yrs):
    m = np.array([(int(t), int(s)) in ev for s in st], float)
    r = np.where(yrs == t)[0]
    share[r] = (W[r] @ m) / np.where(tot[r] > 0, tot[r], np.nan)
B = B.assign(trop_share=share)
S = B[B.year.between(2006, 2024) & B.trop_share.notna()]
def summ(g, lab):
    print(f"{lab}: bank-year={len(g)}, NH={g.idrssd.nunique()}, có phơi nhiễm>0: {(g.trop_share>0).mean():.1%} "
          f"({(g.trop_share>0).sum()} bank-year, {g[g.trop_share>0].idrssd.nunique()} NH), >0,5: {(g.trop_share>0.5).mean():.1%}")
summ(S, "Toàn mẫu")
summ(S[S.ag25 == 1], "NH nông nghiệp (ag25)")
print("\nTheo năm, NH ag25 có phơi nhiễm>0,5:")
a = S[S.ag25 == 1]
print(a.groupby("year").apply(lambda g: (g.trop_share > 0.5).sum()).to_string())
fs = S.FS10.to_numpy(); ok = ~np.isnan(fs)
print(f"\nCorr(FS10, trop_share) = {np.corrcoef(fs[ok], S.trop_share.to_numpy()[ok])[0,1]:.3f}")
