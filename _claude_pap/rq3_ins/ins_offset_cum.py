"""ins_offset_cum.py — LÀM SAU (19/11/2026). Phản ứng tích luỹ hai năm (t và t+1) của doanh thu trồng trọt, bồi thường bảo hiểm
và trợ cấp chính phủ, cùng đơn vị (chia doanh thu trồng trọt gốc 2001–05) và cùng một mẫu; tỷ lệ bù
θ_X = (β_X,t + β_X,t+1) / −(β_R,t + β_R,t+1). Lý do lấy hai năm: BEA ghi doanh thu theo năm dương lịch, vụ thu hoạch cuối năm t
bán một phần ở năm t+1; RMA ghi bồi thường theo năm vụ. Dùng lại joint()/ratio() của ins_offset.py (cùng đặc tả RQ-0, Conley 1.000 km, trễ 2).
Kèm tự tương quan của nhiệt sau FE để đọc hệ số năm t+1. Đầu ra: results_real/ins_offset_cum.csv"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ins_offset import joint, ratio, b, Z95  # noqa  (import chạy lại phần cùng năm của ins_offset.py)
from _pap_common import absorb, codes        # noqa
nxt = b.groupby("fips")["year"].shift(-1) == b["year"] + 1
b["G"] = b["govpay"] * 1000.0 / b["w_base"]                      # trợ cấp chính phủ (BEA dòng 130) / doanh thu trồng trọt gốc
for c in ("I_hd", "I_all", "G"):
    b[c + "_lead1"] = b.groupby("fips")[c].shift(-1).where(nxt)
b["heat_lead1_c"] = b.groupby("fips")["heat"].shift(-1).where(nxt)
Y = ["R", "R_lead1", "I_hd", "I_hd_lead1", "I_all", "I_all_lead1", "G", "G_lead1"]
s = b.dropna(subset=Y + ["heat", "ppt_season_z", "lat"]).copy()
rows = []
for wname, w in (("khong_trong_so", None), ("trong_so_doanh_thu_goc", "w_base")):
    beta, V, n, nc, d = joint(s, Y, w=w)
    def cum(i):
        return beta[i] + beta[i + 1], V[i, i] + V[i + 1, i + 1] + 2 * V[i, i + 1]
    bR, vR = cum(0)
    for nm, i in (("R", 0), ("I_hd", 2), ("I_all", 4), ("G", 6)):
        bc, vc = cum(i)
        r = dict(weight=wname, outcome=nm, b_t=beta[i], se_t=np.sqrt(V[i, i]), b_t1=beta[i + 1], se_t1=np.sqrt(V[i + 1, i + 1]),
                 b_cum=bc, se_cum=np.sqrt(vc), cum_lo=bc - Z95 * np.sqrt(vc), cum_hi=bc + Z95 * np.sqrt(vc), n=n, n_counties=nc,
                 mean_t=float(np.average(d[nm], weights=None if w is None else d[w])))
        if nm != "R":
            cov = V[i, 0] + V[i, 1] + V[i + 1, 0] + V[i + 1, 1]
            th, se = ratio(bc, bR, vc, vR, cov)
            r.update(theta=th, theta_se=se, theta_lo=th - Z95 * se, theta_hi=th + Z95 * se)
        rows.append(r)
out = pd.DataFrame(rows)
out.to_csv(HERE / "results_real" / "ins_offset_cum.csv", index=False)
pd.set_option("display.width", 250)
print(out.round(4).to_string(index=False))
a = b.dropna(subset=["heat", "heat_lead1_c"]).copy()
Z = absorb(a[["heat", "heat_lead1_c"]].to_numpy(float), [codes(a["fips"]), codes(a["div_year"])])
print("corr(nhiệt t, nhiệt t+1) sau FE hạt và division×năm:", round(float(np.corrcoef(Z[:, 0], Z[:, 1])[0, 1]), 4), "; n =", len(a))
