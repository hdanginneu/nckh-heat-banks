"""_v3_spec.py — đặc tả RQ3 v3 dùng chung (khung code bước S1/S3). Theo PAP_v3_formulas.md của Thịnh (09/11/2026).
KHÔNG sửa file v2 nào; chỉ import. Mọi tham số còn chờ quyết định nằm trong CONFIG và được đánh dấu CHỜ CHỐT.
Cấm trước khi đóng băng: không ước lượng C1–C5 với outcome thật + nhiệt thật (run_v3.py chặn bằng guard_real())."""
import os, sys, json, hashlib
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
for _p in (f"{ROOT}/_claude_pap/rq3_v2", f"{ROOT}/_claude_pap/scripts"):
    if _p not in sys.path: sys.path.insert(0, _p)
import numpy as np, pandas as pd                                    # noqa: E402
from _pap_est import fit_lp, bank_frame, RAIN, BANK_CTRL, _permute_within_year   # noqa: E402
from _pap_common import codes, absorb                               # noqa: E402
from _v2_spec import Z_INT, LIN, year_ints, winsor                  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = f"{ROOT}/_claude_pap/rq3_v3/out/panel_v3.parquet"

# ------------------------------------------------------------------ CONFIG (CHỜ CHỐT trước khi đóng băng)
CONFIG = dict(
    # biến outcome cho từng C (bảng quyết định nhóm A; QA_REPORT_v3 mục 3)
    VAR={"C1": "NCOc", "C2": "ALLOW", "C3": "PDNAflt", "C4": "LIQ", "C5": "AGL"},    # CHỜ CHỐT (A2, A4, A5)
    H_C1=6,                      # CHỜ CHỐT (A1): horizon của θ_C1
    OUT_LAST=2024,               # CHỜ CHỐT: năm outcome cuối (khung v3: 2024; dữ liệu có đến 2025 → cú sốc 2019 cho h=6)
    C2_OUT_LAST=2022,            # C2: cửa sổ [t−1, t+h] ⊆ [2006, 2022] và bỏ (b,t,h) có cecl_first ∈ [t, t+h] (Thịnh §2.4)
    T_FIRST=2007,
    DROUGHT="full",              # CHỜ CHỐT (B3): "none" | "level" (Dr) | "full" (Dr, Dr×FS10, Dr×z)
    RI_DROUGHT="fixed",          # CHỜ CHỐT (B3): "fixed" (giữ Dr như mưa) | "joint" (hoán vị Heat và Dr cùng π)
    R=1000, SEED_V3=20261115, NPERM=10,   # CHỜ CHỐT (B1)
    WINSOR=0.01,
    SESOI={"C1": None, "C2": None, "C3": None, "C4": None, "C5": None},   # CHỜ CHỐT (nhóm C), đơn vị của θ_C
)

# θ_C = Σ_h a_h β2^{k,h} (Thịnh §4); "common": các β ước lượng trên mẫu chung ∩_h S_{k,h}
THETA = {
    "C1": dict(hs=lambda: [CONFIG["H_C1"]], w=lambda: [1.0], common=False),
    "C2": dict(hs=lambda: [0, 1, 3, 4, 5, 6], w=lambda: [-.5, -.5, .25, .25, .25, .25], common=True),
    "C3": dict(hs=lambda: [0, 1], w=lambda: [.5, .5], common=True),
    "C4": dict(hs=lambda: [0], w=lambda: [1.0], common=False),
    "C5": dict(hs=lambda: [2], w=lambda: [1.0], common=False),
}
FAMILY = ["C1", "C2", "C3", "C4", "C5"]


def t_last(C, h):
    return (CONFIG["C2_OUT_LAST"] if C == "C2" else CONFIG["OUT_LAST"]) - h


def drought_cols():
    return {"none": [], "level": ["Dr"], "full": ["Dr", "x_Dr_FS10"] + [f"x_Dr_{z}" for z in Z_INT]}[CONFIG["DROUGHT"]]


