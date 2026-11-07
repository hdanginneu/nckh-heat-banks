"""T5 — hạ tầng hoán vị năm cho RI: ma trận trọng số footprint W (bank-năm × hạt) và GDD hạt-năm; kiểm tra dựng lại `heat` hiện có.
Hoán vị năm: gdd_perm(b,t) = Σ_c w_{b,t,c}·GDD(c, π(t)) (trọng số năm t THẬT, thời tiết của năm π(t))."""
import sys, os
sys.path.insert(0, os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"))
from _pap_common import *
import pandas as pd, numpy as np, scipy.sparse as sp, json
ROOT = os.path.expanduser("~/mnt/NCKH - NEU"); V2 = f"{ROOT}/_claude_pap/rq3_v2"
b = pd.read_parquet(f"{V2}/out/panel_v2.parquet", columns=["idrssd", "year", "gdd", "heat"])
h = pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips", "year", "gdd_ex29"])
cty = np.sort(h.county_fips.unique()); yrs = np.arange(1981, 2026)
G = h.pivot(index="county_fips", columns="year", values="gdd_ex29").reindex(index=cty, columns=yrs).to_numpy()
print("G shape", G.shape, "NaN", int(np.isnan(G).sum()))
fw = pd.read_parquet(f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet", columns=["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"])
fw = fw[(fw.deposit_weight_l1 > 0) & fw.analysis_year.between(2006, 2024)]
fw["idrssd"] = fw.idrssd.astype(b.idrssd.dtype)
b = b.reset_index(drop=True); b["row"] = np.arange(len(b))
m = fw.merge(b[["idrssd", "year", "row"]], left_on=["idrssd", "analysis_year"], right_on=["idrssd", "year"], how="inner")
m["ci"] = np.searchsorted(cty, m.county_fips.to_numpy())
ok = (m.ci < len(cty)) & (cty[np.minimum(m.ci, len(cty) - 1)] == m.county_fips.to_numpy()); print("share weights with county in G:", ok.mean().round(4))
m = m[ok]
W = sp.csr_matrix((m.deposit_weight_l1.to_numpy(float), (m.row.to_numpy(), m.ci.to_numpy())), shape=(len(b), len(cty)))
sp.save_npz(f"{V2}/out/W_footprint.npz", W); np.save(f"{V2}/out/G_county_gdd.npy", G); np.save(f"{V2}/out/G_years.npy", yrs)
# kiểm tra dựng lại
gh = np.full(len(b), np.nan)
for t in range(2006, 2025):
    r = np.where(b.year.to_numpy() == t)[0]; gh[r] = W[r] @ np.nan_to_num(G[:, t - 1981])
ws = np.asarray(W.sum(axis=1)).ravel()
d = pd.DataFrame({"gdd": b.gdd, "gh": gh, "ws": ws}).dropna()
print("corr(gdd, gdd_hat)=", np.corrcoef(d.gdd, d.gh)[0, 1].round(6), "| median ratio", (d.gdd / d.gh).median().round(5), "| max|diff|", (d.gdd - d.gh).abs().max().round(3), "| median wsum", np.median(d.ws).round(4))
sd = json.load(open(f"{ROOT}/_claude_pap/out/bank_scales.json"))["sd_gdd_bank"]
print("sd_gdd", sd, "| max|heat - gh/sd| =", ((b.heat - gh / sd).abs()).max().round(4))
