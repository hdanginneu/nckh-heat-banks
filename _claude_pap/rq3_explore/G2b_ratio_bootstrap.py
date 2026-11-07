import sys, os
S=os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"); sys.path.insert(0,S); os.chdir(S)
import _pap_est as E
from _pap_est import *
c=load_county()
bc=c["base_crop_kusd"].where(c["base_crop_kusd"]>0)*1000.0
c["rev_dev"]=c["crop_kusd"]*1000.0/bc-1.0
s=county_frame(c,"y_indem_hd"); s=s[s["y_indem_hd"].notna()&s["rev_dev"].notna()&s["y_indem_heat"].notna()].copy()
X=["heat"]+RAIN
ff={y:FastFE(s,y,X,"fips","div_year","state") for y in ("rev_dev","y_indem_hd","y_indem_heat")}
b0={y:float(f.fit()[0]) for y,f in ff.items()}
print("điểm:",b0,"n",ff["rev_dev"].n)
f0=ff["rev_dev"]; G=f0.C
rng=np.random.default_rng(20261105); B=500
draws=rng.multinomial(G,np.full(G,1.0/G),size=B)
R1,R2,Rv,Ri=[],[],[],[]
for i in range(B):
    w=draws[i][f0.c].astype(float)
    if w.sum()==0: continue
    bv={y:float(f.fit(w)[0]) for y,f in ff.items()}
    Rv.append(bv["rev_dev"]); Ri.append(bv["y_indem_hd"])
    R1.append(bv["y_indem_hd"]/abs(bv["rev_dev"])); R2.append(bv["y_indem_heat"]/abs(bv["rev_dev"]))
q=lambda a:np.percentile(a,[2.5,50,97.5]).round(3)
print("B =",len(R1),"số bang (cụm) =",G)
print("tỷ lệ E1/|mất doanh thu|: điểm %.3f ; boot [2.5,50,97.5]="%(b0['y_indem_hd']/abs(b0['rev_dev'])),q(R1))
print("tỷ lệ E2/|mất doanh thu| (mã nhiệt thuần): điểm %.3f ; boot="%(b0['y_indem_heat']/abs(b0['rev_dev'])),q(R2))
print("β doanh thu mức (boot):",q(Rv)," β E1 (boot):",q(Ri))
print("P(tỷ lệ E1 > 1) = %.3f ; P(tỷ lệ E1 > 0.5) = %.3f"%(np.mean(np.array(R1)>1),np.mean(np.array(R1)>0.5)))
