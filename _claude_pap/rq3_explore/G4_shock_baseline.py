import sys, os
S=os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"); sys.path.insert(0,S); os.chdir(S)
from _pap_est import *
ROOT=os.path.expanduser("~/mnt/NCKH - NEU")
H=pd.read_parquet(f"{ROOT}/_claude_eda/out/tab/heat_county_year.parquet",columns=["county_fips","year","gdd_ex29"])
Hp=H.pivot(index="county_fips",columns="year",values="gdd_ex29").sort_index(axis=1)
yrs=list(range(2006,2026))
def base(kind):
    out={}
    for t in yrs:
        if kind=="fixed": cols=[y for y in Hp.columns if 1981<=y<=2005]
        elif kind=="roll10": cols=list(range(t-10,t))
        elif kind=="roll20": cols=list(range(t-20,t))
        elif kind=="expand": cols=list(range(1981,t))
        out[t]=Hp[cols].mean(axis=1)
    return pd.DataFrame(out)
W=pd.read_parquet(f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet",columns=["analysis_year","idrssd","county_fips","deposit_weight_l1"]).rename(columns={"analysis_year":"year"})
W=W[(W.deposit_weight_l1>0)&W.year.between(2006,2025)]
def agg(vals):   # vals: DataFrame county x year ; trả Σ w·vals theo (idrssd,year) nếu phủ ≥98%
    v=vals.stack().rename("v").reset_index(); v.columns=["county_fips","year","v"]
    m=W.merge(v,on=["county_fips","year"],how="left")
    m["wv"]=m.deposit_weight_l1*m.v; m["ok"]=m.deposit_weight_l1*m.v.notna()
    g=m.groupby(["idrssd","year"]).agg(wv=("wv","sum"),ok=("ok","sum"),w=("deposit_weight_l1","sum")).reset_index()
    g["val"]=np.where(g.ok>=0.98*g.w,g.wv,np.nan)
    return g.set_index(["idrssd","year"])["val"]
Hlev=Hp[yrs]
res={"gdd_rebuilt":agg(Hlev)}
for k in ("fixed","roll10","roll20","expand"):
    A=Hlev-base(k)
    res["S_"+k]=agg(A)
df=pd.DataFrame(res).reset_index()
bh=pd.read_parquet(f"{ROOT}/_claude_eda/out/tab/bank_year_heat.parquet",columns=["idrssd","year","gdd","gdd_anom","gdd_base"])
df["idrssd"]=df.idrssd.astype(bh.idrssd.dtype)
df=df.merge(bh,on=["idrssd","year"],how="inner")
bp=load_bank()[["idrssd","year","division","heat","hq_state"]]
bp["idrssd"]=bp.idrssd.astype(df.idrssd.dtype)
d=df.merge(bp,on=["idrssd","year"],how="inner")
d=d[d.year.between(2006,2023)].copy(); d["div_year"]=d.division+"_"+d.year.astype(str)
print("N bank-năm khớp:",len(d),"ngân hàng:",d.idrssd.nunique())
print("1) rebuilt gdd vs bank_year_heat.gdd: corr=%.4f  max|diff|=%.4f"%(d.gdd_rebuilt.corr(d.gdd),(d.gdd_rebuilt-d.gdd).abs().max()))
bsd=d.groupby("idrssd").gdd_base.nunique(); print("2) gdd_base cố định theo ngân hàng? số giá trị khác nhau theo ngân hàng: median",bsd.median(),"max",bsd.max())
# gdd_anom hiện có vs S_fixed nhất quán
x=d.dropna(subset=["gdd_anom","S_fixed"])
print("3) gdd_anom hiện có vs S_fixed(trọng số nhất quán): corr=%.4f ; sd(gdd_anom)=%.2f sd(S_fixed)=%.2f ; sd(hiệu)=%.2f"%(x.gdd_anom.corr(x.S_fixed),x.gdd_anom.std(),x.S_fixed.std(),(x.gdd_anom-x.S_fixed).std()))
# xu hướng
print("4) TB theo năm (gdd đơn vị thô):")
tr=d.groupby("year")[["gdd_rebuilt","S_fixed","S_roll10","S_roll20","S_expand"]].mean().round(1); print(tr.to_string())
from scipy import stats as st
for c in ["S_fixed","S_roll10","S_roll20","S_expand"]:
    r=st.linregress(tr.index,tr[c]); print("   xu hướng %s: %.2f /năm (p=%.3f)"%(c,r.slope,r.pvalue))
# phương sai sau FE bank + div×năm
cols=["gdd_rebuilt","S_fixed","S_roll10","S_roll20","S_expand"]
dd=d.dropna(subset=cols).copy()
gc=[codes(dd["idrssd"]),codes(dd["div_year"])]
Z=absorb(dd[cols].to_numpy(float),gc,None)
R=pd.DataFrame(Z,columns=cols)
print("5) sau FE bank + div×năm: sd dư / sd gốc, và tương quan dư:")
print((R.std()/dd[cols].std()).round(3).to_string())
print(R.corr().round(3).to_string())
dd[["idrssd","year"]+cols].to_parquet("/tmp/g1/g4_measures.parquet")
