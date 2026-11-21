"""make_report_figures.py — hình minh hoạ cho bài RQ3 v3 (20/11/2026).

Chạy (trong VS Code hoặc terminal), từ bất kỳ thư mục nào:
    python3 _claude_pap/rq3_figs/make_report_figures.py
Đầu ra: _claude_pap/rq3_figs/out/hinh_*.png (200 dpi) và out/figures_numbers.csv (mọi con số in trên hình, kèm file nguồn).

Hình 3.1  Bản đồ: ngày–độ trên 29°C bình quân 2006–2022 theo hạt; trụ sở ngân hàng theo FarmShare_pre.
Hình 3.2  Nhiệt cấp ngân hàng theo năm cú sốc 2007–2024 (trung vị, khoảng 10–90%).
Hình 4.1  Cửa sổ thời gian của năm thống kê chính C1–C5 (sơ đồ, không có số liệu).
Hình 5.1  Binscatter của RQ-0: ln doanh thu trồng trọt theo nhiệt, sau khi khử FE hạt, FE division × năm và mưa.
Hình 5.2  θ̂ của C1–C5 so với phân phối 1.000 hoán vị năm thời tiết.
Hình 5.4  Phản ứng cộng dồn hai năm của doanh thu trồng trọt, bồi thường bảo hiểm và trợ cấp (cấp hạt).
Không ước lượng lại hệ số nào của bài; riêng Hình 5.1 tính lại phần dư theo đặc tả RQ-0 và kiểm hệ số khớp familyABE.csv.
"""
import os, sys, pickle, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.ticker import FuncFormatter, MaxNLocator

HERE = Path(__file__).resolve().parent                 # _claude_pap/rq3_figs
PAP = HERE.parent                                      # _claude_pap (trong repo)
DATA = Path.home() / "mnt" / "NCKH - NEU"              # dữ liệu lớn (OneDrive), giống ROOT của _v3_spec.py
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(PAP / "scripts"))

# ---------- phong cách chung (bảng màu tham chiếu của skill dataviz; nền trắng để in) ----------
INK, INK2, MUTED, AXIS, GRID = "#0b0b0b", "#52514e", "#898781", "#c3c2b7", "#e1e0d9"
BLUE, BLUE_L, BLUE_D = "#2a78d6", "#86b6ef", "#184f95"
GRAY, GRAY_L = "#8f8e8a", "#f0efec"
ORANGE = "#eb6834"
HEAT = ["#fdeee5", "#fbd3bd", "#f6ad87", "#ef8452", "#d9622a", "#a8461b", "#6f2c10"]   # một sắc cam, nhạt → đậm
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "text.color": INK, "axes.labelcolor": INK2,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelcolor": INK2, "ytick.labelcolor": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 9, "axes.titleweight": "bold", "axes.titlelocation": "left", "figure.dpi": 100,
    "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "white", "legend.frameon": False,
})
# numpy 2.x dùng BLAS Accelerate trên macOS báo nhầm "divide by zero / overflow / invalid value encountered in matmul"
# ngay cả với ma trận ngẫu nhiên; kết quả vẫn hữu hạn và khớp phép nhân không dùng BLAS (đã kiểm 20/11/2026).
# Chỉ tắt đúng cảnh báo này; tính đúng được kiểm bằng assert ở Hình 3.1 (toạ độ hữu hạn) và Hình 5.1 (β khớp familyABE.csv).
warnings.filterwarnings("ignore", message=r".*encountered in matmul", category=RuntimeWarning)
NUMS = []                                              # (hình, nội dung, giá trị, nguồn)
SD_BANK = 234.79366746505397                           # độ lệch chuẩn nhiệt cấp ngân hàng, ngày–độ (rq3_rob/results_real/checks_d.json, D39 sd_gdd_bank)


def vn(x, d=2):
    """Số kiểu Việt Nam: dấu phẩy thập phân, dấu trừ thật."""
    s = f"{x:,.{d}f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return s.replace("-", "−")


def vn_fmt(d):
    return FuncFormatter(lambda x, p: vn(x, d))


def note(fig, text):
    fig.text(0.0, -0.02, text, ha="left", va="top", fontsize=7, color=MUTED, wrap=True)


def save(fig, name):
    p = OUT / f"{name}.png"
    fig.savefig(p)
    plt.close(fig)
    print("đã ghi", p.relative_to(PAP.parent))


