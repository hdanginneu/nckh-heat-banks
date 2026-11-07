"""30_robustness.py — robustness và falsification ĐỊNH TRƯỚC (kế hoạch mục 9). Danh sách đặc tả cố định bên dưới; không thêm bớt sau khi thấy kết quả.
Mục tiêu: hạt A (y_lncrop), B (y_govpay), E1 (y_indem_hd); ngân hàng C1–C4 (h = 1, 2) và D1 (h = 0, 1). Mọi đặc tả khác với 'main' chỉ ở MỘT điểm.
Ghi: results/robustness.csv, mỗi dòng một (đặc tả × kết cục). Với họ C, ghi thêm có đạt tương đương theo SESOI_y của đặc tả chính hay không.
Tmin (độ-ngày chuẩn Schlenker–Roberts) chạy ở script 31 sau mốc đóng băng.
"""
import json
from _pap_est import *

b = load_bank()
cdf = load_county()
sesoi = pd.read_csv(RES / "familyC.csv").query("`sample` == 'full'").set_index("outcome")["sesoi_y"].to_dict()
DIVS = sorted(b.division.dropna().unique())
rows = []


def add(spec, target, h, sample_lbl, r, j=0, extra=None):
    e = dict(spec=spec)
    if target.startswith("C"):
        ok, _, _ = tost(r["beta"][j], r["se"][j], sesoi[f"{target}_h{h}"])
        e.update(sesoi_pass=ok, sesoi_y=sesoi[f"{target}_h{h}"])
    if extra:
        e.update(extra)
    rows.append(record("ROB", target, h, spec, sample_lbl, r, j=j, extra=e))


def winsor(s, y):
    lo, hi = s[y].quantile([0.01, 0.99])
    s = s.copy(); s[y] = s[y].clip(lo, hi); return s


# ---------------- hạt ----------------
CT = [("A", "y_lncrop"), ("B", "y_govpay"), ("E1", "y_indem_hd")]
for fam, y in CT:
    base = county_frame(cdf, y)
    def run_c(spec, s=None, x=("heat",) + tuple(RAIN), fe=("fips", "div_year"), se="conley", w=None, j=0, cluster=None):
        s = base if s is None else s
        r = fit_lp(s, y, list(x), list(fe), se=se, cty="fips", w=w, cluster=cluster)
        add(spec, fam, 0, "full", r, j=j)
    run_c("fe_county_year", fe=("fips", "year"))
    run_c("fe_county_stateyear", fe=("fips", "state_year"))
    for hc, nm in (("heat_p90", "heat_p90"), ("heat_gt32", "heat_gt32"), ("heat_hex90", "heat_hex90")):
        s2 = base.dropna(subset=[hc]); run_c(nm, s=s2, x=(hc,) + tuple(RAIN))
    run_c("rain_none", x=("heat",))
    s2 = base.copy(); s2["dry"] = (s2.ppt_season_z <= -1).astype(float); s2["heat_x_dry"] = s2.heat * s2.dry
    r = fit_lp(s2, y, ["heat", "heat_x_dry", "dry"] + RAIN, ["fips", "div_year"], se="conley", cty="fips")
    add("rain_dry_interaction:heat_not_dry", fam, 0, "full", r, j=0); add("rain_dry_interaction:heat_x_dry", fam, 0, "full", r, j=1)
    for dv in DIVS:
        run_c(f"drop_division:{dv}", s=base[base.division != dv])
    for yr in (2011, 2012):
        run_c(f"drop_year:{yr}", s=base[base.year != yr])
    run_c("drop_years:2022_2023", s=base[~base.year.isin([2022, 2023])])
    run_c("drop_years:2007_2012", s=base[~base.year.between(2007, 2012)])
    run_c("winsor_1_99", s=winsor(base, y))
    run_c("cluster_state", se="cluster", cluster="state")
    run_c("cluster_division_year", se="cluster", cluster="div_year")
    run_c("weighted_baseline_crop", s=base[base.base_crop_kusd > 0], w="base_crop_kusd")
    s2 = base.dropna(subset=["heat_lead1"]); run_c("placebo_lead1", s=s2, x=("heat_lead1",) + tuple(RAIN))

