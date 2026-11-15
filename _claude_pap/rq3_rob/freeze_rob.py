"""Ghi SHA-256 của file quy tắc và run_rob.py vào hashes_frozen_rob.json (đóng băng nội bộ trước khi chạy dữ liệu thật)."""
import os, json, hashlib, datetime
D = os.path.dirname(os.path.abspath(__file__))
F = ["RULES_R1_R7.md", "RULES_R8_R12.md", "run_rob.py"]
H = {f: hashlib.sha256(open(f"{D}/{f}", "rb").read()).hexdigest() for f in F}
json.dump(H, open(f"{D}/hashes_frozen_rob.json", "w"), indent=1)
open(f"{D}/FROZEN_AT_ROB.txt", "w").write(datetime.datetime.now(datetime.timezone.utc).isoformat() + "\n")
print(json.dumps(H, indent=1))
