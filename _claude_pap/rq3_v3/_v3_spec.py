"""_v3_spec.py — đặc tả RQ3 v3 dùng chung, theo PAP_v3.md (mục ghi trong ngoặc). KHÔNG sửa file v2 nào; chỉ import.
SPEC=main (mặc định): đặc tả xác nhận = đặc tả V2, không có hạn hán (PAP §4).
SPEC=dr            : độ vững R1 = thêm Dr, Dr×FS10, Dr×z; hoán vị CHUNG (Heat, Dr) theo cùng π (PAP §9.1).
Chạy outcome thật + nhiệt thật chỉ khi PAP v3 đã đóng băng (guard_real)."""
import os, sys, json, hashlib, re
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
for _p in (f"{ROOT}/_claude_pap/rq3_v2", f"{ROOT}/_claude_pap/scripts"):
    if _p not in sys.path: sys.path.insert(0, _p)
import numpy as np, pandas as pd                                    # noqa: E402
from _pap_est import fit_lp, bank_frame, RAIN, BANK_CTRL, _permute_within_year   # noqa: E402
from _pap_common import codes, absorb, TAB                          # noqa: E402
from _v2_spec import Z_INT, LIN, year_ints, winsor                  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = f"{ROOT}/_claude_pap/rq3_v3/out/panel_v3.parquet"
SPEC = os.environ.get("SPEC", "main")
assert SPEC in ("main", "dr")

CONFIG = dict(
    VAR={"C1": "NCOc", "C2": "ALLOW", "C3": "PDNAflt", "C4": "LIQ", "C5": "AGLt"},   # PAP §3
    H_C1=6,                      # θ_C1 = β2 của NCO cộng dồn t..t+6
    OUT_LAST=2025,               # năm outcome cuối (Call Report 2025 đủ quý 4); cú sốc t ≤ min(2024, 2025 − h)
    C2_OUT_LAST=2022,            # C2: [t−1, t+h] ⊆ [2006, 2022], bỏ (b,t) có cecl_first ∈ [t, t+h]
    T_FIRST=2007,
    DROUGHT={"main": "none", "dr": "full"}[SPEC],
    RI_DROUGHT={"main": "fixed", "dr": "joint"}[SPEC],
    R=1000, SEED_V3=20261115, NPERM=10,
    WINSOR=0.01,
)
_sf = f"{HERE}/sesoi_v3.json"
SESOI = json.load(open(_sf)) if os.path.exists(_sf) else {}        # {"C1": {"primary": Δ, "alt": Δ, ...}, ...}; sinh bởi sesoi_v3.py

FAMILY = ["C1", "C2", "C3", "C4", "C5"]
# θ = Σ_h w_h β2^{k,h}; common=True: mọi β ước lượng trên mẫu chung ∩_h S_{k,h} (PAP §3.3)
_T = {
    "C1": dict(hs=[CONFIG["H_C1"]], w=[1.0], common=False),
    "C2": dict(hs=[0, 1, 3, 4, 5, 6], w=[-.5, -.5, .25, .25, .25, .25], common=True),
    "C3": dict(hs=[0, 1], w=[.5, .5], common=True),
    "C4": dict(hs=[0], w=[1.0], common=False),
    "C5": dict(hs=[2], w=[1.0], common=False),
}
DIVS = ["East North Central", "East South Central", "Middle Atlantic", "Mountain", "New England", "Pacific", "South Atlantic",
        "West North Central", "West South Central"]


def thetas():
    """Danh sách thống kê: họ xác nhận (grp='main') và độ vững đã đăng ký (grp='rob'; PAP §9)."""
    T = [dict(name=C, C=C, var=CONFIG["VAR"][C], grp="main", opts={}, **_T[C]) for C in FAMILY]
    if SPEC == "main":
        T.append(dict(name="C3_ag", C="C3", var="PDNAag", grp="rob", opts={}, **_T["C3"]))     # R3: thêm vay sản xuất NN (mẫu NH có báo cáo)
        T.append(dict(name="C3_fl", C="C3", var="PDNAfl", grp="rob", opts={}, **_T["C3"]))     # R3: mẫu số dư nợ đất NN
        T.append(dict(name="C1_fl", C="C1", var="NCOfl", grp="rob", opts={}, **_T["C1"]))      # R4: NCO nợ đất NN
        T.append(dict(name="C5_ag", C="C5", var="AGL", grp="rob", opts={}, **_T["C5"]))        # R4: tăng trưởng % sổ NN
        T.append(dict(name="C1_early", C="C1", var="NCOc", grp="desc", opts={}, hs=[1], w=[1.0], common=False))          # mô tả: NCO cộng dồn t..t+1
        T.append(dict(name="C1_late", C="C1", var="NCOc", grp="desc", opts={}, hs=[2, 6], w=[-1.0, 1.0], common=True))   # mô tả: NCO trong t+3..t+6 (mẫu chung)
        for i, d in enumerate(DIVS):                                                           # R2: bỏ từng division (C4)
            T.append(dict(name=f"C4_dd{i}", C="C4", var="LIQ", grp="rob", opts={"drop_div": d}, **_T["C4"]))
        for y in range(CONFIG["T_FIRST"], 2025):                                               # R2: bỏ từng năm (C4)
            T.append(dict(name=f"C4_dy{y}", C="C4", var="LIQ", grp="rob", opts={"drop_year": y}, **_T["C4"]))
    return T


