"""run_v22.py — PAP v2.2. python3 run_v22.py"""
import os, sys, numpy as np, pandas as pd, json
ROOT = os.path.expanduser("~/mnt/NCKH - NEU"); OUT = f"{ROOT}/_claude_pap/rq3_v22/results"
sys.path.insert(0, f"{ROOT}/_claude_pap/scripts")
from _pap_common import TAB
D = {"CHI": [19, 17, 18, 26, 55], "KC": [8, 20, 31, 40, 56], "DAL": [48], "MIN": [27, 30, 38, 46], "STL": [5, 29, 21, 47, 28],
     "RICH": [51, 54, 24, 37, 45], "SF": [6, 41, 53, 16, 32, 49, 4]}
h = pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips", "year", "gdd_ex29"])
w = pd.read_csv(f"{ROOT}/_claude_pap/out/rma_coverage_ratio.csv", dtype={"fips": str})[["fips", "crop_rec_0105_usd"]].rename(columns={"fips": "county_fips"})
h = h.merge(w, on="county_fips", how="inner"); h = h[h.crop_rec_0105_usd > 0]
h["st"] = h.county_fips.str[:2].astype(int)
rows = []
for dname, sts in D.items():
    g = h[h.st.isin(sts) & h.year.between(1991, 2025)]
    s = g.groupby("year").apply(lambda x: np.average(x.gdd_ex29, weights=x.crop_rec_0105_usd), include_groups=False)
    rows += [dict(dist=dname, year=y, gdd=v) for y, v in s.items()]
H = pd.DataFrame(rows); H["dev"] = H.gdd - H.groupby("dist").gdd.transform("mean"); H["heat"] = H.dev / H.dev.std()
x = pd.read_excel(f"{ROOT}/data_external/fed_ag_survey/FederalReserveDistrictSurveysofAgCreditConditionsHistoricalDataQ22026.xlsx", "Data")
x = x.replace("---", np.nan); x["year"] = x.Date.str[:4].astype(int); x["q"] = x.Date.str[-1].astype(int)
VARS = {"001": "demand", "002": "funds", "003": "repay", "004": "renew", "005": "collat", "006": "income", "015": "rate_op_fixed"}
L = []
for dname in D:
    for code, nm in VARS.items():
        c = f"{code}{dname}"
        if c in x: L.append(pd.DataFrame({"dist": dname, "year": x.year, "q": x.q, "var": nm, "y": pd.to_numeric(x[c], errors="coerce")}))
S = pd.concat(L).dropna()
def cell(var, q, lag):   # lag=1: Q của năm t+1 gắn với nhiệt năm t
    s = S[(S["var"] == var) & (S.q == q)].copy(); s["year"] = s.year - lag
    return s.merge(H[["dist", "year", "heat"]], on=["dist", "year"]).dropna()
_M = {}
def twfe(s, hv):
    """β của OLS với FE khu vực + năm, khử FE bằng phép chiếu chính xác (ma trận M = I − D(D'D)⁺D', lưu theo mẫu)."""
    key = tuple(zip(s.dist, s.year))
    if key not in _M:
        Dm = np.column_stack([pd.get_dummies(s.dist).to_numpy(float), pd.get_dummies(s.year).to_numpy(float)])
        _M[key] = np.eye(len(s)) - Dm @ np.linalg.pinv(Dm)
    M = _M[key]; y = M @ s.y.values.astype(float); X = M @ s[hv].values.astype(float)
    return float((X @ y) / (X @ X))
years = np.arange(1991, 2026); piv = H.pivot(index="year", columns="dist", values="heat")
rng = np.random.default_rng(20261107); R = 2000; PIS = []
while len(PIS) < R:
    p = rng.permutation(years)
    if (p != years).all(): PIS.append(dict(zip(years, p)))
res = []; perm_store = {}
specs = [(v, 4, 0, "Q4_t") for v in ["demand", "funds", "repay", "renew", "collat", "income", "rate_op_fixed"]] + \
        [(v, 3, 0, "Q3_t") for v in ["demand", "funds", "repay", "renew", "collat", "income"]] + \
        [(v, 1, 1, "Q1_t+1") for v in ["demand", "funds", "repay", "renew", "collat", "income"]] + \
        [(v, 1, 0, "Q1_t_placebo") for v in ["demand", "funds", "repay", "renew", "collat", "income"]]
for v, q, lag, tag in specs:
    s = cell(v, q, lag)
    if len(s) < 30: continue
    b = twfe(s, "heat"); pb = []
    for pi in PIS:
        s2 = s.copy(); s2["hp"] = [piv.loc[pi[yy], dd] if pi[yy] in piv.index else np.nan for yy, dd in zip(s2.year, s2.dist)]
        s2 = s2.dropna(subset=["hp"]); pb.append(twfe(s2, "hp"))
    pb = np.array(pb); perm_store[(v, tag)] = pb
    res.append(dict(var=v, timing=tag, beta=b, sd_perm=pb.std(ddof=1), p_RI=(1 + (np.abs(pb) >= abs(b)).sum()) / (1 + R), n=len(s),
                    districts=s.dist.nunique(), years=f"{s.year.min()}-{s.year.max()}", mean_y=s.y.mean(), sd_y=s.y.std()))
O = pd.DataFrame(res)
fam = ["demand", "funds", "repay", "renew", "collat"]
sub = O[(O.timing == "Q4_t") & O["var"].isin(fam)].reset_index()
T = np.column_stack([np.abs(perm_store[(v, "Q4_t")]) / sd for v, sd in zip(sub["var"], sub.sd_perm)]); tobs = np.abs(sub.beta) / sub.sd_perm
order = np.argsort(-tobs.values); prev = 0; padj = {}
for r_, i in enumerate(order):
    p_ = (1 + (T[:, order[r_:]].max(axis=1) >= tobs.values[i]).sum()) / (1 + R); prev = max(prev, p_); padj[sub.loc[i, "var"]] = prev
O["p_WY"] = [padj.get(v) if t == "Q4_t" else np.nan for v, t in zip(O["var"], O.timing)]
O.to_csv(f"{OUT}/v22_results.csv", index=False); H.to_csv(f"{OUT}/district_heat.csv", index=False)
pd.set_option("display.width", 200); print(O.round(3).to_string(index=False))
print("corr heat với năm 2012:", H[H.year == 2012].set_index("dist").heat.round(2).to_dict())
