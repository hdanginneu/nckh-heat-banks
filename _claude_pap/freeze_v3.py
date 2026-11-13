"""freeze_v3.py — đóng băng PAP v3: hash của PAP, code và dữ liệu đầu vào (chạy MỘT lần, từ thư mục _claude_pap).
  python3 freeze_v3.py            → ghi hashes_frozen_v3.json (từ chối nếu đã có)
  python3 freeze_v3.py --verify   → kiểm mọi file vẫn khớp hash"""
import hashlib, json, os, datetime, sys
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
O = f"{B}/hashes_frozen_v3.json"
FILES = ["PAP_v3.md", "rq3_v3/_v3_spec.py", "rq3_v3/run_v3.py", "rq3_v3/build_v3.py", "rq3_v3/sesoi_v3.py", "rq3_v3/sesoi_v3.json",
         "rq3_v3/data/build_drought.py", "rq3_v3/data/fetch_usdm.py", "rq3_v3/data/make_codebook.py", "rq3_v3/data/codebook_v3.csv"]
DATA = ["_claude_pap/rq3_v3/out/panel_v3.parquet", "data_external/usdm/county_year_drought.parquet"]


def h(p):
    s = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): s.update(chunk)
    return s.hexdigest()


if "--verify" in sys.argv:
    d = json.load(open(O))
    bad = [p for p, v in d["files"].items() if h(f"{B}/{p}") != v] + [p for p, v in d["data"].items() if h(f"{ROOT}/{p}") != v]
    print(bad or "khớp toàn bộ"); sys.exit(1 if bad else 0)
if os.path.exists(O): sys.exit("đã đóng băng — không ghi lại")
miss = [p for p in FILES if not os.path.isfile(f"{B}/{p}")] + [p for p in DATA if not os.path.isfile(f"{ROOT}/{p}")]
if miss: sys.exit(f"thiếu file, chưa đóng băng: {miss}")
json.dump({"frozen_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "files": {p: h(f"{B}/{p}") for p in FILES}, "data": {p: h(f"{ROOT}/{p}") for p in DATA}}, open(O, "w"), indent=1)
print("đã đóng băng:", O)
