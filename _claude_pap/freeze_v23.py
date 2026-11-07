import hashlib, json, os, datetime, sys
B = os.path.dirname(os.path.abspath(__file__)); O = f"{B}/hashes_frozen_v23.json"; F = ["PAP_v2.3.md", "rq3_v23/_v23.py"]
h = lambda p: hashlib.sha256(open(f"{B}/{p}", "rb").read()).hexdigest()
if "--verify" in sys.argv: d = json.load(open(O)); print([p for p, v in d["files"].items() if h(p) != v] or "khớp toàn bộ"); sys.exit()
if os.path.exists(O): sys.exit("đã đóng băng")
json.dump({"frozen_at": datetime.datetime.now().isoformat(timespec="seconds"), "files": {p: h(p) for p in F}}, open(O, "w"), indent=1); print("đã đóng băng")
