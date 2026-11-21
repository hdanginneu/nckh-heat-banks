"""Ghi SHA-256 của RULES_B1_B4.md và run_b.py vào hashes_frozen_b.json (đóng băng nội bộ trước khi chạy dữ liệu thật)."""
import os, json, hashlib, datetime
D = os.path.dirname(os.path.abspath(__file__))
H = {f: hashlib.sha256(open(f"{D}/{f}", "rb").read()).hexdigest() for f in ["RULES_B1_B4.md", "run_b.py"]}
H["frozen_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(H, open(f"{D}/hashes_frozen_b.json", "w"), indent=1); print(json.dumps(H, indent=1))
