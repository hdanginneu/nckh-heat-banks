"""61_check_report_numbers.py — đối chiếu MỌI con số trong RESULTS_REPORT.md với các file kết quả (CSV/JSON trong out/results, out/*.csv, specs_run.csv).
Mỗi số trong báo cáo phải khớp (sai số làm tròn theo số chữ số thập phân của chính số đó, cũng thử ×100 cho phần trăm) với một giá trị trong kết quả.
Bỏ qua: năm 1900–2100, số nguyên < 100 không có phần thập phân (số thứ tự mục, h, số họ), ngày tháng. Ghi các số không khớp vào out/report_number_check.csv.
"""
import json, re, sys
import numpy as np
import pandas as pd
from _pap_common import *

rep = (PAP / "RESULTS_REPORT.md").read_text(encoding="utf-8")
vals = []
def add_df(df):
    for c in df.columns:
        x = pd.to_numeric(df[c], errors="coerce").dropna().to_numpy(float)
        vals.append(x)
for p in list((PAP / "out" / "results").rglob("*.csv")) + list((PAP / "out").glob("*.csv")) + [PAP / "specs_run.csv"]:
    try: add_df(pd.read_csv(p))
    except Exception: pass
for p in list((PAP / "out" / "results").glob("*.json")) + list((PAP / "out").glob("*.json")):
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
        elif isinstance(o, (int, float)) and not isinstance(o, bool): vals.append(np.array([float(o)]))
    walk(json.load(open(p)))
# số trong specs_run.extra_json
try:
    for s in pd.read_csv(PAP / "specs_run.csv").extra_json.dropna():
        for k, v in json.loads(s).items():
            if isinstance(v, (int, float)) and not isinstance(v, bool): vals.append(np.array([float(v)]))
except Exception: pass
V = np.sort(np.concatenate(vals)); V = V[np.isfinite(V)]
V = np.unique(np.concatenate([V, V * 100, np.abs(V), np.abs(V) * 100, V / 1000, V * 1000]))

bad = []
for m in re.finditer(r"(?<![\w.])-?\d+(?:[.,]\d+)*(?![\w])", rep):
    tok = m.group(0)
    t = tok.replace("−", "-")
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", t): t = t.replace(".", "")          # dấu chấm ngăn nghìn
    t = t.replace(",", ".")
    try: x = float(t)
    except ValueError: continue
    dec = len(t.split(".")[1]) if "." in t else 0
    if dec == 0 and (abs(x) < 100 or 1900 <= abs(x) <= 2100): continue
    tol = 0.5 * 10 ** (-dec) + 1e-9
    i = np.searchsorted(V, x - tol); ok = i < len(V) and V[i] <= x + tol
    if not ok:
        ctx = rep[max(0, m.start() - 50): m.end() + 30].replace("\n", " ")
        bad.append(dict(số=tok, ngữ_cảnh=ctx))
pd.DataFrame(bad).to_csv(PAP / "out" / "report_number_check.csv", index=False)
print(f"{len(bad)} số không khớp" if bad else "Mọi số trong báo cáo khớp với file kết quả")
log_run(f"61_check_report_numbers: {len(bad)} số không khớp.")