# ---------- Hình 3.1: bản đồ ----------
def fig_3_1():
    geo = pickle.loads((DATA / "_claude_eda/out/tab/_geo_cache.pkl").read_bytes())
    heat = pd.read_parquet(DATA / "_claude_eda/out/tab/heat_county_year.parquet", columns=["county_fips", "year", "gdd_ex29"])
    mean_gdd = heat[heat.year.between(2006, 2022)].groupby("county_fips").gdd_ex29.mean()
    bins = [0, 50, 100, 200, 300, 400, 600, 2000]
    cmap, norm = ListedColormap(HEAT), BoundaryNorm(bins, len(HEAT))
    rings, vals = [], []
    for gid, polys in zip(geo["geoid"], geo["polys"]):
        v = mean_gdd.get(gid, np.nan)
        for r in polys:
            rings.append(r); vals.append(v)
    vals = np.array(vals)
    # phép chiếu của _geo_cache: ước lượng ánh xạ (kinh, vĩ độ) → (x, y) bằng đa thức bậc 3 từ tâm hạt
    def centroid(ring):                                # tâm hình học theo diện tích (công thức shoelace)
        x, y = ring[:, 0], ring[:, 1]
        c = x * np.roll(y, -1) - np.roll(x, -1) * y
        a = c.sum() / 2
        return np.array([((x + np.roll(x, -1)) * c).sum() / (6 * a), ((y + np.roll(y, -1)) * c).sum() / (6 * a)])
    cx = np.array([centroid(max(p, key=len)) for p in geo["polys"]])
    lon, lat = np.asarray(geo["lon"]), np.asarray(geo["lat"])
    def design(lo, la):
        lo, la = (np.asarray(lo) + 96) / 30, (np.asarray(la) - 38) / 12
        return np.column_stack([lo ** i * la ** j for i in range(4) for j in range(4 - i)])
    A = design(lon, lat)
    coef = np.linalg.lstsq(A, cx, rcond=None)[0]
    resid = np.abs(A @ coef - cx).max(axis=0)
    # hq_lat/hq_lon trong panel_v3 là tâm của hạt đặt trụ sở năm t−1 (rq3_e41/04_build_panel_ext.py, county_centroids)
    banks = pd.read_parquet(DATA / "_claude_pap/rq3_v3/out/panel_v3.parquet",
                            columns=["idrssd", "year", "farmshare_pre", "hq_lat", "hq_lon", "division", "heat"])
    banks = banks[banks.year.between(2007, 2024)]
    n_all = banks.idrssd.nunique()
    heat_bank = banks.groupby("idrssd").heat.mean() * SD_BANK      # nhiệt trung bình 2007–2024 của từng ngân hàng, ngày–độ
    # mỗi ngân hàng một chấm, ở vị trí trụ sở năm đầu tiên trong mẫu (bảng đã xếp theo idrssd, năm)
    banks = banks.dropna(subset=["hq_lat", "hq_lon", "farmshare_pre"]).drop_duplicates("idrssd")
    bxy = design(banks.hq_lon, banks.hq_lat) @ coef
    assert np.isfinite(bxy).all()
    groups = [("dưới 10%", banks.farmshare_pre < .10, AXIS, 1.2),
              ("10–25%", banks.farmshare_pre.between(.10, .25, inclusive="left"), BLUE_L, 2.0),
              ("từ 25% trở lên", banks.farmshare_pre >= .25, BLUE_D, 2.4)]
    allxy = np.vstack([r for r in rings])
    (x0, y0), (x1, y1) = allxy.min(axis=0), allxy.max(axis=0)
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.7), gridspec_kw={"wspace": 0.04})
    fig.subplots_adjust(bottom=0.2)
    border = LineCollection(geo["border"], colors="white", linewidths=0.35)
    ax = axes[0]
    ok = ~np.isnan(vals)
    pc = PolyCollection([r for r, k in zip(rings, ok) if k], array=vals[ok], cmap=cmap, norm=norm, edgecolors="none", linewidths=0)
    ax.add_collection(pc)
    ax.add_collection(PolyCollection([r for r, k in zip(rings, ok) if not k], facecolors=GRAY_L, edgecolors="none"))
    ax.add_collection(border)
    ax.set_title("(a) Nhiệt mùa vụ theo hạt", fontsize=8.5)
    cax = fig.add_axes([0.14, 0.1, 0.3, 0.03])
    cb = fig.colorbar(pc, cax=cax, orientation="horizontal", ticks=bins[:-1])
    cb.ax.set_xticklabels(["0", "50", "100", "200", "300", "400", "600+"], fontsize=6.8)
    cb.outline.set_visible(False); cb.ax.tick_params(length=0)
    cb.ax.set_title("Ngày–độ trên 29°C, trung bình năm 2006–2022", fontsize=6.8, color=INK2, loc="left", fontweight="normal")
    ax = axes[1]
    ax.add_collection(PolyCollection(rings, facecolors=GRAY_L, edgecolors="none"))
    ax.add_collection(LineCollection(geo["border"], colors="white", linewidths=0.35))
    for lab, m, col, sz in groups:
        ax.scatter(bxy[m.to_numpy(), 0], bxy[m.to_numpy(), 1], s=sz, c=col, linewidths=0, label=f"{lab} ({m.sum():,})".replace(",", "."), zorder=3)
    ax.set_title("(b) Trụ sở ngân hàng theo FarmShare", fontsize=8.5)
    ax.legend(loc="upper left", bbox_to_anchor=(0.04, -0.01), ncol=1, fontsize=6.8, markerscale=3.0, handletextpad=0.3,
              labelspacing=0.25, title="FarmShare_pre (số ngân hàng)", title_fontsize=6.8, alignment="left")
    for ax in axes:
        ax.set_xlim(x0 - 0.005, x1 + 0.005); ax.set_ylim(y0 - 0.005, y1 + 0.005); ax.set_aspect("equal"); ax.axis("off")
    save(fig, "hinh_3_1_ban_do")
    NUMS.extend([("3.1", "số hạt trên bản đồ có nhiệt / tổng", f"{int(sum(g in mean_gdd.index for g in geo['geoid']))} / {len(geo['geoid'])}", "heat_county_year.parquet; _geo_cache.pkl"),
                 ("3.1", "trung vị ngày–độ/hạt 2006–2022", round(float(mean_gdd.median()), 1), "heat_county_year.parquet"),
                 ("3.1", "sai số lớn nhất của phép chiếu xấp xỉ (đơn vị bản đồ)", round(float(resid.max()), 4), "_geo_cache.pkl"),
                 ("3.1", "sai số chiếu lớn nhất / bề ngang bản đồ", round(float(resid.max() / (x1 - x0)), 4), "_geo_cache.pkl"),
                 ("3.1", "số ngân hàng trong mẫu 2007–2024 / có FarmShare_pre và toạ độ", f"{n_all} / {len(banks)}", "panel_v3.parquet"),
                 ("3.1", "số ngân hàng", len(banks), "panel_v3.parquet"),
                 ("3.1", "ngân hàng FarmShare ≥ 25%", int(groups[2][1].sum()), "panel_v3.parquet"),
                 ("3.1", "ngân hàng FarmShare 10–25%", int(groups[1][1].sum()), "panel_v3.parquet"),
                 ("3.1", "tỷ lệ ngân hàng FarmShare ≥ 25% có trụ sở ở West North Central", round(float((banks.division[groups[2][1]] == "West North Central").mean()), 3), "panel_v3.parquet"),
                 ("3.1", "nhiệt TB 2007–2024 của ngân hàng trung vị, FarmShare ≥ 25% / 10–25% / dưới 10% (ngày–độ)",
                  " / ".join(f"{heat_bank.reindex(banks.idrssd[groups[i][1]]).median():.1f}" for i in (2, 1, 0)), "panel_v3.parquet")])


