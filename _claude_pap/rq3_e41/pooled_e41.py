"""pooled_e41.py — gộp ước lượng của mẫu chính (năm sốc 2007–2024) và mẫu ngoài (1995–2006) cho C1–C5 theo trọng số nghịch đảo phương sai.
Hai mẫu không chung năm sốc và dùng hai dãy hoán vị khác nhau, nên coi hai ước lượng là độc lập. Phương sai = sd_adj² (độ lệch chuẩn hoán vị đã
nhân κ). Báo thêm z của hiệu hai mẫu (dị biệt). TOST với Δ của bài. Không ước lượng hồi quy mới.
Đầu ra: results_real/pooled_e41.csv"""
import os, json, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
M = pd.read_csv(f"{H}/../rq3_v3/results_real/v3_confirmatory.csv").set_index("name")
E = pd.read_csv(f"{H}/results_real/e41_results.csv"); E = E[E.rule == "E41-2"].set_index("stat")
D = {C: json.load(open(f"{H}/../rq3_v3/sesoi_v3.json"))[C]["primary"] for C in M.index}
rows = []
for C in M.index:
    tm, sm, te, se = M.loc[C, "theta"], M.loc[C, "sd_adj"], E.loc[C, "theta"], E.loc[C, "sd_adj"]
    w = np.array([1 / sm**2, 1 / se**2]); t = (w @ [tm, te]) / w.sum(); s = 1 / np.sqrt(w.sum())
    lo, hi = t - 1.6449 * s, t + 1.6449 * s; z = (te - tm) / np.sqrt(sm**2 + se**2)
    rows.append(dict(stat=C, theta_main=tm, theta_ext=te, z_hieu=z, theta_gop=t, sd_gop=s, ci90_lo=lo, ci90_hi=hi,
                     ci95_lo=t - 1.96 * s, ci95_hi=t + 1.96 * s, delta=D[C], tuong_duong=bool(lo > -D[C] and hi < D[C]),
                     can_tren_FS25=2.5 * hi, nam_soc_ngoai=E.loc[C, "years"]))
O = pd.DataFrame(rows); O.to_csv(f"{H}/results_real/pooled_e41.csv", index=False)
pd.set_option("display.width", 250); print(O.round(4).to_string(index=False))
