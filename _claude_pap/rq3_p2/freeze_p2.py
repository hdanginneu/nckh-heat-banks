"""freeze_p2.py — đóng băng PAP giai đoạn 2: ghi SHA-256 của văn bản, code, ngưỡng Δ và dữ liệu đầu vào mới.
Chạy MỘT lần sau khi nhóm duyệt PAP_P2.md. Sau đó đăng PAP_P2.md + hashes_frozen_p2.json lên OSF và dán link vào osf_registration.txt."""
import os, json, hashlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.expanduser("~/mnt/NCKH - NEU")
FILES = ["PAP_P2.md", "run_p2.py", "sesoi_p2.json"]
DATA = [f"{ROOT}/_claude_feasibility/out/12_ffiec_ri_rce_bank_year.parquet",
        f"{ROOT}/_claude_feasibility/12_ffiec_ri_rce_extract.py"]

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

out = f"{HERE}/hashes_frozen_p2.json"
assert not os.path.exists(out), "Đã đóng băng rồi; không ghi đè."
H = {f: sha(f"{HERE}/{f}") for f in FILES}
H.update({p: sha(p) for p in DATA})
json.dump(H, open(out, "w"), indent=1)
open(f"{HERE}/FROZEN_AT_P2.txt", "w").write(datetime.datetime.now().astimezone().isoformat() + "\n")
print(json.dumps(H, indent=1))
