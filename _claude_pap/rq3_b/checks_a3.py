"""A3: tự tương quan bậc 1 của nhiệt cấp ngân hàng sau khi khử FE ngân hàng + division×năm (mô tả, không phải phân tích mới).
Hai cách: (a) cặp (b,t),(b,t−1) có cả hai năm, phần dư của mỗi năm khử FE trên toàn panel; (b) như (a) nhưng chỉ năm sốc 2007–2024."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rq3_v3"))
from _v3_spec import np, pd, load_panel, codes
B = load_panel()[["idrssd", "year", "division", "heat", "div_year"]].dropna()
B = B[B.year.between(2006, 2024)].reset_index(drop=True)
def resid(d):
    y = d.heat.to_numpy(float).copy(); g1 = codes(d.idrssd); g2 = codes(d.div_year)
    for _ in range(200):                                    # khử hai chiều FE bằng lặp xen kẽ
        y0 = y.copy()
        y -= (np.bincount(g1, y) / np.bincount(g1))[g1]; y -= (np.bincount(g2, y) / np.bincount(g2))[g2]
        if np.max(np.abs(y - y0)) < 1e-10: break
    return y
out = {}
for lab, lo in (("2006_2024", 2006), ("2007_2024", 2007)):
    d = B[B.year >= lo].reset_index(drop=True); d["r"] = resid(d)
    m = d.merge(d[["idrssd", "year", "r", "heat"]].assign(year=d.year + 1), on=["idrssd", "year"], suffixes=("", "_l1"))
    out[lab] = dict(n_pairs=len(m), corr_resid=float(np.corrcoef(m.r, m.r_l1)[0, 1]), corr_raw=float(np.corrcoef(m.heat, m.heat_l1)[0, 1]),
                    sd_resid=float(d.r.std()))
print(json.dumps(out, indent=1)); json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_real", "a3_autocorr.json"), "w"), indent=1)
