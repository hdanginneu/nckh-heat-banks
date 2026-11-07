import sys, os
S=os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"); sys.path.insert(0,S); os.chdir(S)
from _pap_est import *
P1=os.path.expanduser("~/mnt/NCKH - NEU/_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet")
cols=["idrssd","year","allowance_legacy_kusd","allowance_cecl_kusd","chargeoffs_ytd_kusd","recoveries_ytd_kusd","provision_ytd_kusd"]
p=pd.read_parquet(P1,columns=cols).drop_duplicates(["idrssd","year"])
b=load_bank().merge(p,on=["idrssd","year"],how="left",suffixes=("","_p"))
b=b.sort_values(["idrssd","year"]).reset_index(drop=True)
L1=b["totloans_l1"]  # kusd, t-1
def at(col,k):  # giá trị tại năm t+k nếu năm liền kề
    v=b.groupby("idrssd")[col].shift(-k); yr=b.groupby("idrssd")["year"].shift(-k)
    return pd.Series(np.where(yr==b["year"]+k,v,np.nan),index=b.index)
def prev(col):
    v=b.groupby("idrssd")[col].shift(1); yr=b.groupby("idrssd")["year"].shift(1)
    return pd.Series(np.where(yr==b["year"]-1,v,np.nan),index=b.index)
A=b["allowance_legacy_kusd"]; Am1=prev("allowance_legacy_kusd")
b["NCO_h0"]=100*(b.chargeoffs_ytd_kusd-b.recoveries_ytd_kusd)/L1
b["dALLOW_h0"]=100*(A-Am1)/L1
b["dALLOW_h1"]=100*(at("allowance_legacy_kusd",1)-Am1)/L1
b["ALLOWlag"]=100*Am1/L1
# năm bắt đầu CECL của từng ngân hàng
first=b[b.allowance_cecl_kusd.notna()].groupby("idrssd").year.min()
b["cecl_adopt_year"]=(b.year==b.idrssd.map(first)).astype(float)
# kiểm tra danh tính: dALLOW ~ PROV - NCO
x=b[["dALLOW_h0","S_prov_cum_h0","NCO_h0"]].dropna(); x=x[(x.S_prov_cum_h0.abs()<20)&(x.dALLOW_h0.abs()<20)]
print("corr(dALLOW, PROV-NCO)=",np.corrcoef(x.dALLOW_h0,x.S_prov_cum_h0-x.NCO_h0)[0,1].round(3),"n",len(x))
print("trung vi dALLOW_h0 theo nam:",b.groupby("year").dALLOW_h0.median().round(3).to_dict())
rows=[]
def run(col,grp,years,extra,tag,h):
    s=bank_frame(b,col,h,group=grp,years=years,extra_dropna=extra); s=s.dropna(subset=[f"heat_lead{h+1}"])
    lo,hi=s[col].quantile([.01,.99]); s[col]=s[col].clip(lo,hi)
    se0,n=null_se(s,col,[f"heat_lead{h+1}"]+RAIN+BANK_CTRL+list(extra),["idrssd","div_year"],"hq_county_fips_l1",lat="hq_lat",lon="hq_lon")
    sd=float(s[col].std()); r=dict(sample=grp or "all",y=col,spec=tag,years=f"{s.year.min()}-{s.year.max()}",n=n,n_banks=s.idrssd.nunique(),sd_y=sd,se0=se0,mde80=2.8016*se0,mde_sd=2.8016*se0/sd)
    rows.append(r); print(r,flush=True)
for grp in ("ag25",None):
    run("S_prov_cum_h0",grp,(2006,2022),[],"raw",0)
    run("S_prov_cum_h0",grp,(2006,2022),["NCO_h0","S_npl_total_h0","ALLOWlag"],"cond_NCO_dNPL_allowlag",0)
    run("dALLOW_h0",grp,(2006,2022),[],"raw",0)
    run("dALLOW_h0",grp,(2006,2022),["NCO_h0","S_npl_total_h0","ALLOWlag"],"cond_NCO_dNPL_allowlag",0)
    run("dALLOW_h0",grp,(2006,2023),["cecl_adopt_year"],"raw+adoptdummy",0)
    run("dALLOW_h1",grp,(2006,2022),[],"raw",1)
pd.DataFrame(rows).to_csv("/tmp/g1/g3_mde.csv",index=False)
