"""sesoi_v3.py — tính SESOI (Δ_C) cho C1–C5 theo PAP_v3.md §6 và ghi sesoi_v3.json (được đóng băng cùng PAP).
Chỉ dùng thống kê mô tả KHÔNG điều kiện theo nhiệt (trung bình, độ lệch chuẩn của outcome); không ước lượng hệ số nào.
Δ_C = r_C × ȳ_C / 2,5 (C1–C3): r_C = tác động tương đối trong bài gốc (PAP_v3_SESOI.md của Mai, số in trong bài);
  ȳ_C = mức trung bình của biến tương ứng ở nhóm tham chiếu FarmShare_pre ∈ (15%, 35%] (quanh mức 25% của phép so sánh tham chiếu);
  chia 2,5 vì θ tính cho +10 điểm % FarmShare còn phép so sánh tham chiếu là FS 25% so với 0 (quy ước PAP v2), nhiệt +1 SD.
Δ_C = 0,10 × SD(y) / 2,5 (C4, C5): quy ước kế thừa PAP v2 (đã đóng băng trước khi có kết quả v2); không có neo tài liệu."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["SPEC"] = "main"
from _v3_spec import *            # noqa: F401,F403
from build_v3 import lookup

R_ANCHOR = {   # nguồn: PAP_v3_SESOI.md (Mai, 09/11/2026), mục 1.2–1.3
    "C1": dict(primary=0.126, alt=0.063, src="Lu & Nikolaev 2024, Bảng 2A: lỗ muộn năm 5–6 cộng 2 năm = 12,6% NCO bình quân một năm; alt = 6,3% (một năm)"),
    "C2": dict(primary=0.020, alt=0.022, src="Lu & Nikolaev 2024, Bảng 2A cột 4: ALL muộn trừ sớm = 2,0% ALL bình quân (ghép cách A); alt = 2,2% (cách B)"),
    "C3": dict(primary=0.092, alt=0.25, src="Özsoy et al. 2025, Bảng 2 cột 4: cận dưới một phía 5% = 9,2% NPL bình quân; alt = 25% (ước lượng điểm +0,40 điểm %)"),
}

def wmean(x, p=0.01):
    x = x.dropna(); lo, hi = x.quantile([p, 1 - p]); return float(x.clip(lo, hi).mean()), int(len(x))

b = pd.read_parquet(PANEL, columns=["idrssd", "year", "farmshare_pre", "totloans_l1", "NCOc_h0", "ALLOWlag"])
ref = b[(b.farmshare_pre > .15) & (b.farmshare_pre <= .35)]
P = lookup(b.idrssd.dtype)
idx = pd.MultiIndex.from_arrays([ref.idrssd.to_numpy(), ref.year.to_numpy() - 1])
pd_l1 = pd.Series(P["pdna_fl"].reindex(idx).to_numpy(), index=ref.index)
ybar = {
    "C1": wmean(ref.loc[ref.year.between(2007, 2024), "NCOc_h0"]),                                   # NCO ròng năm, % dư nợ t−1
    "C2": wmean(ref.loc[ref.year.between(2007, 2022), "ALLOWlag"]),                                  # dự phòng t−1, % dư nợ t−1
    "C3": wmean((100 * pd_l1 / ref.totloans_l1.where(ref.totloans_l1 > 0))[ref.year.between(2007, 2024)]),   # (30–89 + nonaccrual) đất NN t−1, % dư nợ t−1
}
out = {}
for C in ("C1", "C2", "C3"):
    y, n = ybar[C]; a = R_ANCHOR[C]
    out[C] = dict(primary=a["primary"] * y / 2.5, alt=a["alt"] * y / 2.5, r_primary=a["primary"], r_alt=a["alt"], ybar_ref=y, n_ref=n, rule="r × ȳ_ref / 2,5", source=a["src"])
B = load_panel(False)
for C in ("C4", "C5"):
    th = [t for t in thetas() if t["name"] == C][0]; h = th["hs"][0]
    s = make_frame(B, C, f"{th['var']}_h{h}", h)
    sd = float(np.std(s[f"{th['var']}_h{h}"].to_numpy(float)))
    out[C] = dict(primary=0.10 * sd / 2.5, alt=None, sd_y=sd, n=int(len(s)), rule="0,10 × SD(y trong mẫu ước lượng, sau winsorize) / 2,5", source="quy ước kế thừa PAP v2 (ΔLIQ); không có neo tài liệu")
json.dump(out, open(f"{HERE}/sesoi_v3.json", "w"), indent=1, ensure_ascii=False)
for C, v in out.items(): print(C, {k: (round(x, 5) if isinstance(x, float) else x) for k, x in v.items() if k not in ("source", "rule")})
