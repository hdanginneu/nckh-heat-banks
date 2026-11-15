"""03_sod_weights.py — trọng số tiền gửi t−1 theo hạt (năm phân tích = năm SOD + 1) cho 1995–2006, cùng quy tắc Phase 2:
  w(b,t,c) = tiền gửi chi nhánh của b ở hạt c trong SOD t−1 / tổng tiền gửi dương của b ở 48 bang liền kề + DC (mã hạt hợp lệ).
  Không chuẩn hoá lại khi hạt không có số liệu thời tiết (giữ đúng quy tắc wsum ≥ 0,98 của mẫu chính).
  Hạt trụ sở t−1 = hạt của chi nhánh BRNUM = 0.
Mã hạt cũ đổi sang mã TIGER 2024 (lưới dữ liệu nhiệt): 12025→12086 (Miami-Dade, 1997), 46113→46102 (2015), 51560→51005, 51780→51083,
51515→51019, 30113→30031 (Yellowstone NP, giải thể 1997). Connecticut: SOD dùng 8 hạt cũ, lưới 2024 dùng 9 vùng quy hoạch không khớp
ranh giới hạt → tiền gửi CT để KHÔNG ánh xạ được (trọng số bị thiếu, ngân hàng CT rơi khỏi mẫu qua quy tắc wsum ≥ 0,98). Ghi là hạn chế.
Kiểm: dựng analysis_year 2005 từ SOD 2004 tự tải, so với phase2_footprint_weights_lag1 (năm 2005). Phase 2 gán chi nhánh vào hạt
theo toạ độ SIMS (lưới TIGER 2024), không theo mã hạt khai báo STCNTYBR; một số chi nhánh có toạ độ mặc định (vd. tâm bang IL)
nên bị gán sai hạt. E41 dùng STCNTYBR. Script đo mức lệch nhiệt năm 2006 giữa hai cách.
Đầu ra: OUT/fw_1995_2006.parquet, OUT/hq_1995_2006.parquet, OUT/check_03.txt"""
import numpy as np, pandas as pd
from e41_common import EXT, OUT, FW, SODY

RECODE = {12025: 12086, 46113: 46102, 51560: 51005, 51780: 51083, 51515: 51019, 30113: 30031}
NONCONUS = {2, 15, 60, 66, 69, 72, 78}

def weights(sod_year):
    s = pd.read_parquet(f"{EXT}/sod/sod_{sod_year}.parquet")
    s["cf"] = s.STCNTYBR.replace(RECODE).astype(int); st = s.cf // 1000
    s["dep"] = pd.to_numeric(s.DEPSUMBR, errors="coerce")
    ok = (s.dep > 0) & (s.cf % 1000 > 0) & ~st.isin(NONCONUS) & (st <= 56)
    tot = s[ok].groupby("RSSDID").dep.sum().rename("main_conus")
    c = s[ok].groupby(["RSSDID", "cf"]).dep.sum().rename("cdep").reset_index().merge(tot, left_on="RSSDID", right_index=True)
    c["deposit_weight_l1"] = c.cdep / c.main_conus
    c = c.rename(columns={"RSSDID": "idrssd", "cf": "county_fips"}); c["analysis_year"] = sod_year + 1
    hq = s[s.BRNUM == 0].drop_duplicates("RSSDID")[["RSSDID", "cf"]].rename(columns={"RSSDID": "idrssd", "cf": "hq_county_fips_l1"})
    hq["year"] = sod_year + 1
    return c[["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"]], hq

