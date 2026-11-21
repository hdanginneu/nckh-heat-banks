"""ins_offset.py — PHÂN TÍCH LÀM SAU (post hoc, 19/11/2026), không nằm trong kế hoạch v3.
Câu hỏi: tiền bồi thường bảo hiểm cây trồng bù được bao nhiêu phần doanh thu trồng trọt mất đi khi mùa vụ nóng hơn 1 SD?
Đặc tả giống RQ-0 / họ E1 (kế hoạch vòng đầu 15/10/2026): y(c,t) = β·Nhiệt + δ1·mưa_z + δ2·mưa_z² + α_c + τ_(division,t);
SE Conley 1.000 km, trễ 2 năm (hàm fit_lp của scripts/_pap_est.py, không sửa).
Điểm mới so với E1: hai kết cục cùng đơn vị (chia doanh thu trồng trọt gốc 2001–05, USD) trên CÙNG một mẫu,
  R = doanh thu trồng trọt năm t / gốc;  I_hd = bồi thường do hạn + nhiệt + gió nóng (mã 11, 12, 62) / gốc;  I_all = bồi thường mọi nguyên nhân / gốc,
và tỷ lệ bù θ = β_I / (−β_R), khoảng tin cậy theo phương pháp delta với hiệp phương sai chéo Conley.
Hai cách cân: không trọng số (như E1) và trọng số = doanh thu gốc (đọc theo tổng đô la).
Đầu vào: county_panel.parquet (đường dẫn ở argv[1]). Đầu ra: rq3_ins/results_real/ins_offset.csv
"""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from _pap_common import conley_meat, codes          # noqa: E402
from _pap_est import fit_lp, RAIN, Z95              # noqa: E402

panel = Path(sys.argv[1])
b = pd.read_parquet(panel)
b = b[b.year.between(2006, 2022)].copy()
has = b["has_col"].fillna(False).astype(bool)
base_usd = b["base_crop_kusd"].where(b["base_crop_kusd"] > 0) * 1000.0
b["R"] = (b["crop"] * 1000.0 / base_usd)                       # doanh thu năm t / gốc
b["R_lead1"] = b.groupby("fips")["R"].shift(-1).where(b.groupby("fips")["year"].shift(-1) == b["year"] + 1)
b["I_hd"] = (b["indem_hd_main"] / base_usd).where(has)          # = y_indem_hd của E1
b["I_all"] = (b["indem_total"] / base_usd).where(has)
b["w_base"] = base_usd
b["div_year"] = b.division + "_" + b.year.astype(str)
assert np.allclose(b["I_hd"].dropna(), b.loc[b["I_hd"].notna(), "y_indem_hd"]), "I_hd phải trùng y_indem_hd"

X = ["heat"] + RAIN
FE = ["fips", "div_year"]


def joint(s, ys, w=None):
    """Ước lượng các kết cục ys trên cùng mẫu s; trả về β, V chung (Conley, gồm hiệp phương sai chéo) cho hệ số nhiệt."""
    fits = [fit_lp(s, y, X, FE, se="conley", cty="fips", w=w, keep=True) for y in ys]
    n0 = fits[0]["n"]
    assert all(f["n"] == n0 for f in fits), "mẫu phải trùng nhau"
    Xt = fits[0]["Xt"]
    for f in fits[1:]:
        assert np.allclose(f["Xt"], Xt), "Xt phải trùng (cùng mẫu, cùng FE, cùng trọng số)"
    d = fits[0]["d"]
    wv = np.ones(n0) if w is None else d[w].to_numpy(float) / d[w].to_numpy(float).mean()
    cc = codes(d["fips"]); yr = codes(d["year"])
    first = pd.DataFrame({"c": cc, "lat": d["lat"].to_numpy(), "lon": d["lon"].to_numpy()}).drop_duplicates("c").sort_values("c")
    k = Xt.shape[1]
    bread = np.linalg.inv(Xt.T @ (Xt * wv[:, None]))
    U = np.column_stack([Xt * (wv * f["e"])[:, None] for f in fits])
    M = conley_meat(U, np.ones(n0), cc, yr, first.lat.to_numpy(), first.lon.to_numpy(), cutoff=1000.0, lag=2)
    B = np.kron(np.eye(len(ys)), bread)
    V = B @ M @ B
    V = (V + V.T) / 2
    idx = [j * k for j in range(len(ys))]            # vị trí hệ số nhiệt của từng kết cục
    Vh = V[np.ix_(idx, idx)]
    beta = np.array([f["beta"][0] for f in fits])
    # kiểm tra: phương sai riêng khớp fit_lp (khi fit_lp không phải cắt trị riêng âm)
    for j, f in enumerate(fits):
        assert abs(np.sqrt(Vh[j, j]) - f["se"][0]) / f["se"][0] < 1e-6, ("SE lệch fit_lp", ys[j], np.sqrt(Vh[j, j]), f["se"][0])
    return beta, Vh, n0, d["fips"].nunique(), d


