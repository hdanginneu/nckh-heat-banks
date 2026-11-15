"""Ghi SHA-256 của PAP_E41.md và code E41 vào hashes_frozen_e41.json (đóng băng nội bộ trước khi chạy outcome thật)."""
import os, json, hashlib, datetime
D = os.path.dirname(os.path.abspath(__file__))
F = ["PAP_E41.md", "run_e41.py", "e41_common.py", "01_extract_cr.py", "03_sod_weights.py", "04_build_panel_ext.py"]
H = {f: hashlib.sha256(open(f"{D}/{f}", "rb").read()).hexdigest() for f in F}
json.dump(H, open(f"{D}/hashes_frozen_e41.json", "w"), indent=1)
open(f"{D}/FROZEN_AT_E41.txt", "w").write(datetime.datetime.now(datetime.timezone.utc).isoformat() + "\n")
print(json.dumps(H, indent=1))