def main():
    W, H = zip(*[weights(y) for y in range(1994, 2006)])
    fw, hq = pd.concat(W, ignore_index=True), pd.concat(H, ignore_index=True)
    fw.to_parquet(f"{OUT}/fw_1995_2006.parquet", index=False); hq.to_parquet(f"{OUT}/hq_1995_2006.parquet", index=False)
    # kiểm với Phase 2 năm phân tích 2005
    p = pd.read_parquet(FW, columns=["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"]); p = p[p.analysis_year == 2005]
    p["idrssd"] = pd.to_numeric(p.idrssd); p["county_fips"] = pd.to_numeric(p.county_fips)
    m = fw[fw.analysis_year == 2005].merge(p, on=["idrssd", "county_fips"], how="outer", suffixes=("_e41", "_p2"), indicator=True)
    both = m[m._merge == "both"]; d = (both.deposit_weight_l1_e41 - both.deposit_weight_l1_p2).abs()
    ph = pd.read_parquet(SODY, columns=["analysis_year", "idrssd", "hq_county_fips_l1"]); ph = ph[ph.analysis_year == 2005]
    ph["idrssd"] = pd.to_numeric(ph.idrssd); ph["hq_county_fips_l1"] = pd.to_numeric(ph.hq_county_fips_l1, errors="coerce")
    hm = hq[hq.year == 2005].merge(ph, on="idrssd", suffixes=("_e41", "_p2"))
    L = [f"Kiểm năm phân tích 2005 (SOD 2004): cặp (ngân hàng, hạt) chung {len(both):,}; chỉ ở E41 {int((m._merge=='left_only').sum()):,}; "
         f"chỉ ở Phase 2 {int((m._merge=='right_only').sum()):,}",
         f"|lệch trọng số| trên cặp chung: trung vị {d.median():.2e}, p99 {d.quantile(.99):.2e}, lớn nhất {d.max():.2e}; tỷ lệ lệch > 1e-6: {(d > 1e-6).mean():.2%}",
         f"Chỉ ở Phase 2 theo bang (đầu): {(m[m._merge=='right_only'].county_fips // 1000).value_counts().head(5).to_dict()}",
         f"Chỉ ở E41 theo bang (đầu): {(m[m._merge=='left_only'].county_fips // 1000).value_counts().head(5).to_dict()}",
         f"Hạt trụ sở khớp: {(hm.hq_county_fips_l1_e41 == hm.hq_county_fips_l1_p2).mean():.2%} trên {len(hm):,} ngân hàng chung"]
    # cùng ngân hàng, năm phân tích 2006: nhiệt dựng từ hạt khai báo (E41) so với hạt theo toạ độ (Phase 2), đơn vị SD nhiệt của mẫu chính
    import json
    from e41_common import ROOT, TAB
    sd = json.load(open(f"{ROOT}/_claude_pap/out/bank_scales.json"))["sd_gdd_bank"]
    h = pd.read_parquet(f"{TAB}/heat_county_year.parquet", columns=["county_fips", "year", "gdd_ex29"]); h["county_fips"] = pd.to_numeric(h.county_fips)
    h6 = h[h.year == 2006].set_index("county_fips").gdd_ex29
    def bank_heat(w):
        w = w.assign(g=w.county_fips.map(h6)); w = w[w.g.notna()]
        return (w.deposit_weight_l1 * w.g).groupby(w.idrssd).sum() / sd, w.deposit_weight_l1.groupby(w.idrssd).sum()
    p6 = pd.read_parquet(FW, columns=["analysis_year", "idrssd", "county_fips", "deposit_weight_l1"]); p6 = p6[p6.analysis_year == 2006]
    p6["idrssd"] = pd.to_numeric(p6.idrssd); p6["county_fips"] = pd.to_numeric(p6.county_fips)
    he, we = bank_heat(fw[fw.analysis_year == 2006]); hp, wp = bank_heat(p6)
    k = pd.concat([he.rename("e"), hp.rename("p"), we.rename("we"), wp.rename("wp")], axis=1).dropna()
    k = k[(k.we >= .98) & (k.wp >= .98)]; dd = (k.e - k.p).abs()
    L.append(f"Nhiệt 2006 (đơn vị SD mẫu chính), {len(k):,} ngân hàng có wsum ≥ 0,98 ở cả hai cách: tương quan {k.e.corr(k.p):.4f}; "
             f"|lệch| trung vị {dd.median():.3g}, p95 {dd.quantile(.95):.3g}, lớn nhất {dd.max():.3g}; tỷ lệ |lệch| > 0,1 SD: {(dd > .1).mean():.2%}")
    open(f"{OUT}/check_03.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L))

if __name__ == "__main__":
    main()