def ratio(bI, bR, vII, vRR, vIR):
    th = bI / (-bR)
    g = np.array([-1.0 / bR, bI / bR ** 2])                 # ∂θ/∂bI, ∂θ/∂bR
    V = np.array([[vII, vIR], [vIR, vRR]])
    se = float(np.sqrt(g @ V @ g))
    return th, se


rows = []
base = b.dropna(subset=["R", "I_hd", "I_all", "heat", "ppt_season_z", "lat"]).copy()
for wname, w in (("khong_trong_so", None), ("trong_so_doanh_thu_goc", "w_base")):
    beta, V, n, nc, d = joint(base, ["R", "I_hd", "I_all"], w=w)
    bR, bH, bA = beta
    for nm, j in (("R", 0), ("I_hd", 1), ("I_all", 2)):
        rows.append(dict(sample="cung_mau", weight=wname, outcome=nm, beta=beta[j], se=np.sqrt(V[j, j]),
                         ci95_lo=beta[j] - Z95 * np.sqrt(V[j, j]), ci95_hi=beta[j] + Z95 * np.sqrt(V[j, j]), n=n, n_counties=nc,
                         mean_y=float(np.average(d[nm], weights=None if w is None else d[w]))))
    for nm, j in (("theta_hd", 1), ("theta_all", 2)):
        th, se = ratio(beta[j], bR, V[j, j], V[0, 0], V[j, 0])
        rows.append(dict(sample="cung_mau", weight=wname, outcome=nm, beta=th, se=se, ci95_lo=th - Z95 * se, ci95_hi=th + Z95 * se, n=n, n_counties=nc))

# thời điểm: doanh thu bán năm t+1 (vụ thu hoạch cuối năm t có thể bán năm sau); tổng mất hai năm so với bồi thường năm vụ t
two = b.dropna(subset=["R", "R_lead1", "I_hd", "I_all", "heat", "ppt_season_z", "lat"]).copy()
for wname, w in (("khong_trong_so", None), ("trong_so_doanh_thu_goc", "w_base")):
    beta, V, n, nc, d = joint(two, ["R", "R_lead1", "I_hd", "I_all"], w=w)
    for nm, j in (("R", 0), ("R_lead1", 1), ("I_hd", 2), ("I_all", 3)):
        rows.append(dict(sample="co_t+1", weight=wname, outcome=nm, beta=beta[j], se=np.sqrt(V[j, j]),
                         ci95_lo=beta[j] - Z95 * np.sqrt(V[j, j]), ci95_hi=beta[j] + Z95 * np.sqrt(V[j, j]), n=n, n_counties=nc))
    bL = beta[0] + beta[1]; vL = V[0, 0] + V[1, 1] + 2 * V[0, 1]
    rows.append(dict(sample="co_t+1", weight=wname, outcome="R_t_plus_t1", beta=bL, se=np.sqrt(vL), ci95_lo=bL - Z95 * np.sqrt(vL),
                     ci95_hi=bL + Z95 * np.sqrt(vL), n=n, n_counties=nc))
    for nm, j in (("theta2_hd", 2), ("theta2_all", 3)):
        vIL = V[j, 0] + V[j, 1]
        th, se = ratio(beta[j], bL, V[j, j], vL, vIL)
        rows.append(dict(sample="co_t+1", weight=wname, outcome=nm, beta=th, se=se, ci95_lo=th - Z95 * se, ci95_hi=th + Z95 * se, n=n, n_counties=nc))

out = pd.DataFrame(rows)
out.to_csv(HERE / "results_real" / "ins_offset.csv", index=False)
pd.set_option("display.width", 200)
print(out.round(4).to_string(index=False))
