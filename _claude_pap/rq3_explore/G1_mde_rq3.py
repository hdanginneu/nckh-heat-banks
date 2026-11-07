import sys, os
sys.path.insert(0, os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"))
os.chdir(os.path.expanduser("~/mnt/NCKH - NEU/_claude_pap/scripts"))
from _pap_est import *
b = load_bank()
# thanh khoản: thay đổi tỷ lệ thanh khoản từ t-1 đến t+h = liq_l1(t+h+1) - liq_l1(t)
b = b.sort_values(["idrssd","year"]).copy()
for h in (0,1):
    nxt = b.groupby("idrssd")["liquidity_ratio_l1"].shift(-(h+1))
    # chỉ hợp lệ nếu năm liền kề
    yr = b.groupby("idrssd")["year"].shift(-(h+1))
    b[f"LIQ_h{h}"] = np.where(yr == b["year"]+h+1, 100*(nxt - b["liquidity_ratio_l1"]), np.nan)
rows=[]
for grp,gname in (("ag25","ag25"),(None,"all")):
    for y,hs in (("S_prov_cum",(0,1)),("LIQ",(0,1)),("S_loan_growth",(0,1)),("D1",(0,1))):
        for h in hs:
            col=f"{y}_h{h}"
            lead=f"heat_lead{h+1}"
            for fe_name,fe_col in (("div_year","div_year"),("state_year","state_year")):
                s = bank_frame(b, col, h, group=grp)
                s = s.dropna(subset=[lead])
                # winsor 1% de tranh outlier
                lo,hi = s[col].quantile([.01,.99]); s[col]=s[col].clip(lo,hi)
                try:
                    se0,n = null_se(s, col, [lead]+RAIN+BANK_CTRL, ["idrssd", fe_col], "hq_county_fips_l1", lat="hq_lat", lon="hq_lon")
                except Exception as ex:
                    print("ERR",col,gname,fe_name,ex); continue
                sd=float(s[col].std())
                rows.append(dict(sample=gname,y=col,fe=fe_name,n=n,n_banks=s.idrssd.nunique(),sd_y=sd,se0=se0,mde80=2.8016*se0,mde_in_sd=2.8016*se0/sd))
                print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv("/tmp/g1/mde_rq3.csv",index=False)
