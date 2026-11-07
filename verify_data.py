"""Kiểm dữ liệu đầu vào khớp MANIFEST.sha256 (chạy sau setup_paths.sh)."""
import hashlib, os, sys
root = os.path.expanduser("~/mnt/NCKH - NEU")
man = sys.argv[1]  # đường dẫn tới data_inputs/MANIFEST.sha256
bad = 0
for line in open(man):
    h, p = line.split(maxsplit=1); p = p.strip().lstrip("./")
    f = os.path.join(root, p)
    try:
        got = hashlib.sha256(open(f, "rb").read()).hexdigest()
    except FileNotFoundError:
        print("THIẾU", p); bad += 1; continue
    if got != h: print("SAI HASH", p); bad += 1
print("Lỗi:", bad); sys.exit(1 if bad else 0)
