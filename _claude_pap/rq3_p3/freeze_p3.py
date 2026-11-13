"""freeze_p2.py — đóng băng PAP vòng cuối (P3): ghi SHA-256 của văn bản, code, ngưỡng Δ và dữ liệu đầu vào mới.
Chạy MỘT lần trước khi chạy dữ liệu thật (đóng băng nội bộ, không đăng bên ngoài)."""
import os, json, hashlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
FILES = ["PAP_P3.md", "run_p3.py", "../rq3_p2/run_p2.py", "../rq3_p2/sesoi_p2.json", "../rq3_v3/sesoi_v3.json"]
DATA = [f"{ROOT}/_claude_pap/out/rma_coverage_ratio.csv"]

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

out = f"{HERE}/hashes_frozen_p3.json"
assert not os.path.exists(out), "Đã đóng băng rồi; không ghi đè."
H = {f: sha(f"{HERE}/{f}") for f in FILES}
H.update({p.replace(ROOT, "ROOT:"): sha(p) for p in DATA})          # đường dẫn tương đối theo ROOT để chạy được trên mọi máy
json.dump(H, open(out, "w"), indent=1)
open(f"{HERE}/FROZEN_AT_P3.txt", "w").write(datetime.datetime.now().astimezone().isoformat() + "\n")
print(json.dumps(H, indent=1))