def load_panel(fake=False, fake_seed=0, fake_beta=0.0):
    """panel_v3. fake=True: hoán vị CẢ HÀNG outcome v3 trong từng năm × ag25 (như PAP_FAKE của v1/v2), seed cố định.
    fake_beta ≠ 0: gài thêm fake_beta·heat·FS10 vào mọi outcome sau khi hoán vị (kiểm power, Thịnh §12.2)."""
    import pyarrow.parquet as pq
    allc = pq.ParquetFile(PANEL).schema_arrow.names
    keep = ["idrssd", "year", "division", "hq_state", "hq_county_fips_l1", "hq_lat", "hq_lon", "heat", "ag25", "farmshare_pre",
            "cecl_first", "Dr", "Dr3"] + RAIN + BANK_CTRL + ["FS10"] + Z_INT
    pref = tuple(f"{v}_h" for v in CONFIG["VAR"].values()) + ("PRE_", "EXIT_")
    b = pd.read_parquet(PANEL, columns=keep + [c for c in allc if c.startswith(pref)])   # chỉ cột cần (máy 3 GB RAM)
    b["div_year"] = b.division + "_" + b.year.astype(str)
    for z in ["FS10"] + Z_INT:
        b[f"x_Dr_{z}"] = b["Dr"] * b[z]
    if fake:
        ycols = [c for c in b.columns if c.split("_h")[0] in ("NCOc", "ALLOW", "PDNAfl", "PDNAflt", "PDNAag", "LIQ", "AGL", "AGLt", "NCOfl", "NCOag", "EXIT")
                 and "_h" in c] + [c for c in b.columns if c.startswith("PRE_")]
        b = _permute_within_year(b, ycols, 300 + fake_seed, strata=("ag25",))
        if fake_beta:
            for c in ycols: b[c] = b[c] + fake_beta * b.heat * b.FS10
    return b


def base_need():
    return ["FS10"] + Z_INT + drought_cols()


def sample(b, C, y, h, rows=None, t0=None):
    """S_{k,h} cho cột outcome y: t ∈ [T_FIRST (hoặc t0), t_last(C,h)], đủ y, heat, mưa, controls, FS10, Z, hạn hán;
    C2 bỏ (b,t) có cecl_first ∈ [t, t+h]. rows: giới hạn về tập chỉ số này (mẫu chung)."""
    s = bank_frame(b, y, 0, group=None, years=(t0 or CONFIG["T_FIRST"], t_last(C, h)), extra_dropna=base_need())
    if C == "C2":
        s = s[~s.cecl_first.between(s.year, s.year + h)]
    if rows is not None:
        s = s.loc[s.index.intersection(rows)]
    return s


def theta_rows(b, C):
    """Chỉ số hàng của mẫu chung (∩ các h của θ_C) hoặc None nếu θ_C chỉ dùng một h."""
    th = THETA[C]
    if not th["common"]:
        return None
    idx = None
    for h in th["hs"]():
        r = sample(b, C, f"{CONFIG['VAR'][C]}_h{h}", h).index
        idx = r if idx is None else idx.intersection(r)
    return idx


def make_frame(b, C, y, h, rows=None, p=None, t0=None):
    s = sample(b, C, y, h, rows, t0).copy()
    p = CONFIG["WINSOR"] if p is None else p
    if p: s = winsor(s, [y], p)
    return s


def controls():
    return RAIN + BANK_CTRL + drought_cols()


def regressors(s, hv="heat"):
    """[x_FS10, x_z_size, x_z_liq, x_z_lat, heat, controls..., yi_*] — thứ tự như _v2_spec.fit; β2 = cột 0, β1 = cột len(LIN)."""
    s = s.copy()
    for m in LIN: s["x_" + m] = s[hv] * s[m]
    s, yn = year_ints(s, 2)
    xs = ["x_" + m for m in LIN] + [hv] + controls() + yn
    return s, xs


