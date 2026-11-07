"""T1 — (a) thời gian một lần fit; (b) placebo nhiệt năm t+1 (lead) cho spec chính. Không dùng hệ số nhiệt thật."""
from _v2_spec import *
b = pd.read_parquet(f"{V2}/out/panel_v2.parquet")
rows = []
for y, cond, tag in (("dALLOW_h0", True, "dALLOW|cond"), ("S_prov_cum_h0", True, "prov|cond"), ("dLIQ_h0", False, "dLIQ"),
                     ("dALLOW_h0", False, "dALLOW raw"), ("S_prov_cum_h0", False, "prov raw")):
    s = frame(b, y, cond, need_lead=True)
    for se in ("conley", "state"):
        t0 = time.time()
        r, xs = fit(s, y, "heat_lead1", cond, se=se)
        d = dict(outcome=tag, se=se, n=r["n"], banks=r["n_units"], sd_y=r["sd_y"], b2=r["beta"][0], se2=r["se"][0], t2=r["beta"][0] / r["se"][0],
                 b1=r["beta"][1], t1=r["beta"][1] / r["se"][1], secs=round(time.time() - t0, 1))
        rows.append(d); print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()}, flush=True)
pd.DataFrame(rows).to_csv(f"{V2}/out/T1_placebo_lead.csv", index=False)
