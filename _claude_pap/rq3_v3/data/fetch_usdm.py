"""fetch_usdm.py — tải thống kê US Drought Monitor theo hạt (kiểu cộng dồn: cột D2 = % diện tích hạt ở D2 trở lên).
Nguồn: USDM Data Services, CountyStatistics/GetDroughtSeverityStatisticsByAreaPercent, statisticsType=1.
Mỗi file thô = một bang × một năm, các tuần có MapDate từ 25/3 đến 5/10 (lọc mùa 4–9 làm ở build_drought.py).
Đầu ra: ~/mnt/NCKH - NEU/data_external/usdm/raw/{BANG}_{NĂM}.csv. Chạy lại an toàn: bỏ qua file đã có.
Lệnh: python3 fetch_usdm.py [số_luồng] [ngân_sách_giây]"""
import os, sys, time, subprocess
from concurrent.futures import ThreadPoolExecutor
OUT = os.path.expanduser("~/mnt/NCKH - NEU/data_external/usdm/raw")
STATES = ("AL AZ AR CA CO CT DE DC FL GA ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD "
          "TN TX UT VT VA WA WV WI WY").split()
YEARS = range(2005, 2026)
URL = ("https://usdmdataservices.unl.edu/api/CountyStatistics/GetDroughtSeverityStatisticsByAreaPercent"
       "?aoi={s}&startdate=3/25/{y}&enddate=10/5/{y}&statisticsType=1")

def get(job):
    s, y = job; f = f"{OUT}/{s}_{y}.csv"
    if os.path.exists(f): return "skip"
    r = subprocess.run(["curl", "-sS", "-m", "90", "-H", "Accept: text/csv", URL.format(s=s, y=y)], capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    if r.returncode != 0 or not txt.startswith("MapDate"): return f"FAIL {s} {y}"
    open(f + ".tmp", "w").write(txt); os.replace(f + ".tmp", f); return "ok"

if __name__ == "__main__":
    nt = int(sys.argv[1]) if len(sys.argv) > 1 else 8; budget = float(sys.argv[2]) if len(sys.argv) > 2 else 160
    jobs = [(s, y) for s in STATES for y in YEARS if not os.path.exists(f"{OUT}/{s}_{y}.csv")]
    t0 = time.time(); res = []
    with ThreadPoolExecutor(nt) as ex:
        futs = []
        for j in jobs:
            futs.append(ex.submit(lambda j=j: get(j) if time.time() - t0 < budget else "later"))
        res = [f.result() for f in futs]
    left = sum(1 for s in STATES for y in YEARS if not os.path.exists(f"{OUT}/{s}_{y}.csv"))
    print({k: res.count(k) for k in set(res) if not k.startswith("FAIL")}, [r for r in res if r.startswith("FAIL")][:10], "còn thiếu:", left)
