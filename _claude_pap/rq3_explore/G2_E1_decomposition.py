import sys, os
S=os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"); sys.path.insert(0,S); os.chdir(S)
import _pap_est as E
from _pap_est import *
assert not E.FAKE
c=load_county()
bc=c["base_crop_kusd"].where(c["base_crop_kusd"]>0)*1000.0
c["rev_ratio"]=(c["crop_kusd"]*1000.0/bc)                       # doanh thu / baseline (mức, không log)
c["rev_dev"]=c["rev_ratio"]-1.0                                  # lệch so với baseline
c["y_indem_drought"]=((c["indem_hd_main"]-c["indem_heat_only"])/bc).where(c["has_col"].astype(bool) if c["has_col"].dtype!=object else c["has_col"].notna())
# mẫu E (có bản ghi RMA) — giống E1
sE=county_frame(c,"y_indem_hd").dropna(subset=["heat_lead1"])  # chỉ để lấy cấu trúc; mẫu thật lấy theo y_indem_hd có giá trị
rows=[]
def go(y,tag,sample_col="y_indem_hd"):
    s=county_frame(c,y)
    s=s[s[sample_col].notna()]            # cùng mẫu với E1
    r=fit_lp(s,y,["heat"]+RAIN,["fips","div_year"],se="conley",cty="fips")
    d=dict(outcome=y,tag=tag,n=r["n"],beta=float(r["beta"][0]),se=float(r["se"][0]),lo=float(r["ci95"][0][0]),hi=float(r["ci95"][1][0]),sd_y=r["sd_y"])
    rows.append(d); print(d,flush=True)
go("y_lncrop","A trên mẫu E (hạt có bản ghi RMA)")
go("rev_dev","doanh thu/baseline − 1 (mức), mẫu E")
go("y_indem_hd","E1 (Drought+Heat+HotWind)")
go("y_indem_heat","E2 (Heat+HotWind)")
go("y_indem_drought","Drought thuần (cause 11)")
go("y_indem_total","Tổng bồi thường mọi nguyên nhân")
pd.DataFrame(rows).to_csv("/tmp/g1/g2.csv",index=False)
