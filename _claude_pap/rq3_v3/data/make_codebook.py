"""make_codebook.py — sinh codebook_v3.csv: mỗi biến v3 kèm mã Call Report, tên mục và khoảng hiệu lực LẤY TRỰC TIẾP từ MDRM_CSV
(Federal Reserve MDRM, bản đã tải trong _claude_feasibility/external/mdrm), và tỷ lệ có số liệu theo năm trong dữ liệu của nhóm.
Không gõ tay tên mục: nếu mã không có trong MDRM, cột mdrm_check ghi NOT_FOUND."""
import os
import pandas as pd
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
MDRM = f"{ROOT}/_claude_feasibility/external/mdrm/MDRM_CSV.csv"
P1 = f"{ROOT}/_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet"
AG = f"{ROOT}/_claude_feasibility/out/07_ffiec_ag_bank_year.parquet"
OT = f"{ROOT}/_claude_feasibility/out/09_ffiec_other_bank_year.parquet"
HERE = os.path.dirname(os.path.abspath(__file__))

# (biến v3, vai trò, mã MDRM, file nguồn, cột nguồn, ghi chú thay đổi định nghĩa / cảnh báo)
ROWS = [
 ("nco_tot", "C1: charge-off tổng (tử số NCO)", "RIAD4635", "P1", "chargeoffs_ytd_kusd", "RI-B Phần I mục 9 cột A; số YTD, Q4 = cả năm"),
 ("nco_tot", "C1: thu hồi tổng (trừ khỏi charge-off)", "RIAD4605", "P1", "recoveries_ytd_kusd", "RI-B Phần I mục 9 cột B; YTD"),
 ("allow", "C2: dự phòng tín dụng (stock)", "RCON3123", "P1", "allowance_legacy_kusd", "RC mục 4.c. Sau khi áp dụng CECL (ASU 2016-13; NH cộng đồng đa số từ 2023) cùng mã nhưng là allowance for credit losses: gãy cấu trúc [I]. RCFD3123 khi thiếu RCON"),
 ("cecl_first", "C2: xác định năm áp dụng CECL", "RCONJJ30", "P1", "allowance_cecl_kusd", "CẢNH BÁO [F]: JJ30 là dự phòng cho tài sản PCD, KHÔNG phải tổng dự phòng CECL; 2023 chỉ 59,5% NH có số (98,6% bằng 0). Dùng 'năm đầu có JJ30' làm năm áp dụng CECL (như v2) sẽ bỏ sót NH áp dụng sớm không báo JJ30 [I]"),
 ("pdna_fl", "C3: nợ bảo đảm bằng đất NN quá hạn 30–89 ngày", "RCON3493", "AG", "farmland_pd30_89", "RC-N; báo cáo gần như đủ (97% dòng)"),
 ("pdna_fl", "C3: nợ bảo đảm bằng đất NN nonaccrual", "RCON3495", "AG", "farmland_nonaccrual", "RC-N"),
 ("(phụ)", "Nợ bảo đảm bằng đất NN quá hạn ≥ 90 ngày", "RCON3494", "AG", "farmland_pd90", "RC-N; không thuộc C3 theo khung (30–89 + nonaccrual)"),
 ("pdna_fp", "C3 bản Thịnh: vay sản xuất NN quá hạn 30–89 ngày", "RCON1594", "AG", "farm_pd30_89", "CẢNH BÁO [F]: chỉ 52–74% dòng có số, và tỷ lệ tăng theo FarmShare (41% ở FS≤5%, 95% ở FS>25%). Nghi do ngưỡng báo cáo theo tỷ trọng vay NN [?: chưa đọc hướng dẫn FFIEC]"),
 ("pdna_fp", "C3 bản Thịnh: vay sản xuất NN nonaccrual", "RCON1583", "AG", "farm_nonaccrual", "Như RCON1594"),
 ("(phụ)", "Vay sản xuất NN quá hạn ≥ 90 ngày", "RCON1597", "AG", "farm_pd90", "Như RCON1594"),
 ("nco_fl", "Phụ: charge-off nợ bảo đảm bằng đất NN", "RIAD3584", "AG", "farmland_chargeoff", "RI-B; YTD"),
 ("nco_fl", "Phụ: thu hồi nợ bảo đảm bằng đất NN", "RIAD3585", "AG", "farmland_recovery", "RI-B; YTD"),
 ("nco_fp", "Phụ: charge-off vay sản xuất NN", "RIAD4655", "AG", "farm_chargeoff", "Thiếu theo FarmShare như RCON1594"),
 ("nco_fp", "Phụ: thu hồi vay sản xuất NN", "RIAD4665", "AG", "farm_recovery", "Như RIAD4655"),
 ("ag_loans", "C5 và mẫu số: dư nợ bảo đảm bằng đất NN", "RCON1420", "P1", "farmland_loans_kusd", "RC-C Phần I mục 1.b"),
 ("ag_loans", "C5 và mẫu số: dư nợ vay sản xuất NN", "RCON1590", "P1", "ag_production_loans_kusd", "RC-C Phần I mục 3; RCFD1590 khi thiếu RCON"),
 ("L", "Mẫu số chung: tổng dư nợ", "RCON2122", "P1", "total_loans_kusd", "RC mục 4.a/RC-C mục 12"),
 ("liq", "C4: tiền mặt và tiền gửi", "RCON0081", "P1", "cash_and_due_kusd", "liquidity_ratio = (0081+0071 + B987+B989 + HTM + 1773)/2170; đã kiểm đồng nhất thức trên P1 (sai khác 0) [F]"),
 ("liq", "C4: tiền gửi có hưởng lãi", "RCON0071", "P1", "cash_and_due_kusd", ""),
 ("liq", "C4: bán vốn liên ngân hàng", "RCONB987", "P1", "fed_funds_sold_kusd", ""),
 ("liq", "C4: hợp đồng mua lại đảo ngược", "RCONB989", "P1", "fed_funds_sold_kusd", ""),
 ("liq", "C4: chứng khoán giữ đến đáo hạn (trước CECL)", "RCON1754", "P1", "htm_securities_kusd", "Sau CECL chuyển sang RCONJJ34 [F theo cột source]: định nghĩa HTM đổi (ròng dự phòng) [I]"),
 ("liq", "C4: chứng khoán giữ đến đáo hạn (sau CECL)", "RCONJJ34", "P1", "htm_securities_kusd", ""),
 ("liq", "C4: chứng khoán sẵn sàng để bán", "RCON1773", "P1", "afs_securities_kusd", ""),
 ("liq", "C4: tổng tài sản", "RCON2170", "P1", "total_assets_kusd", ""),
 ("(TDR)", "TDR/loan modification đất NN, quá hạn 30–89", "RCONK130", "OT", "farmland_tdr_pd30", "Từ 2023 (ASU 2022-02) mục đổi thành 'loan modifications to borrowers experiencing financial difficulty': gãy định nghĩa [I]. Đề xuất không dùng TDR trong v3"),
 ("(TDR)", "TDR/loan modification vay sản xuất NN, quá hạn 30–89", "RCONK138", "OT", "farm_prod_tdr_pd30", "Như RCONK130"),
]