def fit(s, y, se="conley", h=0):
    s2, xs = regressors(s)
    if se == "conley":
        r = fit_lp(s2, y, xs, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon", lag=h + 2)
    else:
        r = fit_lp(s2, y, xs, ["idrssd", "div_year"], se="cluster", cluster="hq_state")
    return r, xs


class V3Design:
    """β nhanh (không SE) cho RI, chính xác theo FWL, không lặp:
      1) khử FE ngân hàng bằng trừ trung bình theo ngân hàng (chính xác);
      2) FE division×năm và phần cố định (mưa, controls, năm×gradient, hạn hán nếu cố định) đưa vào ma trận F đã khử FE ngân hàng;
         lấy cơ sở trực chuẩn Q của F bằng SVD (bỏ chiều suy biến), chiếu y và mỗi X lên phần bù của Q.
    Tương đương hồi quy OLS có FE ngân hàng + div×năm như fit_lp (kiểm bằng lệnh CHK). Dựng trong bộ nhớ, không lưu đĩa."""
    def __init__(self, s, y):
        s = s.reset_index()                                  # cột 'index' = chỉ số hàng trong panel
        s2, yn = year_ints(s, 2)
        self.g = codes(s.idrssd); self.ng = int(self.g.max()) + 1
        self.cnt = np.bincount(self.g, minlength=self.ng).astype(float)
        self.joint = CONFIG["RI_DROUGHT"] == "joint" and CONFIG["DROUGHT"] != "none"
        fixed = RAIN + BANK_CTRL + ([] if self.joint else drought_cols()) + yn
        dy = codes(s.div_year); Dd = np.zeros((len(s), int(dy.max()) + 1)); Dd[np.arange(len(s)), dy] = 1.0
        F = self.within(np.column_stack([Dd, s2[fixed].to_numpy(float)]))
        try:
            U, sv, _ = np.linalg.svd(F, full_matrices=False)
        except np.linalg.LinAlgError:          # gesdd đôi khi không hội tụ (gặp ở 1/20 seed giả): dùng gesvd chậm hơn nhưng ổn định
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

    def beta(self, hvec, drvec=None):
        h = np.asarray(hvec, float)
        cols = [h * self.M[:, j] for j in range(self.M.shape[1])] + [h]
        if self.joint:
            dr = np.asarray(drvec, float)
            cols += [dr] if CONFIG["DROUGHT"] == "level" else [dr] + [dr * self.M[:, j] for j in range(self.M.shape[1])]
        Xt = self.resid(self.within(np.column_stack(cols)))
        return np.linalg.lstsq(Xt, self.yt, rcond=None)[0][: len(LIN) + 1]   # [β2 (x_FS10), γ_size, γ_liq, γ_lat, β1 (heat)]


# ------------------------------------------------------------------ chặn chạy thật trước khi đóng băng
def guard_real():
    """Chỉ cho chạy outcome thật + nhiệt thật khi có hashes_frozen_v3.json và mọi file trong đó khớp hash."""
    hf = f"{ROOT}/_claude_pap/hashes_frozen_v3.json"
    alt = os.path.join(os.path.dirname(HERE), "hashes_frozen_v3.json")
    f = hf if os.path.exists(hf) else alt
    if not os.path.exists(f):
        sys.exit("CHẶN: chưa có hashes_frozen_v3.json (PAP v3 chưa đóng băng). Chỉ được chạy PAP_FAKE=1.")
    d = json.load(open(f)); files = d.get("files", d)
    for k, v in files.items():
        cand = [os.path.join(os.path.dirname(HERE), k), os.path.join(ROOT, "_claude_pap", k), os.path.join(HERE, k)]
        p = next((c for c in cand if os.path.isfile(c)), None)
        if p is None or hashlib.sha256(open(p, "rb").read()).hexdigest() != v:
            sys.exit(f"CHẶN: {k} không khớp hash đóng băng.")
