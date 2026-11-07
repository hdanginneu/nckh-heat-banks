"""70_post_freeze_E_by_crop.py — PHỤ LỤC SAU ĐÓNG BĂNG (thăm dò, không thuộc kế hoạch v1; xem POST_FREEZE_ADDENDUM.md).
Tách họ E1 theo nhóm cây trồng: bồi thường RMA do Drought/Heat/Hot Wind (mã 11, 12, 62) theo cây / doanh thu cây trồng baseline của hạt,
cùng đặc tả họ E (FE hạt + division×năm, mưa z, z², nhiệt gdd_ex29/SD, SE Conley). Nhóm cây: 4 cây có tổng bồi thường nhiệt-hạn lớn nhất 2001–2022 và 'còn lại'.
Ghi results_post_freeze/E_by_crop.csv; không ghi vào specs_run.csv của kế hoạch.
"""
import zipfile
import pandas as pd
import numpy as np
from _pap_est import *

assert not FAKE
COL = ["year", "st", "stab", "cty", "ctyname", "cmd", "cmdname", "plan", "planab", "cov", "stage", "cause", "causedesc", "mon", "monname",
       "lossyr", "pol_prem", "pol_ind", "netq", "endacres", "liab", "prem", "prod_prem", "subsidy", "stsub", "addsub", "efa", "detq", "indem", "lr"]
rows = []
for y in range(2001, 2023):
    z = zipfile.ZipFile(RMA / f"colsom_{y}.zip")
    c = pd.read_csv(z.open(z.namelist()[0]), sep="|", header=None, names=COL, dtype=str, encoding="latin1", usecols=["year", "st", "cty", "cmdname", "cause", "indem"])
    c["indem"] = pd.to_numeric(c["indem"]); c["cause"] = c["cause"].str.strip(); c["cmdname"] = c["cmdname"].str.strip().str.upper()
    c = c[(c.cty.str.strip() != "999") & c.cause.isin(["11", "12", "62"])]
    c["fips"] = c.st.str.zfill(2) + c.cty.str.zfill(3)
    rows.append(c.groupby(["fips", "cmdname"], as_index=False)["indem"].sum().assign(year=y))
R = pd.concat(rows)
top = R.groupby("cmdname").indem.sum().sort_values(ascending=False)
groups = list(top.index[:4])
R["grp"] = np.where(R.cmdname.isin(groups), R.cmdname, "OTHER")
G = R.groupby(["fips", "year", "grp"], as_index=False).indem.sum().pivot_table(index=["fips", "year"], columns="grp", values="indem", fill_value=0.0).reset_index()
cdf = load_county()
d = cdf.merge(G, on=["fips", "year"], how="left")
has = d.has_col.fillna(False).astype(bool)
bc = d.base_crop_kusd.where(d.base_crop_kusd > 0) * 1000.0
out = []
for g in groups + ["OTHER"]:
    d[f"y_{g}"] = (d[g].fillna(0.0) / bc).where(has)    # hạt-năm có bản ghi RMA mà không có bồi thường cây này = 0 hợp lệ
    s = county_frame(d, f"y_{g}")
    r = fit_lp(s, f"y_{g}", ["heat"] + RAIN, ["fips", "div_year"], se="conley", cty="fips")
    out.append(dict(crop_group=g, total_indem_usd_2001_2022=float(top.get(g, R[R.grp == "OTHER"].indem.sum())), beta=float(r["beta"][0]), se=float(r["se"][0]),
                    ci95_lo=float(r["ci95"][0][0]), ci95_hi=float(r["ci95"][1][0]), n=r["n"], sd_y=r["sd_y"]))
tot = sum(o["beta"] for o in out)
(PAP / "out" / "results_post_freeze").mkdir(exist_ok=True)
pd.DataFrame(out).to_csv(PAP / "out" / "results_post_freeze" / "E_by_crop.csv", index=False)
print(pd.DataFrame(out).round(4).to_string(index=False)); print("tổng β theo nhóm:", round(tot, 4))
log_run("70_post_freeze_E_by_crop (THĂM DÒ, sau đóng băng): họ E tách theo cây.")