# ---------------- ngân hàng ----------------
BT = [(f"C{k}", h) for k in (1, 2, 3, 4) for h in (1, 2)] + [("D1", 0), ("D1", 1)]
for o, h in BT:
    y = f"{o}_h{h}"
    base = bank_frame(b, y, h)
    fam = o
    X = ["heat"] + RAIN + BANK_CTRL
    CK = dict(cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")

    def run_b(spec, s=None, x=tuple(X), fe=("idrssd", "div_year"), se="conley", w=None, j=0, cluster=None, ycol=None):
        s = base if s is None else s
        r = fit_lp(s, ycol or y, list(x), list(fe), se=se, w=w, cluster=cluster, **CK)
        add(spec, fam, h, "full", r, j=j)
    run_b("fe_bank_year", fe=("idrssd", "year"))
    run_b("fe_bank_stateyear", fe=("idrssd", "state_year"))
    for hc in ("heat_p90", "heat_gt32", "heat_hex90"):
        s2 = base.dropna(subset=[hc]); run_b(hc, s=s2, x=(hc,) + tuple(RAIN) + tuple(BANK_CTRL))
    run_b("rain_none", x=tuple(["heat"] + BANK_CTRL))
    s2 = base.copy(); s2["dry"] = (s2.ppt_season_z <= -1).astype(float); s2["heat_x_dry"] = s2.heat * s2.dry
    r = fit_lp(s2, y, ["heat", "heat_x_dry", "dry"] + RAIN + BANK_CTRL, ["idrssd", "div_year"], se="conley", **CK)
    add("rain_dry_interaction:heat_not_dry", fam, h, "full", r, j=0); add("rain_dry_interaction:heat_x_dry", fam, h, "full", r, j=1)
    # mẫu
    run_b("drop_thrift", s=base[~base.ots_docket_ever.fillna(False).astype(bool)])
    run_b("only_2012_2025", s=base[base.year >= 2012])
    run_b("drop_years:2007_2012", s=base[~base.year.between(2007, 2012)])
    for dv in DIVS:
        run_b(f"drop_division:{dv}", s=base[base.division != dv])
    for yr in (2011, 2012):
        run_b(f"drop_year:{yr}", s=base[base.year != yr])
    run_b("drop_years:2022_2023", s=base[~base.year.isin([2022, 2023])])
    for gname in ("ag15", "ag35"):
        sg = bank_frame(b, y, h, group=gname)
        run_b(f"farmshare_{gname[2:]}pct", s=sg)
    # thống kê
    run_b("no_controls", x=tuple(["heat"] + RAIN))
    run_b("winsor_1_99", s=winsor(base, y))
    run_b("cluster_bank", se="cluster", cluster="idrssd")
    run_b("cluster_state", se="cluster", cluster="hq_state")
    run_b("cluster_division_year", se="cluster", cluster="div_year")
    run_b("weighted_portfolio_loans", w=("farmland_l1" if o in ("C1", "C2", "D2") else "agprod_l1"))
    # falsification
    sl = bank_frame(b, y, h, group="low5")
    run_b("falsification_low_farmshare", s=sl)
    lead = f"heat_lead{h + 1}"
    s2 = base.dropna(subset=[lead]); run_b(f"placebo_lead_t+{h + 1}", s=s2, x=(lead,) + tuple(RAIN) + tuple(BANK_CTRL))

R = pd.DataFrame(rows)
R.to_csv(RES / "robustness.csv", index=False)
print("[FAKE] xong robustness" if FAKE else f"{len(R)} đặc tả")
log_run(f"30_robustness ({'FAKE' if FAKE else 'THẬT'}): {len(R)} dòng đặc tả.")
