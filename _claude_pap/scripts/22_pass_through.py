"""22_pass_through.py — estimand pass-through (kế hoạch mục 7).
PT_h = [ảnh hưởng của +1 SD nhiệt lên tổn thất tín dụng nông nghiệp của ngân hàng, USD, tích lũy đến h]
       / [−ảnh hưởng của +1 SD nhiệt lên doanh thu cây trồng trong footprint ngân hàng, USD (năm t)].
Tử số: LOSS = Σ_{k=0..h} net charge-off (farmland + vay sản xuất) + Δ(quá hạn 90+ & nonaccrual) (farmland + vay sản xuất) giữa t+h và t−1.
Mẫu chính: ngân hàng nông nghiệp (ag25) MỘT HẠT, t 2006–2022 (BEA đến 2022); mẫu phụ: mọi ngân hàng ag25 (mẫu số = doanh thu footprint-weighted).
Hai hồi quy cùng mẫu, cùng đặc tả họ C (FE ngân hàng + division×năm, mưa z, z², controls t−1).
Khoảng tin cậy: bootstrap theo cụm bang, 999 lần, seed 20261015, rút lại đồng thời cả hai vế. Số mô tả "cent tổn thất ngân hàng trên mỗi USD doanh thu mất";
ngân hàng chỉ nắm một phần nợ nông nghiệp của hạt nên đây là cận dưới theo nghĩa phân bổ.
"""
from _pap_est import *

B = 999
b = load_bank()
X = ["heat"] + RAIN + BANK_CTRL
out = []
for samp, single in (("main_single_county", True), ("secondary_all_ag", False)):
    for h in (1, 2):
        y = f"LOSS_kusd_h{h}"
        s = bank_frame(b, y, h, years=(2006, 2022), extra_dropna=("crop_fp_kusd",))
        if single:
            s = s[s.single_county_main_flag.fillna(False).astype(bool)]
        s = s.copy()
        s["num"] = s[y] * 1000.0
        s["den"] = s["crop_fp_kusd"] * 1000.0
        for col, sub in halves(s).items():
            if sub.hq_state.nunique() < 5:
                continue
            rn = fit_lp(sub, "num", X, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
            rd = fit_lp(sub, "den", X, ["idrssd", "div_year"], se="conley", cty="hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
            recn = record("PT_num", "LOSS_USD", h, samp, col, rn)
            recd = record("PT_den", "crop_fp_USD", 0, samp, col, rd)
            pt = rn["beta"][0] / (-rd["beta"][0])
            # bootstrap theo cụm bang
            fn = FastFE(sub, "num", X, "idrssd", "div_year", "hq_state")
            fd = FastFE(sub, "den", X, "idrssd", "div_year", "hq_state")
            states = sorted(sub.hq_state.unique())
            sid = codes(sub.dropna(subset=["num", "den"] + X + ["idrssd", "div_year", "hq_state"]).hq_state)
            draws = state_draws(states, B, SEED + 100 * h + (0 if single else 7))
            pts = np.empty(B); dens = np.empty(B); nums = np.empty(B)
            for i in range(B):
                w = draws[i][sid].astype(float)
                bn = fn.fit(w)[0]; bd = fd.fit(w)[0]
                nums[i], dens[i], pts[i] = bn, bd, bn / (-bd)
            stable = dens < 0
            ci = np.percentile(pts[stable], [2.5, 97.5]) if stable.sum() > 0.5 * B else (np.nan, np.nan)
            row = dict(sample=samp, half=col, h=h, pt_cents_per_usd=100 * pt, pt_ci95_lo=100 * ci[0], pt_ci95_hi=100 * ci[1], share_den_nonneg=float(1 - stable.mean()),
                       num_usd=rn["beta"][0], num_se=rn["se"][0], den_usd=rd["beta"][0], den_se=rd["se"][0], n=rn["n"], n_banks=rn["n_units"], n_states=sub.hq_state.nunique(), B=B,
                       num_boot_lo=np.percentile(nums, 2.5), num_boot_hi=np.percentile(nums, 97.5), den_boot_lo=np.percentile(dens, 2.5), den_boot_hi=np.percentile(dens, 97.5))
            out.append(row)
            append_spec(dict(timestamp=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), family="PT", outcome=f"PT_h{h}", h=h, spec="boot_state_999", sample=f"{samp}:{col}",
                             beta=100 * pt, ci95_lo=100 * ci[0], ci95_hi=100 * ci[1], n=rn["n"], n_units=rn["n_units"], n_clusters=sub.hq_state.nunique()))
pd.DataFrame(out).to_csv(RES / "pass_through.csv", index=False)
print("[FAKE] xong pass-through" if FAKE else pd.DataFrame(out)[["sample", "half", "h", "pt_cents_per_usd", "pt_ci95_lo", "pt_ci95_hi", "share_den_nonneg", "n"]].round(3).to_string(index=False))
log_run(f"22_pass_through ({'FAKE' if FAKE else 'THẬT'}): {len(out)} ước lượng pass-through, B={B}.")