# ---------- Hình 3.2: nhiệt cấp ngân hàng theo năm ----------
def fig_3_2():
    b = pd.read_parquet(DATA / "_claude_pap/rq3_v3/out/panel_v3.parquet", columns=["idrssd", "year", "heat"])
    b = b[b.year.between(2007, 2024)].dropna(subset=["heat"])          # năm cú sốc của mẫu ngân hàng (mục 3.1)
    SD = SD_BANK
    g = b.groupby("year").heat.agg(med="median", p10=lambda s: s.quantile(.1), p90=lambda s: s.quantile(.9)) * SD
    hot = g.med.idxmax()
    fig, ax = plt.subplots(figsize=(6.6, 2.3))
    for yr, r in g.iterrows():
        col = ORANGE if yr == hot else GRAY
        ax.plot([yr, yr], [r.p10, r.p90], color=col, lw=2, solid_capstyle="round", alpha=0.9 if yr == hot else 0.55)
        ax.plot(yr, r.med, "o", ms=5, color=col, mec="white", mew=0.8, zorder=3)
    ax.annotate(f"{hot}: trung vị {vn(g.med[hot], 0)} ngày–độ", (hot, g.p90[hot]), xytext=(hot + 0.6, g.p90[hot] * 0.98),
                fontsize=7.5, color=INK, va="top")
    ax.set_xticks(range(2008, 2025, 2)); ax.set_xlim(2006.4, 2024.6)
    ax.set_ylim(0, None); ax.yaxis.set_major_formatter(vn_fmt(0)); ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.set_ylabel("Ngày–độ trên 29°C\n(cân theo tiền gửi chi nhánh)")
    ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    save(fig, "hinh_3_2_nhiet_theo_nam")
    NUMS.extend([("3.2", f"trung vị năm nóng nhất ({hot})", round(float(g.med[hot]), 1), "panel_v3.parquet × SD 234,79"),
                 ("3.2", "trung vị thấp nhất", f"{g.med.idxmin()}: {round(float(g.med.min()), 1)}", "panel_v3.parquet"),
                 ("3.2", "số ngân hàng–năm", len(b), "panel_v3.parquet"),
                 ("3.2", "chênh trung vị cao nhất − thấp nhất", round(float(g.med.max() - g.med.min()), 1), "panel_v3.parquet"),
                 ("3.2", "độ rộng P10–P90 trong năm, nhỏ nhất / lớn nhất", f"{(g.p90 - g.p10).min():.1f} / {(g.p90 - g.p10).max():.1f}", "panel_v3.parquet")])


