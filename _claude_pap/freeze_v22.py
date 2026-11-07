import hashlib, json, os, datetime, sys
B = os.path.dirname(os.path.abspath(__file__)); O = f"{B}/hashes_frozen_v22.json"
F = ["PAP_v2.2.md", "rq3_v22/run_v22.py"]
h = lambda p: hashlib.sha256(open(f"{B}/{p}", "rb").read()).hexdigest()
if "--verify" in sys.argv:
    d = json.load(open(O)); bad = [p for p, v in d["files"].items() if h(p) != v]; print("khớp toàn bộ" if not bad else bad); sys.exit(0)
if os.path.exists(O): sys.exit("đã đóng băng")
json.dump({"frozen_at": datetime.datetime.now().isoformat(timespec="seconds"), "files": {p: h(p) for p in F}}, open(O, "w"), indent=1); print("đã đóng băng")
