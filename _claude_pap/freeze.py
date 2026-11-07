"""freeze.py — đóng băng nội bộ: SHA-256 của kế hoạch và mọi script giai đoạn 2; ghi hashes_frozen.json, FREEZE_NOTE.md và DECISIONS_LOG.md.
Chạy một lần. Kiểm tra sau này: python3 freeze.py --verify
"""
import datetime as dt, hashlib, json, sys
from pathlib import Path
PAP = Path(__file__).resolve().parent; ROOT = PAP.parent
files = [ROOT / "_claude_eda" / "PRE_ANALYSIS_PLAN_v1.md", ROOT / "_claude_eda" / "PRE_ANALYSIS_PLAN_v1.docx"] + sorted((PAP / "scripts").glob("*.py"))
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
cur = {str(p.relative_to(ROOT)): h(p) for p in files}
store = PAP / "hashes_frozen.json"
if "--verify" in sys.argv:
    old = json.load(open(store))["files"]
    diff = {k: (old.get(k), cur.get(k)) for k in set(old) | set(cur) if old.get(k) != cur.get(k)}
    print("KHỚP với bản đóng băng" if not diff else f"LỆCH: {json.dumps(diff, indent=1)}"); sys.exit(0 if not diff else 1)
assert not store.exists(), "đã đóng băng rồi"
now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
json.dump({"frozen_at": now, "files": cur}, open(store, "w"), indent=1)
lines = [f"# FREEZE_NOTE — đóng băng nội bộ {now}", "", "Kế hoạch không đăng công khai. Từ mốc này không sửa kế hoạch hay code giai đoạn 2; mọi sửa ghi vào `DEVIATIONS.md`.", "", "| File | SHA-256 |", "|---|---|"]
lines += [f"| `{k}` | `{v}` |" for k, v in cur.items()]
(PAP / "FREEZE_NOTE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
with open(ROOT / "_claude_eda" / "DECISIONS_LOG.md", "a", encoding="utf-8") as f:
    f.write(f"\n## Mốc đóng băng nội bộ ({now})\nĐóng băng nội bộ ngày {now}; kế hoạch không đăng công khai. SHA-256 `PRE_ANALYSIS_PLAN_v1.md` = `{cur['_claude_eda/PRE_ANALYSIS_PLAN_v1.md']}`; `.docx` = `{cur['_claude_eda/PRE_ANALYSIS_PLAN_v1.docx']}`. Hash từng script ở `_claude_pap/FREEZE_NOTE.md` và `hashes_frozen.json` ({len(files) - 2} script). Tmin không chạy (quyết định 15/10).\n")
print("đã đóng băng", now, len(files), "file")