def t_last(C, h):
    return min(2024, (CONFIG["C2_OUT_LAST"] if C == "C2" else CONFIG["OUT_LAST"]) - h)


def drought_cols():
    return {"none": [], "full": ["Dr", "x_Dr_FS10"] + [f"x_Dr_{z}" for z in Z_INT]}[CONFIG["DROUGHT"]]


OUTVARS = ("NCOc", "ALLOW", "PDNAflt", "PDNAfl", "PDNAag", "LIQ", "AGLt", "AGL", "NCOfl")
_YRE = re.compile(r"^(%s)_h\d$|^PRE_|^EXIT_h\d$" % "|".join(OUTVARS))


def load_panel(fake=False, fake_seed=0, fake_beta=0.0):
    """panel_v3 (chỉ cột cần). fake=True: hoán vị CẢ HÀNG outcome v3 trong từng năm × ag25 (như PAP_FAKE của v1/v2), seed cố định;
    fake_beta ≠ 0: gài thêm fake_beta·heat·FS10 vào mọi outcome sau khi hoán vị."""
    import pyarrow.parquet as pq
    allc = pq.ParquetFile(PANEL).schema_arrow.names
    keep = ["idrssd", "year", "division", "hq_state", "hq_county_fips_l1", "hq_lat", "hq_lon", "heat", "ag25", "farmshare_pre",
            "cecl_first", "Dr"] + RAIN + BANK_CTRL + ["FS10"] + Z_INT
    ycols = [c for c in allc if _YRE.match(c)]
    b = pd.read_parquet(PANEL, columns=keep + ycols)
    b["div_year"] = b.division + "_" + b.year.astype(str)
    for z in ["FS10"] + Z_INT: b[f"x_Dr_{z}"] = b["Dr"] * b[z]
    if fake:
        b = _permute_within_year(b, ycols, 300 + fake_seed, strata=("ag25",))
        if fake_beta:
            for c in ycols: b[c] = b[c] + fake_beta * b.heat * b.FS10
    return b


def sample(b, C, y, h, rows=None, t0=None, opts=None):
    """S_{k,h} cho cột outcome y (PAP §3.3): t ∈ [T_FIRST (hoặc t0), t_last(C,h)]; đủ y, heat, mưa, controls, FS10, Z (và Dr nếu SPEC=dr);
    C2 bỏ (b,t) có cecl_first ∈ [t, t+h]. opts: drop_div / drop_year. rows: giới hạn về tập chỉ số (mẫu chung)."""
    s = bank_frame(b, y, 0, group=None, years=(t0 or CONFIG["T_FIRST"], t_last(C, h)), extra_dropna=["FS10"] + Z_INT + drought_cols())
    if C == "C2": s = s[~s.cecl_first.between(s.year, s.year + h)]
    opts = opts or {}
    if "drop_div" in opts: s = s[s.division != opts["drop_div"]]
    if "drop_year" in opts: s = s[s.year != opts["drop_year"]]
    if rows is not None: s = s.loc[s.index.intersection(rows)]
    return s


def common_rows(b, th):
    if not th["common"]: return None
    idx = None
    for h in th["hs"]:
        r = sample(b, th["C"], f"{th['var']}_h{h}", h, opts=th["opts"]).index
        idx = r if idx is None else idx.intersection(r)
    return idx


def make_frame(b, C, y, h, rows=None, p=None, t0=None, opts=None):
    s = sample(b, C, y, h, rows, t0, opts).copy()
    p = CONFIG["WINSOR"] if p is None else p
    if p: s = winsor(s, [y], p)                                     # winsorize y ở 1%/99% TRONG mẫu
    return s


def controls():
    return RAIN + BANK_CTRL + drought_cols()


def regressors(s, hv="heat"):
    """[x_FS10, x_z_size, x_z_liq, x_z_lat, heat, controls..., yi_*] — thứ tự như _v2_spec.fit; β2 = cột 0, β1 = cột len(LIN)."""
    s = s.copy()
    for m in LIN: s["x_" + m] = s[hv] * s[m]
    s, yn = year_ints(s, 2)
    return s, ["x_" + m for m in LIN] + [hv] + controls() + yn


