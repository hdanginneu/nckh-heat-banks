"""checks_e.py — mô tả, LÀM SAU (19/11/2026); không đổi kết quả nào. E47: đặt cận trên tổn thất cạnh lợi nhuận ròng một năm.
Nhóm tham chiếu giống E46 của checks_d.py: ngân hàng FarmShare_pre trong (15%; 35%], năm 2007–2024.
Lợi nhuận ròng = net_income_ytd_kusd cuối năm (Call Report, cộng dồn cả năm); vốn cấp 1 = tier1_capital_kusd cuối năm (> 0).
Lệnh: python3 checks_e.py → results_real/checks_e.json"""
import os, json
import numpy as np, pandas as pd
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
PANEL = f"{ROOT}/_claude_pap/rq3_v3/out/panel_v3.parquet"
P1F = f"{ROOT}/_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet"
D = os.path.dirname(os.path.abspath(__file__))
B = pd.read_parquet(PANEL, columns=["idrssd", "year", "farmshare_pre"])
p1 = pd.read_parquet(P1F, columns=["idrssd", "year", "net_income_ytd_kusd", "q4_net_income_ytd_kusd", "tier1_capital_kusd",
                                   "net_chargeoffs_ytd_kusd", "total_loans_kusd"]).drop_duplicates(["idrssd", "year"])
p1["idrssd"] = pd.to_numeric(p1.idrssd).astype(B.idrssd.dtype)
ref = B[(B.farmshare_pre > .15) & (B.farmshare_pre <= .35) & B.year.between(2007, 2024)][["idrssd", "year"]].merge(p1, on=["idrssd", "year"], how="left")
ok = ref.tier1_capital_kusd > 0
ni_t1 = (ref.net_income_ytd_kusd / ref.tier1_capital_kusd).where(ok)
nco_t1 = (ref.net_chargeoffs_ytd_kusd / ref.tier1_capital_kusd).where(ok)
same_q4 = float((ref.net_income_ytd_kusd == ref.q4_net_income_ytd_kusd)[ref.q4_net_income_ytd_kusd.notna()].mean())
med = float(ni_t1.median())
fn = pd.read_csv(f"{D}/results_real/final_numbers.csv").set_index("stat")
l2t = json.load(open(f"{D}/results_real/final_numbers_note.json"))["loans_to_tier1"]
pool = pd.read_csv(f"{D}/../rq3_e41/results_real/pooled_e41.csv").set_index("stat")
b_main = float(fn.loc["C1", "pct_von_cap1"])                       # cận trên C1, % vốn cấp 1 (Bảng 5)
b_pool = float(pool.loc["C1", "can_tren_FS25"]) * l2t               # cận trên C1 gộp hai mẫu, % vốn cấp 1
out = {"E47": dict(n_bank_years=int(len(ref)), n_with_ni_and_t1=int(ni_t1.notna().sum()), n_banks=int(ref.idrssd.nunique()),
                   share_ni_equals_q4_ytd=same_q4,
                   median_ni_to_tier1=med, p25_ni_to_tier1=float(ni_t1.quantile(.25)), p75_ni_to_tier1=float(ni_t1.quantile(.75)),
                   share_bank_years_loss=float((ni_t1 < 0).mean()),
                   median_nco_to_tier1=float(nco_t1.median()),
                   bound_c1_pct_tier1=b_main, bound_c1_pooled_pct_tier1=b_pool,
                   bound_as_share_of_one_year_ni=b_main / 100 / med, pooled_bound_as_share_of_one_year_ni=b_pool / 100 / med)}
json.dump(out, open(f"{D}/results_real/checks_e.json", "w"), indent=1, ensure_ascii=False, default=float)
print(json.dumps(out, indent=1, ensure_ascii=False, default=float))
