"""_v2_fast.py — ước lượng nhanh β (không SE) cho hoán vị năm/RI: FE 2 chiều bằng phép chiếu luân phiên; các cột cố định (y, controls, dummy năm×FS) chỉ khử FE MỘT lần."""
from _v2_spec import *
from _pap_common import codes, absorb

def ap_absorb(M, g1, g2, tol=1e-9, maxit=2000):
    M = np.asarray(M, float)
    if M.ndim == 1: M = M[:, None]
    n1, n2 = g1.max() + 1, g2.max() + 1
    c1 = np.bincount(g1, minlength=n1).astype(float); c2 = np.bincount(g2, minlength=n2).astype(float)
    out = np.empty_like(M)
    for j in range(M.shape[1]):
        x = M[:, j].copy()
        for it in range(maxit):
            m1 = np.bincount(g1, weights=x, minlength=n1) / c1; x -= m1[g1]
            m2 = np.bincount(g2, weights=x, minlength=n2) / c2; x -= m2[g2]
            m1b = np.bincount(g1, weights=x, minlength=n1) / c1
            if np.abs(m1b).max() < tol * (1 + np.abs(x).max()): break
        out[:, j] = x
    return out

class Design:
    """Gói mẫu s (đã winsorize) + cột cố định. beta(hvec) trả về hệ số của [x_fs, hv, x_size, x_liq, x_lat]."""
    def __init__(self, s, y, cond, yearint=0):
        self.s = s.reset_index(drop=True); self.y = y
        self.g1, self.g2 = codes(self.s.idrssd), codes(self.s.div_year)
        fixed = RAIN + BANK_CTRL + (COND if cond else [])
        F = self.s[fixed].to_numpy(float)
        extra = []
        if yearint >= 1:
            Y = pd.get_dummies(self.s.year).to_numpy(float)[:, 1:]       # bỏ 1 năm
            extra.append(Y * self.s["FS10"].to_numpy(float)[:, None])
        if yearint >= 2:
            for z in Z_INT: extra.append(Y * self.s[z].to_numpy(float)[:, None])
        F = np.column_stack([F] + extra) if extra else F
        Zf = absorb(np.column_stack([self.s[y].to_numpy(float), F]), [self.g1, self.g2])
        self.yt, self.Ft = Zf[:, 0], Zf[:, 1:]
        self.names = ["x_fs", "hv", "x_size", "x_liq", "x_lat"]
    def beta(self, hvec):
        s = self.s; h = np.asarray(hvec, float)
        X = np.column_stack([h * s.FS10.to_numpy(float), h] + [h * s[z].to_numpy(float) for z in Z_INT])
        Xt = absorb(X, [self.g1, self.g2])
        A = np.column_stack([Xt, self.Ft])
        return np.linalg.lstsq(A, self.yt, rcond=None)[0][:5]

if __name__ == "__main__":
    b = pd.read_parquet(f"{V2}/out/panel_v2.parquet")
    s = frame(b, "dALLOW_h0", True, need_lead=True)
    t0 = time.time(); D = Design(s, "dALLOW_h0", True); print("prep", round(time.time() - t0, 1))
    t0 = time.time(); bb = D.beta(s.heat_lead1.to_numpy()); print("beta", round(time.time() - t0, 2), bb.round(5))
    r, _ = fit(s, "dALLOW_h0", "heat_lead1", True, se="state"); print("fit_lp x_fs, hv:", r["beta"][:2].round(5))
