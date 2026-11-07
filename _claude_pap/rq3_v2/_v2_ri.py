"""_v2_ri.py — hoán vị năm thời tiết (randomization inference). heat_perm(b,t) = Σ_c w_{b,t,c} GDD(c, π(t)) / sd_gdd (trọng số footprint năm t THẬT)."""
import json
from _v2_spec import *
from _pap_common import codes, absorb, TAB
import scipy.sparse as sp

def build_W(b):
    h = pd.read_parquet(TAB / "heat_county_year.parquet", columns=["county_fips", "year", "gdd_ex29"])
    cty = np.sort(h.county_fips.unique()); yrs = np.arange(1981, 2026)
    G = h.pivot(index="county_fips", columns="year", values="gdd_ex29").reindex(index=cty, columns=yrs).to_numpy()
    fw = pd.read_parquet(f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet", columns=["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"])
    fw = fw[(fw.deposit_weight_l1 > 0) & fw.analysis_year.between(2006, 2024)].copy(); fw["idrssd"] = fw.idrssd.astype(b.idrssd.dtype)
    k = b[["idrssd", "year"]].reset_index(drop=True); k["row"] = np.arange(len(k))
    m = fw.merge(k, left_on=["idrssd", "analysis_year"], right_on=["idrssd", "year"], how="inner")
    m["ci"] = np.searchsorted(cty, m.county_fips.to_numpy())
    W = sp.csr_matrix((m.deposit_weight_l1.to_numpy(float), (m.row.to_numpy(), m.ci.to_numpy())), shape=(len(k), len(cty)))
    sd = json.load(open(f"{ROOT}/_claude_pap/out/bank_scales.json"))["sd_gdd_bank"]
    return W, G, yrs, sd

def perm_heat(W, G, yrs, sd, rows, years_of_rows, pi_map):
    """heat_perm cho các hàng `rows` (chỉ số hàng trong b) với bản đồ năm pi_map: t -> π(t). Trả mảng theo thứ tự rows."""
    out = np.empty(len(rows)); 
    for t in np.unique(years_of_rows):
        sel = np.where(years_of_rows == t)[0]
        g = G[:, int(pi_map[t]) - 1981]
        out[sel] = (W[rows[sel]] @ g) / sd
    return out

def draw_pi(rng, years):
    years = np.array(years)
    while True:
        pi = rng.permutation(years)
        if (pi != years).all(): return dict(zip(years.tolist(), pi.tolist()))

CACHE = os.path.expanduser("~/rq3cache"); os.makedirs(CACHE, exist_ok=True)   # cache cục bộ trên VM (không đồng bộ OneDrive)

class Design:
    """β nhanh (không SE): FE bank + div×năm; khử FE cho phần cố định MỘT lần; mỗi hoán vị chỉ khử FE cho các cột nhiệt (x_<mults>..., heat)."""
    def __init__(self, rows, g, yt, Ft, M, year, mults):
        self.rows, self.g, self.yt, self.Ft, self.M, self.year, self.mults = rows, g, yt, Ft, M, year, mults
    @classmethod
    def build(cls, s, key, level=2, mults=None, bases=None, extra_ctrl=()):
        y, cond, extra = OUTS[key]
        mults = LIN if mults is None else mults
        rows = s.index.to_numpy(); s = s.reset_index(drop=True)
        s2, yn = year_ints(s, level, bases)
        g = [codes(s.idrssd), codes(s.div_year)]
        F = s2[ctrl_cols(key, extra_ctrl) + yn].to_numpy(float)
        Zf = absorb(np.column_stack([s[y].to_numpy(float), F]), g)
        M = np.column_stack([s[m].to_numpy(float) for m in mults])
        return cls(rows, g, Zf[:, 0], Zf[:, 1:], M, s.year.to_numpy(), list(mults))
    def save(self, path):
        np.savez(path, rows=self.rows, g1=self.g[0], g2=self.g[1], yt=self.yt, Ft=self.Ft, M=self.M, year=self.year, mults=np.array(self.mults))
    @classmethod
    def load(cls, path):
        d = np.load(path, allow_pickle=False)
        return cls(d["rows"], [d["g1"], d["g2"]], d["yt"], d["Ft"], d["M"], d["year"], d["mults"].tolist())
    def beta(self, hvec):
        h = np.asarray(hvec, float)
        X = np.column_stack([h * self.M[:, j] for j in range(self.M.shape[1])] + [h])
        Xt = absorb(X, self.g)
        return np.linalg.lstsq(np.column_stack([Xt, self.Ft]), self.yt, rcond=None)[0][:X.shape[1]]   # [x_<mults>..., heat]