# ---------- Hình 4.1: cửa sổ thời gian ----------
def fig_4_1():
    rows = [("C1", "Tổn thất ròng cộng dồn", [(0, 6, BLUE, "cộng dồn t … t+6")], False),
            ("C2", "Dự phòng muộn − sớm", [(0, 1, BLUE_L, "sớm (trừ)"), (3, 6, BLUE_D, "muộn (cộng)")], True),
            ("C3", "Quá hạn sớm, đất NN", [(0, 1, BLUE, "trung bình h = 0, 1")], True),
            ("C4", "Thanh khoản", [(0, 0, BLUE, "h = 0")], True),
            ("C5", "Dư nợ nông nghiệp", [(2, 2, BLUE, "h = 2")], True)]
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ax.axvspan(-0.5, 0.5, color="#fbd3bd", alpha=0.55, lw=0, zorder=0)
    ax.text(0, len(rows) - 0.35, "năm nóng", ha="center", va="bottom", fontsize=7.5, color="#a8461b")
    for i, (code, name, segs, base) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.text(-4.75, y, code, ha="left", va="center", fontsize=8.5, fontweight="bold", color=INK)
        ax.text(-4.3, y, name, ha="left", va="center", fontsize=7.5, color=INK2)
        if base:
            ax.plot(-1, y, "o", ms=5, mfc="white", mec=INK2, mew=1, zorder=3)
            ax.plot([-1, segs[-1][1]], [y, y], color=AXIS, lw=0.8, zorder=1)
        for a, b_, col, lab in segs:
            ax.barh(y, b_ - a + 0.7, left=a - 0.35, height=0.42, color=col, zorder=2)
            ax.text((a + b_) / 2, y + 0.3, lab, ha="center", va="bottom", fontsize=6.8, color=INK2)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_xticks(range(-1, 7)); ax.set_xticklabels(["t−1", "t", "t+1", "t+2", "t+3", "t+4", "t+5", "t+6"])
    ax.set_xlim(-4.8, 6.6); ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.spines["bottom"].set_bounds(-1.4, 6.6)
    ax.plot([], [], "o", ms=5, mfc="white", mec=INK2, label="mốc so sánh t−1 (biến kết quả là thay đổi từ t−1)")
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, -0.12), fontsize=7)
    save(fig, "hinh_4_1_cua_so_thong_ke")


