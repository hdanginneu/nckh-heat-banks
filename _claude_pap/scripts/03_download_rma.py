"""03_download_rma.py — tải USDA RMA Cause of Loss (colsom_YYYY) và Summary of Business
State/County/Crop (sobcov_YYYY), 2001-2022, về ~/Projects/nckh_data/external/rma/.
Ghi nhật ký từng file: thời điểm, URL, kích thước, SHA-256. Chạy lại được (bỏ qua file đã có trong log).

Nguồn: www.rma.usda.gov/sites/default/files/information-tools/ (bản sao chính thức của RMA;
máy này không phân giải được pubfs-rma.fpac.usda.gov - xem DECISIONS_LOG).
"""
import csv, datetime as dt, hashlib, os, subprocess, sys

BASE = "https://www.rma.usda.gov/sites/default/files/information-tools"
OUT = os.path.expanduser("~/Projects/nckh_data/external/rma")
LOG = os.path.join(OUT, "download_log.csv")
YEARS = range(2001, 2023)
PREFIX = ["colsom", "sobcov"]
LIMIT_BYTES = 5 * 1024**3


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    done = set()
    if os.path.exists(LOG):
        with open(LOG, newline="") as f:
            done = {r["url"] for r in csv.DictReader(f)}
    new = not os.path.exists(LOG)
    total = 0
    with open(LOG, "a", newline="") as lf:
        w = csv.writer(lf)
        if new:
            w.writerow(["time_utc", "url", "file", "bytes", "sha256", "last_modified", "content_type"])
        for p in PREFIX:
            for y in YEARS:
                url = f"{BASE}/{p}_{y}.zip"
                fn = os.path.join(OUT, f"{p}_{y}.zip")
                if url in done and os.path.exists(fn):
                    total += os.path.getsize(fn)
                    continue
                hdr = subprocess.run(["curl", "-sS", "-m", "60", "-L", "-I", url], capture_output=True, text=True, check=True).stdout
                hl = {k.strip().lower(): v.strip() for k, _, v in (l.partition(":") for l in hdr.splitlines()) if v}
                ct, lm = hl.get("content-type", ""), hl.get("last-modified", "")
                if "zip" not in ct:
                    sys.exit(f"Không phải zip: {url} ({ct})")
                subprocess.run(["curl", "-sS", "-m", "600", "-L", "-o", fn + ".part", url], check=True)
                os.replace(fn + ".part", fn)
                size = os.path.getsize(fn)
                total += size
                if total > LIMIT_BYTES:
                    sys.exit("Vượt 5 GB - dừng và hỏi Hdang")
                w.writerow([dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), url, fn, size, sha256(fn), lm, ct])
                lf.flush()
                print(url, size, flush=True)
    print("TOTAL bytes", total)


if __name__ == "__main__":
    main()
