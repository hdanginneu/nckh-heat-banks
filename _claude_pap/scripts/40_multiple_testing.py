"""40_multiple_testing.py — Romano–Wolf step-down trong từng họ A, B, D, E (kế hoạch mục 8): 2.000 lần bootstrap theo cụm bang, seed cố định 20261015+500.
Thống kê: t cụm-bang (SE cụm theo bang, hồi quy hạt/ngân hàng cùng đặc tả chính nhưng ước lượng bằng FastFE: FE đơn vị + dummy division×năm, chính xác như hồi quy chính).
Lưu ý: p-value Conley (kết quả chính) và p-value RW (cụm bang) dùng hai ước lượng phương sai khác nhau; báo cả hai. Họ A và B có một giả thuyết (RW = p thô).
Họ D = {D1_h0, D1_h1}; họ E = {E1, E2}. H3 (họ C) KHÔNG dùng RW (intersection-union). Ngưỡng báo cáo: p_RW < 0,05 (hai phía).
Kết quả: results/romano_wolf.csv.
"""
from scipy import stats
from _pap_est import *

B = 2000
FAMS = {"A": [("A", "county", "y_lncrop", 0)], "B": [("B", "county", "y_govpay", 0)],
        "D": [("D1_h0", "bank", "D1_h0", 0), ("D1_h1", "bank", "D1_h1", 1)],
        "E": [("E1", "county", "y_indem_hd", 0), ("E2", "county", "y_indem_heat", 0)]}
cdf, bdf = load_county(), load_bank()
states = sorted(set(cdf.state.dropna()) | set(bdf.hq_state.dropna()))
smap = {s: i for i, s in enumerate(states)}
draws = state_draws(states, B, SEED + 500)
rows = []
for fam, tests in FAMS.items():
    objs = []
    for name, level, y, h in tests:
        if level == "county":
            s = county_frame(cdf, y)
            f = FastFE(s, y, ["heat"] + RAIN, "fips", "div_year", "state")
        else:
            s = bank_frame(bdf, y, h)
            f = FastFE(s, y, ["heat"] + RAIN + BANK_CTRL, "idrssd", "div_year", "hq_state")
        sidx = np.array([smap[x] for x in f.c_labels])[f.c]      # mã bang toàn cục của từng hàng
        beta, se = f.fit(se=True)
        objs.append((name, f, sidx, float(beta[0]), float(se[0]), len(f.c_labels)))
    J = len(objs)
    t_obs = np.array([abs(o[3] / o[4]) for o in objs])
    tstar = np.empty((B, J))
    for i in range(B):
        for j, (name, f, sidx, b0, s0, G) in enumerate(objs):
            w = draws[i][sidx].astype(float)
            bb, ss = f.fit(w, se=True)
            tstar[i, j] = abs((bb[0] - b0) / ss[0]) if ss[0] > 0 else np.nan
    order = np.argsort(-t_obs)
    p_rw = np.empty(J)
    prev = 0.0
    for rank, j in enumerate(order):
        rem = order[rank:]
        m = np.nanmax(tstar[:, rem], axis=1)
        p = (1 + np.sum(m >= t_obs[j])) / (B + 1)
        prev = max(prev, p); p_rw[j] = prev
    for j, (name, f, sidx, b0, s0, G) in enumerate(objs):
        p_raw = 2 * (1 - stats.t.cdf(t_obs[j], G - 1))
        row = dict(timestamp=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), family=f"RW_{fam}", outcome=name, h=tests[j][3], spec="romano_wolf_state_boot", sample="full",
                   beta=b0, se=s0, p=p_raw, n=f.n, n_clusters=G, p_rw=float(p_rw[j]), t_state_cluster=float(b0 / s0), n_tests_in_family=J, B=B)
        append_spec(row); rows.append(row)
pd.DataFrame(rows).to_csv(RES / "romano_wolf.csv", index=False)
print("[FAKE] xong Romano–Wolf" if FAKE else pd.DataFrame(rows)[["family", "outcome", "beta", "se", "p", "p_rw"]].round(4).to_string(index=False))
log_run(f"40_multiple_testing ({'FAKE' if FAKE else 'THẬT'}): Romano–Wolf B={B} cho {len(rows)} giả thuyết.")
