"""T3 — kích cỡ kiểm định dưới H0 bằng HOÁN VỊ NĂM của chuỗi nhiệt: heat_perm(b,t) = heat(b, π(t)), π là hoán vị không điểm cố định của các năm 2006–2024,
dùng CHUNG cho mọi ngân hàng (giữ tương quan không gian chéo-ngân hàng của nhiệt và tương quan nhiệt–FS; phá liên kết nhiệt–kết cục theo năm).
Kết cục, FE div×năm, mưa, controls giữ nguyên thực. Không dùng hệ số nhiệt thật. Dùng: python3 T3_size_yearperm.py <outcome> <cond 0/1> <R> <seed>"""
import sys
from _v2_spec import *
y, cond, R, seed = sys.argv[1], bool(int(sys.argv[2])), int(sys.argv[3]), int(sys.argv[4])
b = pd.read_parquet(f"{V2}/out/panel_v2.parquet")
piv = b.pivot(index="idrssd", columns="year", values="heat")
years = np.array(sorted(b.year.unique())); PV = piv.to_numpy()
s0 = frame(b, y, cond)
ib = piv.index.get_indexer(s0.idrssd)
rng = np.random.default_rng(seed); rows = []
for rep in range(R):
    while True:
        pi = rng.permutation(years)
        if (pi != years).all(): break
    mp = dict(zip(years, pi)); iy = piv.columns.get_indexer(s0.year.map(mp).to_numpy())
    s = s0.assign(heatp=PV[ib, iy]).dropna(subset=["heatp"])
    rc, _ = fit(s, y, "heatp", cond, se="conley"); rs, _ = fit(s, y, "heatp", cond, se="state")
    rows.append(dict(rep=rep, n=rc["n"], b2=rc["beta"][0], zc=rc["beta"][0] / rc["se"][0], zs=rs["beta"][0] / rs["se"][0], b1=rc["beta"][1],
                     z1c=rc["beta"][1] / rc["se"][1], z1s=rs["beta"][1] / rs["se"][1]))
    if rep % 2 == 1:
        D = pd.DataFrame(rows); print(rep + 1, "size β2 conley", (D.zc.abs() > 1.96).mean().round(3), "state", (D.zs.abs() > 1.96).mean().round(3),
                                   "| sd z", D.zc.std().round(2), D.zs.std().round(2), flush=True)
        D.to_csv(f"{V2}/out/T3_{y}_{int(cond)}_{seed}.csv", index=False)
