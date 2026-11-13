"""Vá run_p2.py: thêm R-P1b (mẫu số trừ nợ ngừng dồn tích) và R-P2/P3a (chỉ nhiệt năm t, cùng mẫu)."""
import sys
f = sys.argv[1]
s = open(f).read()

old = '''    p1["YLD"] = 100 * p1.ag_int_ytd / avg                                            # lãi suất hiệu dụng vay sản xuất NN (%/năm)'''
new = '''    p1["YLD"] = 100 * p1.ag_int_ytd / avg                                            # lãi suất hiệu dụng vay sản xuất NN (%/năm)
    p1["AGAVG"] = avg'''
assert old in s; s = s.replace(old, new)

old = '''    P = P.join(p1[["YLD", "elig", "total_assets_kusd", "dep_trans", "dep_nontrans", "q4_ag_production_loans_kusd"]], how="left")'''
new = '''    P = P.join(p1[["YLD", "AGAVG", "ag_int_ytd", "elig", "total_assets_kusd", "dep_trans", "dep_nontrans", "q4_ag_production_loans_kusd"]], how="left")
    perf = P.AGAVG - P.farm_nonaccrual.fillna(0)
    P["YLDp"] = 100 * P.ag_int_ytd / perf.where(perf > 0)                            # R-P1b: mẫu số = dư nợ đang sinh lãi'''
assert old in s; s = s.replace(old, new)

old = '''    B["P1_h0"] = np.where(e1, at("YLD", 0) - at("YLD", -1), np.nan)'''
new = '''    B["P1_h0"] = np.where(e1, at("YLD", 0) - at("YLD", -1), np.nan)
    B["P1_perf"] = np.where(e1, at("YLDp", 1) - at("YLDp", -1), np.nan)'''
assert old in s; s = s.replace(old, new)

s = s.replace('''ycols = ["P1", "P1_h0", "P1_pl",''', '''ycols = ["P1", "P1_h0", "P1_perf", "P1_pl",''')

old = '''         dict(id="S1_trans_pre12", y="S1_trans", t=(2007, 2011), **ONE), dict(id="S1_trans_post12", y="S1_trans", t=(2012, 2024), **ONE)]'''
new = '''         dict(id="S1_trans_pre12", y="S1_trans", t=(2007, 2011), **ONE), dict(id="S1_trans_post12", y="S1_trans", t=(2012, 2024), **ONE),
         dict(id="P1_perf", y="P1_perf", t=(2007, 2023), **ONE),
         dict(id="P2_one", y="P2", t=(2007, 2024), ctrl=TWO["ctrl"], lag=False, same_as_lag=True),
         dict(id="P3_one", y="P3", t=(2007, 2022), ctrl=TWO["ctrl"], lag=False, same_as_lag=True)]'''
assert old in s; s = s.replace(old, new)

old = '''extra_dropna=["FS10"] + Z_INT + d["ctrl"] + (["heat_l1"] if d["lag"] else []))'''
new = '''extra_dropna=["FS10"] + Z_INT + d["ctrl"] + (["heat_l1"] if d["lag"] or d.get("same_as_lag") else []))'''
assert old in s; s = s.replace(old, new)
open(f, "w").write(s)
print("patched")
