"""T4 — so sánh biến thể kiểm soát năm×FS (V0 không; V1 FS10×năm; V2 FS10×năm + Z×năm) theo phân phối β2 dưới hoán vị năm. Không dùng hệ số nhiệt thật.
python3 T4_variants_perm.py <outcome> <cond> <variant> <R> <seed>"""
import sys
from _v2_fast import *
y, cond, var, R, seed = sys.argv[1], bool(int(sys.argv[2])), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
b = pd.read_parquet(f"{V2}/out/panel_v2.parquet")
piv = b.pivot(index="idrssd", columns="year", values="heat"); PV = piv.to_numpy(); years = np.array(sorted(b.year.unique()))
s0 = frame(b, y, cond)
ib = piv.index.get_indexer(s0.idrssd)
D = Design(s0, y, cond, yearint=var)
rng = np.random.default_rng(seed); out = []
t0 = time.time()
for rep in range(R):
    while True:
        pi = rng.permutation(years)
        if (pi != years).all(): break
    mp = dict(zip(years, pi)); iy = piv.columns.get_indexer(D.s.year.map(mp).to_numpy())
    h = PV[ib, iy]
    if np.isnan(h).any():
        h = np.where(np.isnan(h), 0.0, h)    # hàng thiếu nguồn: thay bằng 0 (hiếm); chỉ để so sánh biến thể trên CÙNG mẫu
    bb = D.beta(h); out.append(bb)
    if time.time() - t0 > 150: break
O = np.array(out)
np.save(f"{V2}/out/T4_{y}_{int(cond)}_v{var}_{seed}.npy", O)
print(f"v{var} reps={len(O)} sd(b2)={O[:,0].std():.5f} sd(b1)={O[:,1].std():.5f} mean b2={O[:,0].mean():.5f}")
