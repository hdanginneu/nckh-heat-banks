"""Kiểm các file đã đóng băng trong hashes_frozen_*.json chưa bị sửa."""
import glob, hashlib, json, os
here = os.path.dirname(os.path.abspath(__file__)); pap = os.path.join(here, "_claude_pap")
root = os.path.expanduser("~/mnt/NCKH - NEU")
ok = {}  # file -> True nếu khớp ít nhất một bản hash (bản sửa có hash riêng, vd hashes_v22_fix1.json)
for hf in sorted(glob.glob(os.path.join(pap, "hashes*.json"))):
    d = json.load(open(hf)); files = d.get("files", d)
    for k, v in files.items():
        if not isinstance(v, str) or len(v) != 64: continue
        cand = [os.path.join(pap, k), os.path.join(here, k), os.path.join(root, k)]
        f = next((c for c in cand if os.path.isfile(c)), None)
        if f is None: ok.setdefault(k, None); continue
        m = hashlib.sha256(open(f, "rb").read()).hexdigest() == v
        ok[k] = bool(ok.get(k)) or m
bad = [k for k, v in ok.items() if v is False]; miss = [k for k, v in ok.items() if v is None]
for k in miss: print("không thấy", k)
for k in bad: print("SAI", k)
print(f"Đã kiểm {len(ok)} file, sai {len(bad)}, thiếu {len(miss)}")
