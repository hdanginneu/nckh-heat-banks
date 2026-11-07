"""T6 — MDE/độ lệch chuẩn của β2 dưới hoán vị năm thời tiết, theo outcome × biến thể. python3 T6_ri_mde.py <key> <level> <R> <seed>. Không dùng hệ số nhiệt thật."""
import sys
from _v2_ri import *
key, level, R, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
b = pd.read_parquet(f"{V2}/out/panel_v2.parquet")
W, G, yrs, sd = build_W(b)
s = frame(b, key); D = Design(s, key, level); yr_rows = D.s.year.to_numpy()
rng = np.random.default_rng(seed); out = []; t0 = time.time()
for rep in range(R):
    pi = draw_pi(rng, range(2006, 2025))
    out.append(D.beta(perm_heat(W, G, yrs, sd, D.rows, yr_rows, pi)))
    if time.time() - t0 > 140: break
O = np.array(out); np.save(f"{V2}/out/T6_{key.replace('|','_')}_L{level}_{seed}.npy", O)
print(f"{key} L{level} n={len(D.s)} reps={len(O)} sd(b2)={O[:,0].std():.5f} MDE80={2.8016*O[:,0].std():.5f} sd_y={D.s[OUTS[key][0]].std():.4f} MDE_sd={2.8016*O[:,0].std()/D.s[OUTS[key][0]].std():.4f} time/rep={(time.time()-t0)/len(O):.1f}s")
