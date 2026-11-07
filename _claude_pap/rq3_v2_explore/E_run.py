"""E_run.py — THĂM DÒ SAU ĐÓNG BĂNG PAP v2 (không thuộc phần xác nhận). Dùng cùng đặc tả V2 (_v2_spec, đã đóng băng) cho:
 mech:<key>   phân rã bảng cân đối của ΔLIQ (Δ tài sản thanh khoản, Δ tổng tài sản, Δ cho vay, Δ tiền gửi ... / tổng tài sản t−1)
 jack:<year>  dLIQ bỏ một năm
 plac:<var>   dLIQ với nhiệt thay bằng heat_lead2 / heat_lead3 (placebo một vế) hoặc thêm heat_lag1 (độ trễ phân phối)
 stfe:<key>   FE ngân hàng + bang×năm thay division×năm
 dropwsc11    dLIQ bỏ West South Central năm 2011
Ghi jobs/<task>.json. Lệnh: python3 E_run.py <task> [<task> ...]"""
import sys, os, json, time
sys.path.insert(0, os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v2"))
from _v2_spec import *
EX = os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/rq3_v2_explore")
CH = os.path.expanduser("~/rq3cache/real")

KEEP = ["idrssd", "year", "division", "hq_state", "hq_county_fips_l1", "hq_lat", "hq_lon", "heat", "heat_lead1", "heat_lead2", "heat_lead3", "heat_lag1",
        "ppt_season_z", "ppt_z2", "log_total_assets_l1", "liquidity_ratio_l1", "loans_to_assets_l1", "NCO_h0", "S_npl_total_h0", "ALLOWlag", "cecl_adopt_year",
        "FS10", "z_size", "z_liq", "z_lat", "state_year", "dLIQ_h0", "dALLOW_h0", "S_prov_cum_h0",
        "dLA", "dTA", "dLOAN", "dDEP", "dAGP", "dFARML", "dNONAG", "dEQ", "dCASH", "dSEC"]
def panel():
    f = f"{CH}/panel_explore.parquet"
    if os.path.exists(f): return pd.read_parquet(f, columns=KEEP)
    b = pd.read_parquet(f"{CH}/panel_run.parquet")
    p = pd.read_parquet(P1, columns=["idrssd", "year", "total_loans_kusd", "total_deposits_kusd", "farmland_loans_kusd", "ag_production_loans_kusd",
                                     "total_equity_kusd", "fed_funds_sold_kusd"]).drop_duplicates(["idrssd", "year"])
    b = b.merge(p, on=["idrssd", "year"], how="left", suffixes=("", "_x")).sort_values(["idrssd", "year"]).reset_index(drop=True)
    TA = b["total_assets_kusd_p"]
    def lag(col):
        v = b.groupby("idrssd")[col].shift(1); yr = b.groupby("idrssd")["year"].shift(1)
        return pd.Series(np.where(yr == b.year - 1, v, np.nan), index=b.index)
    TA1 = lag("total_assets_kusd_p")
    b["LA"] = b.liquidity_ratio * TA
    comps = {"dLA": "LA", "dTA": "total_assets_kusd_p", "dLOAN": "total_loans_kusd", "dDEP": "total_deposits_kusd", "dAGP": "ag_production_loans_kusd",
             "dFARML": "farmland_loans_kusd", "dEQ": "total_equity_kusd", "dCASH": "cash_and_due_kusd", "dSEC": None}
    b["SEC"] = b.htm_securities_kusd.fillna(0) + b.afs_securities_kusd.fillna(0)
    comps["dSEC"] = "SEC"
    for k, c in comps.items():
        b[k] = 100 * (b[c] - lag(c)) / TA1
    b["dNONAG"] = b.dLOAN - b.dAGP.fillna(0) - b.dFARML.fillna(0)
    b["heat_lag1"] = lag("heat")
    b["state_year"] = b.hq_state + "_" + b.year.astype(str)
    b.to_parquet(f, index=False)
    return b

OUTS["NCO"] = ("NCO_h0", False, ["cecl_adopt_year"]); OUTS["NPL"] = ("S_npl_total_h0", False, [])
for k in ["dLA", "dTA", "dLOAN", "dDEP", "dAGP", "dFARML", "dNONAG", "dEQ", "dCASH", "dSEC"]:
    OUTS[k] = (k, False, [])

def rows_of(r, xs, tag, key, se, keep):
    out = []
    for i, nm in enumerate(xs):
        if nm in keep:
            out.append(dict(task=tag, key=key, se_type=se, coef=nm, beta=float(r["beta"][i]), se=float(r["se"][i]), p=float(r["p"][i]), n=int(r["n"]),
                            banks=int(r["n_units"]), sd_y=float(r["sd_y"])))
    return out

def fit2(s, key, hv, fe=("idrssd", "div_year"), extra=()):
    y = OUTS[key][0]
    s = make_terms(s, hv, LIN); s, yn = year_ints(s, 2)
    xs = ["x_" + m for m in LIN] + [hv] + ctrl_cols(key) + yn + list(extra)
    rc = fit_lp(s, y, xs, list(fe), se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
    rs = fit_lp(s, y, xs, list(fe), se="cluster", cluster="hq_state")
    return rc, rs, xs

def run(task):
    b = panel(); kind, _, arg = task.partition(":"); res = []
    keep = {"x_FS10", "heat"}
    if kind == "mech":
        s = frame(b, arg); rc, rs, xs = fit2(s, arg, "heat")
    elif kind == "jack":
        s = frame(b, "dLIQ"); s = s[s.year != int(arg)]; rc, rs, xs = fit2(s, "dLIQ", "heat")
    elif kind == "dropwsc11":
        s = frame(b, "dLIQ"); s = s[~((s.division == "West South Central") & (s.year == 2011))]; rc, rs, xs = fit2(s, "dLIQ", "heat")
    elif kind == "plac":
        if arg in ("heat_lead2", "heat_lead3"):
            s = frame(b, "dLIQ", need_lead=arg); rc, rs, xs = fit2(s, "dLIQ", arg); keep = {"x_FS10", arg}
        elif arg == "lag1":
            s = frame(b, "dLIQ", need_lead="heat_lag1").copy()
            ex = []
            for m in LIN: s["G_x_" + m] = s["heat_lag1"] * s[m]; ex.append("G_x_" + m)
            ex.append("heat_lag1"); rc, rs, xs = fit2(s, "dLIQ", "heat", extra=ex); keep = {"x_FS10", "heat", "G_x_FS10", "heat_lag1"}
        elif arg == "lead1lag1":
            s = frame(b, "dLIQ", need_lead="heat_lag1").dropna(subset=["heat_lead1"]).copy()
            ex = []
            for pre, hv in (("G_", "heat_lag1"), ("L_", "heat_lead1")):
                for m in LIN: s[pre + "x_" + m] = s[hv] * s[m]; ex.append(pre + "x_" + m)
                ex.append(hv)
            rc, rs, xs = fit2(s, "dLIQ", "heat", extra=ex); keep = {"x_FS10", "G_x_FS10", "L_x_FS10"}
    elif kind == "stfe":
        s = frame(b, arg); rc, rs, xs = fit2(s, arg, "heat", fe=("idrssd", "state_year"))
    res = rows_of(rc, xs, task, arg or kind, "conley", keep) + rows_of(rs, xs, task, arg or kind, "state", keep)
    return res

if __name__ == "__main__":
    for t in sys.argv[1:]:
        fn = f"{EX}/jobs/{t.replace(':', '_').replace(' ', '_')}.json"
        if os.path.exists(fn): continue
        t0 = time.time(); r = run(t); json.dump(dict(task=t, rows=r, secs=time.time() - t0), open(fn, "w")); print(t, round(time.time() - t0), "s", flush=True)