# ---------- Hình 5.1: binscatter RQ-0 ----------
def fig_5_1():
    from _pap_common import absorb, codes
    # Trên Mac: DATA/_claude_pap là symlink về repo, county_panel.parquet trỏ tiếp về OneDrive _handoff_v3.
    # Trong VM Cowork symlink đó gãy, nên thử thêm đường dẫn thẳng vào _handoff_v3.
    cands = [DATA / "_claude_pap/out/county_panel.parquet",
             DATA / "_handoff_v3/data_inputs/_claude_pap/out/county_panel.parquet"]
    d = pd.read_parquet(next(p for p in cands if p.exists()))
    d = d[d.year.between(2006, 2022)].dropna(subset=["y_lncrop", "heat", "ppt_season_z"]).copy()
    d["div_year"] = d.division + "_" + d.year.astype(str)
    Z = absorb(d[["y_lncrop", "heat", "ppt_season_z", "ppt_z2"]].to_numpy(float), [codes(d.fips), codes(d.div_year)])
    y, x, C = Z[:, 0], Z[:, 1], Z[:, 2:]
    y = y - C @ np.linalg.lstsq(C, y, rcond=None)[0]       # Frisch–Waugh–Lovell: bỏ phần do mưa
    x = x - C @ np.linalg.lstsq(C, x, rcond=None)[0]
    beta = float(x @ y / (x @ x))
    ref = pd.read_csv(PAP / "out/results/familyABE.csv")
    ref = ref[(ref.family == "A") & (ref["sample"] == "full")].iloc[0]
    assert abs(beta - ref.beta) < 1e-6 and len(d) == int(ref.n), (beta, ref.beta, len(d), ref.n)
    q = pd.qcut(x, 20, labels=False)
    bx = pd.Series(x).groupby(q).mean(); by = pd.Series(y).groupby(q).mean()
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    xs = np.linspace(bx.min() * 1.05, bx.max() * 1.05, 50)
    ax.plot(xs, beta * xs, color=INK2, lw=1, zorder=1)
    ax.plot(bx, by, "o", ms=5.5, color=BLUE, mec="white", mew=0.8, zorder=2)
    ax.axhline(0, color=AXIS, lw=0.6, zorder=0); ax.axvline(0, color=AXIS, lw=0.6, zorder=0)
    ax.text(0.98, 0.95, f"Độ dốc β = {vn(beta, 3)}\n(sai số chuẩn Conley {vn(ref.se, 3)})\n{vn(len(d), 0)} hạt–năm",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5, color=INK)
    ax.set_xlabel("Nhiệt mùa vụ, phần dư (độ lệch chuẩn, 232,7 ngày–độ)")
    ax.set_ylabel("ln doanh thu trồng trọt, phần dư")
    ax.xaxis.set_major_formatter(vn_fmt(1)); ax.yaxis.set_major_formatter(vn_fmt(2))
    save(fig, "hinh_5_1_binscatter_rq0")
    NUMS.extend([("5.1", "β tái tính (khớp familyABE A full)", round(beta, 5), "county_panel.parquet; out/results/familyABE.csv"),
                 ("5.1", "SE Conley (lấy từ familyABE)", round(float(ref.se), 5), "out/results/familyABE.csv"),
                 ("5.1", "n", len(d), "county_panel.parquet")])


