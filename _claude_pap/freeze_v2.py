"""freeze_v2.py — đóng băng PAP v2: băm sha256 của PAP_v2.md và mọi *.py trong rq3_v2/ (cùng _pap_est/_pap_common của v1 để chắc chắn không đổi).
python3 freeze_v2.py           # tạo hashes_frozen_v2.json (từ chối nếu đã tồn tại)
python3 freeze_v2.py --verify  # so khớp"""
import hashlib, json, sys, os, glob, datetime
BASE = os.path.dirname(os.path.abspath(__file__))
def files():
    fs = [f"{BASE}/PAP_v2.md"] + sorted(glob.glob(f"{BASE}/rq3_v2/*.py")) + [f"{BASE}/scripts/_pap_est.py", f"{BASE}/scripts/_pap_common.py"]
    return fs
def h(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
OUTJ = f"{BASE}/hashes_frozen_v2.json"
if "--verify" in sys.argv:
    old = json.load(open(OUTJ)); bad = 0
    for p, v in old["files"].items():
        cur = h(f"{BASE}/{p}") if os.path.exists(f"{BASE}/{p}") else None
        ok = cur == v; bad += (not ok); print(("OK   " if ok else "ĐỔI  "), p)
    print("khớp toàn bộ" if bad == 0 else f"{bad} file khác bản đóng băng"); sys.exit(0 if bad == 0 else 1)
if os.path.exists(OUTJ): sys.exit("hashes_frozen_v2.json đã tồn tại — không đóng băng lại.")
d = {"frozen_at": datetime.datetime.now().isoformat(timespec="seconds"), "files": {os.path.relpath(p, BASE): h(p) for p in files()}}
json.dump(d, open(OUTJ, "w"), indent=1, ensure_ascii=False); print("đã đóng băng", d["frozen_at"]); [print(" ", k, v[:12]) for k, v in d["files"].items()]
