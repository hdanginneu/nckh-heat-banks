"""run_all.py — chạy toàn bộ pipeline giai đoạn 2 bằng một lệnh.
  python3 run_all.py          → ước lượng THẬT (chỉ sau đóng băng)
  python3 run_all.py --fake   → kết cục hoán vị (kiểm tra code)
Thứ tự cố định theo kế hoạch mục 12. Dừng ngay nếu một bước lỗi.
"""
import os, subprocess, sys, time
fake = "--fake" in sys.argv
env = {**os.environ, "PAP_FAKE": "1" if fake else "0"}
STEPS = ["10_process_rma.py", "10_build_county_panel.py", "11_build_bank_panel.py", "20_family_A_B_E.py", "21_family_C_D.py", "22_pass_through.py",
         "23_H5.py", "24_failures.py", "30_robustness.py", "40_multiple_testing.py", "50_tables_figures.py"]
here = os.path.dirname(os.path.abspath(__file__))
for s in STEPS:
    t = time.time()
    r = subprocess.run([sys.executable, os.path.join(here, s)], cwd=here, env=env)
    print(f"{s}: {'OK' if r.returncode == 0 else 'LỖI'} ({time.time() - t:.0f}s)", flush=True)
    if r.returncode:
        sys.exit(r.returncode)
