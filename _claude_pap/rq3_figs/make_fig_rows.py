"""Dựng lại số liệu của Hình 1 và Hình 2 (bài RQ3 v3, doc rev 233) từ các file kết quả thật.

Chạy từ thư mục _claude_pap:  python3 rq3_figs/make_fig_rows.py
In ra hai mảng JSON. So với mảng `data:[...]` trong fig1_lp_theo_horizon.jsx và
fig2_tuong_duong_theo_delta.jsx (hai module vẽ hình trong Claude Docs) để kiểm từng số.
"""
import json
import pandas as pd

# Hình 1: β₂ theo h (mỗi h trên mẫu riêng), khoảng tin cậy 90% từ hoán vị
lp = pd.read_csv('rq3_v3/results_real/v3_lp_long.csv')
lp = lp[lp.name.str.startswith('LP_')]
ten = {'C1': 'nco', 'C2': 'allow', 'C3': 'pdna', 'C4': 'liq', 'C5': 'agl'}
h_chinh = {'nco': {6}, 'allow': {0, 1, 3, 4, 5, 6}, 'pdna': {0, 1}, 'liq': {0}, 'agl': {2}}
hinh1 = []
for _, r in lp.iterrows():
    o = ten[r.C]
    h = int(r.h)
    hinh1.append(dict(o=o, h=h, b=round(r.beta2, 6), lo=round(r.ci90_lo, 6), hi=round(r.ci90_hi, 6),
                      p=round(r.p_RI, 3), m=h in h_chinh[o], n=int(r.n)))

# Hình 2: ước lượng và khoảng tin cậy 90% của các thống kê chính, mẫu gộp và mẫu ngoài
cf = pd.read_csv('rq3_v3/results_real/v3_confirmatory.csv').set_index('name')
p2 = pd.read_csv('rq3_p2/results_real/p2_results.csv').set_index('name')
pool = pd.read_csv('rq3_e41/results_real/pooled_e41.csv').set_index('stat')
ext = pd.read_csv('rq3_e41/results_real/e41_results.csv')
ext = ext[ext.rule == 'E41-2'].set_index('stat')
hinh2 = []
for s in ['C1', 'C2', 'C3', 'C5', 'C4']:
    r = cf.loc[s]
    row = dict(stat=s, d=round(r.sesoi_primary, 6), t=round(r.theta, 6), lo=round(r.ci90_lo, 6), hi=round(r.ci90_hi, 6))
    if s == 'C4':  # không gộp (|z| > 1,96): vẽ mẫu ngoài 1995–2006
        e = ext.loc[s]
        row.update(t2=round(e.theta, 6), lo2=round(e.ci90_lo, 6), hi2=round(e.ci90_hi, 6), k2='mẫu ngoài 1995–2006')
    else:
        g = pool.loc[s]
        row.update(t2=round(g.theta_gop, 6), lo2=round(g.ci90_lo, 6), hi2=round(g.ci90_hi, 6), k2='gộp hai mẫu')
    hinh2.append(row)
for s in ['P1', 'P2']:
    r = p2.loc[s]
    hinh2.append(dict(stat=s, d=round(r.sesoi, 6), t=round(r.theta, 6), lo=round(r.ci90_lo, 6), hi=round(r.ci90_hi, 6),
                      t2=None, lo2=None, hi2=None, k2=''))

print(json.dumps(hinh1, ensure_ascii=False))
print(json.dumps(hinh2, ensure_ascii=False))
