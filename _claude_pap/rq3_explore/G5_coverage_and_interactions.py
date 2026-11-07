import sys, os
S=os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"); sys.path.insert(0,S); os.chdir(S)
from _pap_est import *
ROOT=os.path.expanduser("~/mnt/NCKH - NEU")
# 1) bao phủ bảo hiểm cấp ngân hàng, TIỀN XÁC ĐỊNH: trọng số tiền gửi của năm phân tích đầu tiên của ngân hàng
cov=pd.read_csv(OUT/"rma_coverage_ratio.csv",dtype={"fips":str})[["fips","liab_0105","crop_rec_0105_usd","coverage_ratio_0105"]]
W=pd.read_parquet(f"{ROOT}/_drive_latest/full_obs_2005_25_tmax30/PHASE2/phase2_footprint_weights_lag1.parquet",columns=["analysis_year","idrssd","county_fips","deposit_weight_l1"])
W=W[(W.deposit_weight_l1>0)&(W.analysis_year>=2006)]
first=W.groupby("idrssd").analysis_year.min().rename("y0")
W=W.merge(first,on="idrssd"); W=W[W.analysis_year==W.y0]
m=W.merge(cov,left_on="county_fips",right_on="fips",how="left")
m["has"]=m.coverage_ratio_0105.notna()
g=m.groupby("idrssd").apply(lambda d: pd.Series({
  "cov_dep": (d.deposit_weight_l1*d.coverage_ratio_0105).sum()/d.loc[d.has,"deposit_weight_l1"].sum() if d.has.any() else np.nan,
  "cov_crop": d.liab_0105.sum()/d.crop_rec_0105_usd.sum() if d.crop_rec_0105_usd.sum()>0 else np.nan,
  "w_cov": d.loc[d.has,"deposit_weight_l1"].sum()/d.deposit_weight_l1.sum()}),include_groups=False).reset_index()
b=load_bank()
g["idrssd"]=g.idrssd.astype(b.idrssd.dtype)
bk=b.drop_duplicates("idrssd")[["idrssd","farmshare_pre","division","log_total_assets_l1"]].merge(g,on="idrssd",how="left")
print("N ngân hàng:",len(bk),"| có cov_dep:",bk.cov_dep.notna().sum(),"| w_cov median",bk.w_cov.median().round(3))
print("=== phân phối bao phủ (liability/doanh thu cây trồng 2001-05) ===")
print(bk[["cov_dep","cov_crop"]].describe(percentiles=[.05,.25,.5,.75,.95]).round(3).to_string())
hi=bk[bk.farmshare_pre>=0.15]
print(f"--- trong ngân hàng FarmShare>=15% (chỉ mô tả, N={len(hi)}) ---")
print(hi[["cov_dep","cov_crop"]].describe(percentiles=[.05,.25,.5,.75,.95]).round(3).to_string())
print("tương quan (toàn mẫu):"); print(bk[["farmshare_pre","cov_dep","cov_crop","log_total_assets_l1"]].corr().round(3).to_string())
print("phương sai bao phủ GIỮA division / tổng (FS>=15%): ",
      round(float(hi.groupby("division").cov_dep.transform("mean").var()/hi.cov_dep.var()),3))
bk[["idrssd","cov_dep","cov_crop","w_cov"]].to_parquet("/tmp/g1/bank_coverage.parquet")
# 2) MDE cho Heat×Clim và Heat×FS×Cov
p=pd.read_parquet(f"{ROOT}/_drive_latest/full_obs/phase1/phase1_community_all_observations_2005_2025-2.parquet",columns=["idrssd","year","allowance_legacy_kusd","chargeoffs_ytd_kusd","recoveries_ytd_kusd"]).drop_duplicates(["idrssd","year"])
b=b.merge(p,on=["idrssd","year"],how="left").merge(g,on="idrssd",how="left").sort_values(["idrssd","year"]).reset_index(drop=True)
L1=b["totloans_l1"]
v=b.groupby("idrssd")["allowance_legacy_kusd"].shift(1); yr=b.groupby("idrssd")["year"].shift(1)
Am1=pd.Series(np.where(yr==b.year-1,v,np.nan),index=b.index)
b["NCO_h0"]=100*(b.chargeoffs_ytd_kusd-b.recoveries_ytd_kusd)/L1
b["dALLOW_h0"]=100*(b.allowance_legacy_kusd-Am1)/L1
b["ALLOWlag"]=100*Am1/L1
b["FS10"]=b.farmshare_pre*10
bm=b.groupby("idrssd").heat.transform("mean"); bs=bm.std(); b["Clim"]=(bm-bm.mean())/bs   # khí hậu = trung bình nhiệt của ngân hàng, chuẩn hóa
b["Cov"]=(b.cov_dep-b.cov_dep.mean())/b.cov_dep.std()
rows=[]
def mde(col,extra,tag,inter):
    lead="heat_lead1"
    s=bank_frame(b,col,0,group=None,years=(2007,2022),extra_dropna=extra+inter["need"]); s=s.dropna(subset=[lead])
    for nm,expr in inter["terms"].items(): s[nm]=expr(s,lead)
    lo,hi_=s[col].quantile([.01,.99]); s[col]=s[col].clip(lo,hi_)
    xs=list(inter["terms"].keys())+[lead]+RAIN+BANK_CTRL+extra
    se0,n=null_se(s,col,xs,["idrssd","div_year"],"hq_county_fips_l1",lat="hq_lat",lon="hq_lon")
    sd=float(s[col].std()); r=dict(y=col,test=tag,n=n,n_banks=s.idrssd.nunique(),se0=se0,mde80=2.8016*se0,mde_sd=2.8016*se0/sd); rows.append(r); print(r,flush=True)
cond=["NCO_h0","S_npl_total_h0","ALLOWlag"]
for col,extra in (("S_prov_cum_h0",cond),("dALLOW_h0",cond)):
    mde(col,extra,"Heat×Clim (toàn mẫu)",dict(need=["Clim"],terms={"x_clim":lambda s,l:s[l]*s["Clim"]}))
    mde(col,extra,"Heat×FS10×Cov (toàn mẫu, kèm Heat×FS10, Heat×Cov)",dict(need=["FS10","Cov"],terms={
        "x3":lambda s,l:s[l]*s["FS10"]*s["Cov"],"x_fs":lambda s,l:s[l]*s["FS10"],"x_cov":lambda s,l:s[l]*s["Cov"]}))
pd.DataFrame(rows).to_csv("/tmp/g1/g5_mde.csv",index=False)
