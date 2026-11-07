"""freeze_v21.py — đóng băng PAP v2.1: sha256 của PAP_v2.1.md, rq3_v21/*.py và các file v2 được import. --verify để so khớp."""
import hashlib, json, sys, os, glob, datetime
BASE = os.path.dirname(os.path.abspath(__file__)); OUTJ = f"{BASE}/hashes_frozen_v21.json"
def files(): return [f"{BASE}/PAP_v2.1.md"] + sorted(glob.glob(f"{BASE}/rq3_v21/*.py")) + sorted(glob.glob(f"{BASE}/rq3_v2/_v2_*.py")) + [f"{BASE}/scripts/_pap_est.py", f"{BASE}/scripts/_pap_common.py"]
def h(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
if "--verify" in sys.argv:
    old = json.load(open(OUTJ)); bad = [p for p, v in old["files"].items() if not os.path.exists(f"{BASE}/{p}") or h(f"{BASE}/{p}") != v]
    print("khớp toàn bộ" if not bad else f"KHÁC: {bad}"); sys.exit(1 if bad else 0)
if os.path.exists(OUTJ): sys.exit("đã đóng băng")
d = {"frozen_at": datetime.datetime.now().isoformat(timespec="seconds"), "files": {os.path.relpath(p, BASE): h(p) for p in files()}}
json.dump(d, open(OUTJ, "w"), indent=1); print("đã đóng băng", d["frozen_at"], len(d["files"]), "file")