def fit(s, y, se="conley", h=0):
    s2, xs = regressors(s)
    if se == "conley":
        r = fit_lp(s2, y, xs, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon", lag=h + 2)
    else:
        r = fit_lp(s2, y, xs, ["idrssd", "div_year"], se="cluster", cluster="hq_state")
    return r, xs


class V3Design:
    """β nhanh (không SE), chính xác theo FWL, không lặp:
      1) khử FE ngân hàng bằng trừ trung bình theo ngân hàng;
      2) FE division×năm + phần cố định (mưa, controls, năm×gradient) vào ma trận F đã khử FE ngân hàng; lấy cơ sở trực chuẩn Q của F
         bằng SVD (bỏ chiều suy biến); chiếu y và mỗi X lên phần bù của Q.
    Tương đương OLS có FE ngân hàng + div×năm như fit_lp (lệnh CHK kiểm < 1e-8). SPEC=dr: khối hạn hán nằm trong X và được hoán vị cùng nhiệt."""
    def __init__(self, s, y):
        s = s.reset_index()                                  # cột 'index' = chỉ số hàng trong panel
        s2, yn = year_ints(s, 2)
        self.g = codes(s.idrssd); self.ng = int(self.g.max()) + 1
        self.cnt = np.bincount(self.g, minlength=self.ng).astype(float)
        self.joint = CONFIG["RI_DROUGHT"] == "joint"
        fixed = RAIN + BANK_CTRL + yn
        dy = codes(s.div_year); Dd = np.zeros((len(s), int(dy.max()) + 1)); Dd[np.arange(len(s)), dy] = 1.0
        F = self.within(np.column_stack([Dd, s2[fixed].to_numpy(float)]))
        try:
            U, sv, _ = np.linalg.svd(F, full_matrices=False)
        except np.linalg.LinAlgError:                        # gesdd đôi khi không hội tụ: dùng gesvd (chậm hơn, ổn định)
            import scipy.linalg as sla
            U, sv, _ = sla.svd(F, full_matrices=False, lapack_driver="gesvd")
        self.Q = U[:, sv > sv[0] * 1e-11]
        self.yt = self.resid(self.within(s[y].to_numpy(float)[:, None]))[:, 0]
        self.M = np.column_stack([s[m].to_numpy(float) for m in LIN])
        self.rows, self.year = s["index"].to_numpy(), s.year.to_numpy()

    def within(self, A):
        A = np.asarray(A, float)
        mu = np.column_stack([np.bincount(self.g, weights=A[:, j], minlength=self.ng) / self.cnt for j in range(A.shape[1])])
        return A - mu[self.g]

    def resid(self, A):
        return A - self.Q @ (self.Q.T @ A)

    def _xt(self, hvec, drvec=None):
        h = np.asarray(hvec, float)
        cols = [h * self.M[:, j] for j in range(self.M.shape[1])] + [h]
        if self.joint:
            dr = np.asarray(drvec, float)
            cols += [dr] + [dr * self.M[:, j] for j in range(self.M.shape[1])]
        return self.resid(self.within(np.column_stack(cols)))

    def beta(self, hvec, drvec=None):
        return np.linalg.lstsq(self._xt(hvec, drvec), self.yt, rcond=None)[0][: len(LIN) + 1]   # [β2 (x_FS10), γ_size, γ_liq, γ_lat, β1 (heat)]

    def beta_rss(self, hvec, drvec=None):
        """(β, RSS_x): RSS_x = phần biến thiên của cột Heat×FS10 còn lại sau khi khử FE, controls và các cột nhiệt khác.
        Dưới sai số iid, Var(β2) ∝ 1/RSS_x → dùng để so 'đòn bẩy' của nhiệt thật với nhiệt hoán vị (PAP §6.3, hệ số κ)."""
        Xt = self._xt(hvec, drvec)
        bb = np.linalg.lstsq(Xt, self.yt, rcond=None)[0]
        return bb[: len(LIN) + 1], float(1.0 / np.linalg.inv(Xt.T @ Xt)[0, 0])


def guard_real():
    """Chỉ cho chạy outcome thật + nhiệt thật khi có hashes_frozen_v3.json và mọi file trong đó khớp hash."""
    pap = os.path.dirname(HERE)
    f = next((c for c in (f"{pap}/hashes_frozen_v3.json", f"{ROOT}/_claude_pap/hashes_frozen_v3.json") if os.path.exists(c)), None)
    if f is None:
        sys.exit("CHẶN: chưa có hashes_frozen_v3.json (PAP v3 chưa đóng băng). Chỉ được chạy PAP_FAKE=1.")
    d = json.load(open(f))
    for k, v in d["files"].items():
        p = next((c for c in (os.path.join(pap, k), os.path.join(ROOT, k)) if os.path.isfile(c)), None)
        if p is None or hashlib.sha256(open(p, "rb").read()).hexdigest() != v:
            sys.exit(f"CHẶN: {k} không khớp hash đóng băng.")
    for k, v in d.get("data", {}).items():                          # file dữ liệu (ngoài repo) cũng phải khớp
        p = os.path.join(ROOT, k)
        if not os.path.isfile(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != v:
            sys.exit(f"CHẶN: dữ liệu {k} không khớp hash đóng băng.")
