"""rep_pyfixest.py — TÁI LẬP ĐỘC LẬP (19/11/2026) năm thống kê xác nhận C1–C5 của RQ3 v3 bằng pyfixest.
Dùng chung với code gốc: panel_v3 và hàm chọn mẫu / winsorize (_v3_spec.load_panel, common_rows, make_frame), để hai bên ước lượng
trên đúng một tập quan sát. Độc lập với code gốc: biến tương tác nhiệt × {FS10, z} và năm × {FS10, z} do công thức pyfixest tự dựng
(cú pháp ":" và i(year, ·, ref = năm đầu)), FE ngân hàng và division × năm do pyfixest khử bằng bộ giải LSMR có tiền điều kiện
viết bằng Rust của pyfixest (code gốc dùng scipy lsmr / FWL tự viết).
So sánh: β2 từng chân h, θ = Σ w_h β2 (PAP v3 §3.3) với v3_lp_long.csv / v3_confirmatory.csv; SE cụm theo bang trụ sở (CRV1) với
se_state của fit_lp, với hiệu chỉnh mẫu nhỏ giống code gốc (G/(G−1)·(n−1)/(n−k), k không tính FE: ssc(k_fixef="none")) và với
hiệu chỉnh mặc định của pyfixest (k tính cả FE không lồng trong cụm) — mô tả; suy luận chính của bài là hoán vị, không tái lập ở đây. Đầu ra: results_real/rep_pyfixest.csv"""
import os, sys, time, gc
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "rq3_v3"))
import numpy as np, pandas as pd                 # noqa: E402
import pyfixest as pf                            # noqa: E402
import _v3_spec as V                             # noqa: E402
assert V.SPEC == "main"
t0 = time.time()
B = V.load_panel()
ref = pd.read_csv(os.path.join(HERE, "..", "rq3_v3", "results_real", "v3_lp_long.csv")).set_index("name")
conf = pd.read_csv(os.path.join(HERE, "..", "rq3_v3", "results_real", "v3_confirmatory.csv")).set_index("name")
ctrl = " + ".join(V.controls())
# khử FE: LSMR có tiền điều kiện của pyfixest (backend "within", Rust), dung sai 1e-10; giữ quan sát singleton để n khớp code gốc
DEM = pf.LsmrDemeaner(backend="within", fixef_atol=1e-10, fixef_btol=1e-10, fixef_maxiter=100000)
rows_out = []
for th in [t for t in V.thetas() if t["grp"] == "main"]:
    rows = V.common_rows(B, th)
    theta = 0.0
    for h, w in zip(th["hs"], th["w"]):
        y = f"{th['var']}_h{h}"
        s = V.make_frame(B, th["C"], y, h, rows=rows, opts=th["opts"]).copy()
        y0 = int(s.year.min())
        inter = " + ".join(f"heat:{m}" for m in V.LIN)
        yr = " + ".join(f"i(year, {m}, ref={y0})" for m in V.LIN)
        fml = f"{y} ~ {inter} + heat + {ctrl} + {yr} | idrssd + div_year"
        m = pf.feols(fml, data=s, vcov={"CRV1": "hq_state"}, fixef_rm="none", demeaner=DEM, ssc=pf.ssc(k_fixef="none"), lean=True)
        md = pf.feols(fml, data=s, vcov={"CRV1": "hq_state"}, fixef_rm="none", demeaner=DEM, lean=True)   # hiệu chỉnh mặc định của pyfixest
        co, se = m.coef(), m.se()
        b2 = float(co["heat:FS10"]); s2 = float(se["heat:FS10"]); s2d = float(md.se()["heat:FS10"])
        assert abs(float(md.coef()["heat:FS10"]) - b2) < 1e-12
        n_pf, k_pf = int(m._N), len(co)
        del m, md, s; gc.collect()
        r = ref.loc[f"TH_{th['name']}_{h}"]
        rows_out.append(dict(stat=th["name"], h=h, w=w, n_pf=n_pf, n_goc=int(r["n"]), beta2_pf=b2, beta2_goc=float(r["beta2"]),
                             diff=b2 - float(r["beta2"]), rel_diff=(b2 - float(r["beta2"])) / abs(float(r["beta2"])),
                             se_state_pf=s2, se_state_goc=float(r["se_state"]), se_rel_diff=(s2 - float(r["se_state"])) / float(r["se_state"]),
                             se_state_pf_macdinh=s2d, se_rel_diff_macdinh=(s2d - float(r["se_state"])) / float(r["se_state"]),
                             n_coef_pf=k_pf, formula=fml))
        theta += w * b2
        print(f"{th['name']} h={h}: pf {b2:.8f} | gốc {float(r['beta2']):.8f} | n {n_pf} vs {int(r['n'])} | SE bang {s2:.6f} vs {float(r['se_state']):.6f} ({time.time()-t0:.0f}s)", flush=True)
    rows_out.append(dict(stat=th["name"], h="theta", w=np.nan, beta2_pf=theta, beta2_goc=float(conf.loc[th["name"], "theta"]),
                         diff=theta - float(conf.loc[th["name"], "theta"]), rel_diff=(theta - float(conf.loc[th["name"], "theta"])) / abs(float(conf.loc[th["name"], "theta"]))))
out = pd.DataFrame(rows_out)
out.to_csv(os.path.join(HERE, "results_real", "rep_pyfixest.csv"), index=False)
pd.set_option("display.width", 220)
print(out.drop(columns=["formula"]).to_string(index=False))
print("pyfixest", pf.__version__, "; thời gian", round(time.time() - t0), "giây")
