import sys, os
S=os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"); sys.path.insert(0,S); os.chdir(S)
from _pap_est import *
P1=os.path.expanduser("~/mnt/NCKH - NEU/_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet")
p=pd.read_parquet(P1,columns=["idrssd","year","allowance_legacy_kusd","chargeoffs_ytd_kusd","recoveries_ytd_kusd"]).drop_duplicates(["idrssd","year"])
b=load_bank().merge(p,on=["idrssd","year"],how="left").sort_values(["idrssd","year"]).reset_index(drop=True)
L1=b["totloans_l1"]
def prev(col):
    v=b.groupby("idrssd")[col].shift(1); yr=b.groupby("idrssd")["year"].shift(1)
    return pd.Series(np.where(yr==b["year"]-1,v,np.nan),index=b.index)
def at(col,k):
    v=b.groupby("idrssd")[col].shift(-k); yr=b.groupby("idrssd")["year"].shift(-k)
    return pd.Series(np.where(yr==b["year"]+k,v,np.nan),index=b.index)
Am1=prev("allowance_legacy_kusd")
b["NCO_h0"]=100*(b.chargeoffs_ytd_kusd-b.recoveries_ytd_kusd)/L1
b["dALLOW_h0"]=100*(b.allowance_legacy_kusd-Am1)/L1
b["ALLOWlag"]=100*Am1/L1
b["LIQ_h0"]=100*(at("liquidity_ratio_l1",1)-b["liquidity_ratio_l1"])
b["FS10"]=b["farmshare_pre"]*10           # +1 = +10 điểm % FarmShare
bk=b.drop_duplicates("idrssd")
print("=== PHÂN PHỐI FarmShare_pre (ngân hàng, N=%d) ==="%len(bk))
print(bk.farmshare_pre.describe(percentiles=[.1,.25,.5,.75,.9,.95]).round(3).to_string())
bins=[-.001,.05,.15,.25,.35,1.0]; lab=["<5%","5-15%","15-25%","25-35%",">35%"]
t=pd.cut(bk.farmshare_pre,bins,labels=lab).value_counts().reindex(lab)
print(t.to_string())
print("=== TƯƠNG QUAN FarmShare_pre với đặc điểm khác (mức ngân hàng, trung bình theo ngân hàng) ===")
g=b.groupby("idrssd").agg(fs=("farmshare_pre","first"),lta=("log_total_assets_l1","mean"),lat=("hq_lat","first"),heat=("heat","mean"),liq=("liquidity_ratio_l1","mean"),lta2=("loans_to_assets_l1","mean"),eq=("equity_to_assets","mean"))
print(g.corr()["fs"].round(3).to_string())
print("=== MDE tương tác heat_lead x FS10 (toàn mẫu, FE bank + div×năm) ===")
rows=[]
for col,extra,h,tag in (("D1_h0",[],0,"ref D1"),("S_prov_cum_h0",["NCO_h0","S_npl_total_h0","ALLOWlag"],0,"prov|cond"),("dALLOW_h0",["NCO_h0","S_npl_total_h0","ALLOWlag"],0,"dALLOW|cond"),("LIQ_h0",[],0,"dLIQ"),("S_loan_growth_h0",[],0,"loan growth")):
    s=bank_frame(b,col,h,group=None,years=(2007,2022),extra_dropna=extra+["FS10"]); lead=f"heat_lead{h+1}"
    s=s.dropna(subset=[lead]); s["x"]=s[lead]*s["FS10"]
    lo,hi=s[col].quantile([.01,.99]); s[col]=s[col].clip(lo,hi)
    se0,n=null_se(s,col,["x",lead]+RAIN+BANK_CTRL+extra,["idrssd","div_year"],"hq_county_fips_l1",lat="hq_lat",lon="hq_lon")
    sd=float(s[col].std()); r=dict(y=col,spec=tag,n=n,n_banks=s.idrssd.nunique(),sd_y=sd,sd_FS10=float(s.FS10.std()),se0=se0,mde80=2.8016*se0,mde_sd=2.8016*se0/sd)
    rows.append(r); print(r,flush=True)
pd.DataFrame(rows).to_csv("/tmp/g1/gB_mde.csv",index=False)
