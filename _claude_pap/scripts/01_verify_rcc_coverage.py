"""3.1.1 — Dư nợ vay sản xuất nông nghiệp (RC-C, `ag_production_loans_kusd`) có được mọi ngân hàng báo cáo không?
So với coverage quá hạn/nonaccrual vay nông dân (RC-N, có ngưỡng). Không dùng outcome nhiệt; chỉ coverage mô tả.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "out"
P1 = ROOT / "_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet"
ff = pd.read_parquet(ROOT / "_claude_feasibility/out/07_ffiec_ag_bank_year.parquet")
b = pd.read_parquet(P1, columns=["idrssd", "year", "in_contiguous_us_dc", "flag_q4_filing_present", "total_assets_kusd", "total_loans_kusd", "ag_production_loans_kusd", "farmland_loans_kusd"])
b = b[b.in_contiguous_us_dc.astype(bool)].merge(ff[["idrssd", "year", "farm_nonaccrual"]], on=["idrssd", "year"], how="left")
b["q4"] = b.flag_q4_filing_present.astype(bool)
b["size"] = pd.cut(b.total_assets_kusd, [0, 1e5, 3e5, 1e6, np.inf], labels=["<100M", "100–300M", "300M–1B", ">=1B"], right=False)
print("Bank-năm có Q4:", int(b.q4.sum()), "/", len(b))
q = b[b.q4]
rows = []
for sz, g in q.groupby("size", observed=True):
    pos = g.ag_production_loans_kusd > 0
    rows.append({"size": str(sz), "n_q4": len(g), "RCC_ag_prod_nonmissing": g.ag_production_loans_kusd.notna().mean(), "RCC_ag_prod_zero_share": (g.ag_production_loans_kusd == 0).mean(),
                 "RCC_farmland_nonmissing": g.farmland_loans_kusd.notna().mean(),
                 "RCN_1583_nonmissing_if_agprod>0": g.loc[pos, "farm_nonaccrual"].notna().mean(), "n_agprod>0": int(pos.sum())})
t = pd.DataFrame(rows).round(4); print(t.to_string(index=False)); t.to_csv(OUT / "01_rcc_coverage_by_size.csv", index=False)
yr = q.groupby("year").agg(RCC_nonmiss=("ag_production_loans_kusd", lambda s: s.notna().mean()), RCN_nonmiss_if_pos=("farm_nonaccrual", lambda s: np.nan)).drop(columns="RCN_nonmiss_if_pos")
yr["RCN_1583_nonmissing_if_agprod>0"] = q[q.ag_production_loans_kusd > 0].groupby("year").farm_nonaccrual.apply(lambda s: s.notna().mean())
yr.round(4).to_csv(OUT / "01_rcc_coverage_by_year.csv"); print(yr.round(3).T.to_string())