m = pd.read_csv(MDRM, skiprows=1, dtype=str, low_memory=False)
m["code"] = m["Mnemonic"].str.strip() + m["Item Code"].str.strip()
src = {"P1": pd.read_parquet(P1, columns=["year"] + sorted({r[4] for r in ROWS if r[3] == "P1"})),
       "AG": pd.read_parquet(AG), "OT": pd.read_parquet(OT)}
out = []
for var, role, code, f, col, note in ROWS:
    r = m[(m.code == code) & m["End Date"].str.contains("9999", na=False)]
    forms = "; ".join(f"{x['Reporting Form']} {x['Start Date'].strip()[:10]}→nay" for _, x in r.iterrows() if str(x["Reporting Form"]).startswith("FFIEC 0"))
    d = src[f]
    cov = d.groupby("year")[col].apply(lambda s: s.notna().mean()) if col in d else pd.Series(dtype=float)
    out.append(dict(v3_var=var, role=role, mdrm=code, mdrm_item_name=(r["Item Name"].iloc[0].strip() if len(r) else "NOT_FOUND"),
                    mdrm_forms_valid=forms or ("NOT_FOUND" if not len(r) else "chỉ ngoài FFIEC 031/041/051"),
                    mdrm_check="OK" if len(r) else "NOT_FOUND", source_file={"P1": "phase1_community_all_observations_2005_2025-2.parquet",
                    "AG": "07_ffiec_ag_bank_year.parquet", "OT": "09_ffiec_other_bank_year.parquet"}[f], source_col=col,
                    years_with_data=(f"{int(cov[cov > 0].index.min())}–{int(cov[cov > 0].index.max())}" if (cov > 0).any() else "không có"),
                    coverage_min=round(float(cov[cov > 0].min()), 3) if (cov > 0).any() else 0.0,
                    coverage_max=round(float(cov.max()), 3) if len(cov) else 0.0, definition_note=note))
o = pd.DataFrame(out)
o.to_csv(f"{HERE}/codebook_v3.csv", index=False)
print(o[["mdrm", "mdrm_check", "years_with_data", "coverage_min", "coverage_max"]].to_string(index=False))
