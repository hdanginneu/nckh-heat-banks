"""_v2_spec.py — đặc tả RQ3 (PAP v2) dùng chung: định nghĩa outcome, mẫu, tương tác, hàm fit (Conley / cụm-bang)."""
import sys, os, time
from _v2_build import *   # _pap_est, ROOT, V2, build

Z_INT = ["z_size", "z_liq", "z_lat"]           # Z = {log tài sản, thanh khoản, vĩ độ}; z_loans bị loại vì corr −0,984 với z_liq (T0)
LIN = ["FS10"] + Z_INT                          # cột nhân với nhiệt trong đặc tả chính; mục tiêu = cột đầu (FS10)
COND = ["NCO_h0", "S_npl_total_h0", "ALLOWlag"]
# khoá outcome -> (cột y, có điều kiện hoá, control cố định thêm)
OUTS = {
    "dALLOW|cond": ("dALLOW_h0", True, ["cecl_adopt_year"]),
    "prov|cond":   ("S_prov_cum_h0", True, ["cecl_adopt_year"]),
    "dLIQ":        ("dLIQ_h0", False, []),
    "dALLOW|raw":  ("dALLOW_h0", False, ["cecl_adopt_year"]),
    "prov|raw":    ("S_prov_cum_h0", False, ["cecl_adopt_year"]),
    "D1":          ("D1_h0", False, []),
    "dALLOW_h1":   ("dALLOW_h1", False, ["cecl_adopt_year"]),
    "dLIQ_h1":     ("dLIQ_h1", False, []),
    "prov_h1":     ("S_prov_cum_h1", False, ["cecl_adopt_year"]),
}
PRIMARY = ["dALLOW|cond", "prov|cond", "dLIQ"]

def make_terms(s, hv, mults):
    s = s.copy()
    for m in mults:
        s["x_" + m] = s[hv] * s[m]
    return s

def winsor(s, cols, p=0.01):
    for c in cols:
        lo, hi = s[c].quantile([p, 1 - p]); s[c] = s[c].clip(lo, hi)
    return s

def frame(b, key, years=(2007, 2022), need_lead=None, p=0.01, extra_ctrl=(), need=(), group=None):
    """Mẫu ước lượng cho outcome `key`: đủ y, heat, mưa, BANK_CTRL, FS10, Z, (COND), extra; winsorize y và COND ở p/1−p TRONG mẫu."""
    y, cond, extra = OUTS[key]
    ex = list(extra) + list(extra_ctrl) + (COND if cond else []) + ["FS10"] + Z_INT + list(need)
    s = bank_frame(b, y, 0, group=group, years=years, extra_dropna=ex)
    if need_lead:
        s = s.dropna(subset=[need_lead])
    s = s.copy()
    if p: s = winsor(s, [y] + (COND if cond else []), p)
    return s

def ctrl_cols(key, extra_ctrl=()):
    y, cond, extra = OUTS[key]
    return RAIN + BANK_CTRL + (COND if cond else []) + list(extra) + list(extra_ctrl)

def year_ints(s, level, bases=None):
    """Cột năm×base (bỏ năm đầu làm gốc). level 0: không; 1: chỉ base đầu (FS10); 2: mọi base."""
    s = s.copy(); names = []
    bases = list(bases if bases is not None else LIN)
    use = [] if level == 0 else (bases[:1] if level == 1 else bases)
    yrs = sorted(s.year.unique())[1:]
    cols = {}
    for bse in use:
        for yv in yrs:
            nm = f"yi_{bse}_{yv}"; cols[nm] = (s.year == yv).to_numpy(float) * s[bse].to_numpy(float); names.append(nm)
    if cols: s = pd.concat([s, pd.DataFrame(cols, index=s.index)], axis=1)
    return s, names

def fit(s, key, hv, se="conley", level=2, mults=None, bases=None, extra=(), extra_ctrl=()):
    """OLS với FE bank + div×năm; thứ tự cột: [x_<mults>..., hv, controls, năm×gradient, extra]. Mục tiêu = cột đầu."""
    mults = LIN if mults is None else mults
    y, cond, ex = OUTS[key]
    s = make_terms(s, hv, mults)
    s, yn = year_ints(s, level, bases)
    xs = ["x_" + m for m in mults] + [hv] + ctrl_cols(key, extra_ctrl) + yn + list(extra)
    if se == "conley":
        return fit_lp(s, y, xs, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon"), xs
    return fit_lp(s, y, xs, ["idrssd", "div_year"], se="cluster", cluster="hq_state"), xs
