"""size_p2.py — tỷ lệ bác bỏ sai của họ {P1, P2, P3} trên các bộ dữ liệu giả (results_fake_s*/p2_results.csv)."""
import glob, os
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
for f in sorted(glob.glob(f"{HERE}/results_fake_s*/p2_results.csv")):
    d = pd.read_csv(f); d["seed"] = f.split("results_fake_s")[1].split("/")[0]; rows.append(d)
D = pd.concat(rows)
F = D[D.fam == True]                                             # noqa: E712
print("số bộ giả:", F.seed.nunique())
print("tỷ lệ p_RI < 0,05:", round((F.p_RI < .05).mean(), 3), " | tỷ lệ p_WY < 0,05:", round((F.p_WY < .05).mean(), 3))
print("ít nhất một bác bỏ trong họ (FWER):", round(F.groupby("seed").p_WY.min().lt(.05).mean(), 3))
print(F.groupby("name").agg(rej=("p_RI", lambda s: (s < .05).mean()), eq=("tost", "mean"), sdp=("sd_perm", "mean")).round(3).to_string())
