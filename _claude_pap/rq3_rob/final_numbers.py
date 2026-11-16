"""final_numbers.py — quy đổi các kết quả ĐÃ CÓ sang cùng đơn vị cho bảng cận trên của bài (không ước lượng gì mới).
Nguồn: rq3_v3/results_real/v3_confirmatory.csv (C1–C3), rq3_p2/results_real/p2_results.csv (P1, P2), results_real/checks_d.json (E46),
rq3_v3/sesoi_v3.json (ȳ của nhóm FarmShare 15–35%), rq3_rob/results_real/rob_results.csv (R2). Mọi phép quy đổi giả định tuyến tính theo
FarmShare và theo nhiệt, như mục 4.1 của bài. Cận "bất lợi" = đầu CI90 theo hướng xấu cho ngân hàng (tổn thất, dự phòng muộn, quá hạn, lãi suất,
nợ xấu tăng). FS25 = nhân 2,5 (FarmShare 25% so với 0%). Đầu ra: results_real/final_numbers.csv và in bảng."""
import os, json
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
v3 = pd.read_csv(f"{H}/../rq3_v3/results_real/v3_confirmatory.csv").set_index("name")
p2 = pd.read_csv(f"{H}/../rq3_p2/results_real/p2_results.csv").set_index("name")
E = json.load(open(f"{H}/results_real/checks_d.json"))["E46"]
S = json.load(open(f"{H}/../rq3_v3/sesoi_v3.json"))
L2T = E["median_loans_to_assets"] / E["median_tier1_to_assets"]          # điểm % dư nợ → % vốn cấp 1 (trung vị nhóm FarmShare 15–35%)
SD_RESID = 0.21                                                          # SD nhiệt còn lại sau FE, đơn vị SD chung (checks_d D39)
rows = []
def add(k, label, src, unit, ybar=None, tier1=True):
    hi = float(src.loc[k, "ci90_hi"]); th = float(src.loc[k, "theta"])
    fs25 = 2.5 * hi
    rows.append(dict(stat=k, noi_dung=label, theta=th, can_tren_ci90=hi, can_tren_FS25=fs25, don_vi=unit,
                     pct_von_cap1=(fs25 * L2T if tier1 else None), so_voi_muc_nen=(fs25 / ybar if ybar else None),
                     can_tren_FS25_cu_soc_021SD=fs25 * SD_RESID))
add("C1", "Tổn thất ròng cộng dồn t..t+6", v3, "điểm % tổng dư nợ t−1", S["C1"]["ybar_ref"])
add("C2", "Dự phòng muộn trừ sớm", v3, "điểm % tổng dư nợ t−1", S["C2"]["ybar_ref"])
add("C3", "Quá hạn sớm nợ đất NN (TB h = 0, 1)", v3, "điểm % tổng dư nợ t−1", S["C3"]["ybar_ref"], tier1=False)
add("P1", "Lãi suất hiệu dụng vay sản xuất NN, t−1 → t+1", p2, "điểm % lãi suất (×100 = điểm cơ bản)", tier1=False)
add("P2", "Nợ xấu vay sản xuất NN sau đợt nóng hai năm", p2, "điểm % dư nợ vay sản xuất t−2", tier1=False)
O = pd.DataFrame(rows)
c1 = O.set_index("stat").loc["C1", "can_tren_FS25"]
note = {"C1_tren_so_no_NN_pct": c1 / 0.25,                               # nếu toàn bộ tổn thất đến từ sổ nông nghiệp (25% dư nợ)
        "doanh_thu_giam_cap_hat_pct": 11.7, "doanh_thu_giam_theo_mang_luoi_pct": 9.0,
        "ty_le_truyen_dan_toi_da": (c1 / 0.25) / 9.0, "loans_to_tier1": L2T}
O.to_csv(f"{H}/results_real/final_numbers.csv", index=False)
json.dump(note, open(f"{H}/results_real/final_numbers_note.json", "w"), indent=1)
pd.set_option("display.width", 250); print(O.round(4).to_string(index=False)); print(json.dumps(note, indent=1))