# ---------- Hình 5.2: phân phối hoán vị ----------
def fig_5_2():
    z = np.load(PAP / "rq3_v3/results_real/perm_theta.npz")
    conf = pd.read_csv(PAP / "rq3_v3/results_real/v3_confirmatory.csv").set_index("name")
    names = {"C1": "C1 Tổn thất", "C2": "C2 Dự phòng", "C3": "C3 Quá hạn", "C4": "C4 Thanh khoản", "C5": "C5 Dư nợ NN"}
    fig, axes = plt.subplots(1, 5, figsize=(6.8, 2.1), gridspec_kw={"wspace": 0.3})
    for ax, k in zip(axes, names):
        th, dl, p, pwy = conf.loc[k, ["theta", "sesoi_primary", "p_RI", "p_WY"]]
        perm = z[k]
        lim = max(np.abs(perm).max(), abs(th), dl) * 1.08
        ax.axvspan(-dl, dl, color=GRAY_L, lw=0, zorder=0)
        cnt, _, _ = ax.hist(perm, bins=np.linspace(-lim, lim, 31), color=AXIS, edgecolor="white", linewidth=0.4, zorder=1)
        ax.set_ylim(0, cnt.max() * 1.55)
        col = ORANGE if pwy < 0.05 else BLUE
        ax.plot([th, th], [0, cnt.max() * 1.12], color=col, lw=1.6, zorder=3, solid_capstyle="butt")
        ax.set_title(names[k], fontsize=7.5, loc="left")
        ax.text(0.0, 0.98, f"θ̂ = {vn(th, 3)}\np = {vn(p, 3)}", transform=ax.transAxes, ha="left", va="top", fontsize=6.6, color=INK)
        ax.set_yticks([]); ax.spines["left"].set_visible(False)
        ax.xaxis.set_major_locator(MaxNLocator(3, symmetric=True)); ax.xaxis.set_major_formatter(vn_fmt(2 if lim < 0.5 else 1))
        ax.tick_params(axis="x", labelsize=6.5)
        NUMS.append(("5.2", f"{k}: θ̂, Δ, p hoán vị, p WY, tỷ lệ hoán vị có |θ*| ≤ Δ",
                     f"{th:.4f}; {dl:.4f}; {p:.3f}; {pwy:.3f}; {np.mean(np.abs(perm) <= dl):.3f}", "v3_confirmatory.csv; perm_theta.npz"))
    save(fig, "hinh_5_2_hoan_vi")


# ---------- Hình 5.4: bồi thường so với doanh thu mất ----------
def fig_5_4():
    c = pd.read_csv(PAP / "rq3_ins/results_real/ins_offset_cum.csv")
    c = c[c.weight == "trong_so_doanh_thu_goc"].set_index("outcome")
    rows = [("R", "Doanh thu trồng trọt", INK2), ("I_hd", "Bồi thường do hạn, nhiệt, gió nóng", BLUE),
            ("I_all", "Bồi thường mọi nguyên nhân", BLUE_L), ("G", "Trợ cấp chính phủ", AXIS)]
    fig, ax = plt.subplots(figsize=(6.6, 2.2))
    for i, (k, lab, col) in enumerate(rows):
        y = len(rows) - 1 - i
        r = c.loc[k]
        ax.barh(y, r.b_cum, height=0.55, color=col, zorder=2)
        ax.plot([r.cum_lo, r.cum_hi], [y, y], color=INK, lw=0.9, zorder=3)
        for e in (r.cum_lo, r.cum_hi):
            ax.plot([e, e], [y - 0.1, y + 0.1], color=INK, lw=0.9, zorder=3)
        txt = vn(r.b_cum, 3) + ("" if k == "R" else f"  ·  {vn(r.theta * 100, 0)}% phần mất")
        ax.text(max(r.cum_hi, 0) + 0.012, y, txt, ha="left", va="center", fontsize=7.5, color=INK)
    ax.axvline(0, color=INK2, lw=0.8, zorder=1)
    ax.set_xlim(-0.6, 0.5); ax.set_yticks([len(rows) - 1 - i for i in range(len(rows))]); ax.set_yticklabels([r[1] for r in rows], fontsize=7.8, color=INK)
    ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
    ax.set_xticks([-0.6, -0.4, -0.2, 0, 0.2]); ax.xaxis.set_major_formatter(vn_fmt(1))
    ax.set_xlabel("Lần doanh thu trồng trọt gốc 2001–2005; cộng dồn năm t và t+1; khoảng tin cậy 95%")
    ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
    save(fig, "hinh_5_4_bao_hiem")
    for k, lab, _ in rows:
        r = c.loc[k]
        NUMS.append(("5.4", lab, f"{r.b_cum:.4f} [{r.cum_lo:.4f}; {r.cum_hi:.4f}]" + ("" if k == "R" else f"; bù {r.theta:.4f}"), "rq3_ins/results_real/ins_offset_cum.csv"))


if __name__ == "__main__":
    for f in (fig_3_1, fig_3_2, fig_4_1, fig_5_1, fig_5_2, fig_5_4):
        f()
    pd.DataFrame(NUMS, columns=["hinh", "noi_dung", "gia_tri", "nguon"]).to_csv(OUT / "figures_numbers.csv", index=False)
    print("xong; số liệu in trên hình ở", (OUT / "figures_numbers.csv").relative_to(PAP.parent))
