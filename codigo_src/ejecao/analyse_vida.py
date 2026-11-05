import numpy as np, pandas as pd, sys
fn=sys.argv[1] if len(sys.argv)>1 else 'vida.csv'; CAP=float(sys.argv[2]) if len(sys.argv)>2 else 1e4
d=pd.read_csv(fn); d=d[d.dE<1e-4]
rows=[]
for (s,e),g in d.groupby(['set','ens'],sort=False):
    T=g['T'].values; cens=(g.status!=1).values; n=len(T)
    S=lambda t:((T>t)|(cens&(T>=t))).mean()
    hl=np.median(np.where(cens,np.inf,T))
    r=dict(set=s,ens=e,n=n,meia_vida=hl,S10=S(10),S100=S(100),S1000=S(1000),S_cap=cens.mean())
    for Tmin in (100,300):
        sel=T>Tmin; dn=(sel&~cens).sum(); L=np.log(np.minimum(T[sel],CAP)/Tmin).sum()
        a=dn/L if L>0 else np.nan; r[f'alfa_{Tmin}']=a; r[f'erro_{Tmin}']=a/np.sqrt(dn) if dn>0 else np.nan; r[f'n_{Tmin}']=sel.sum()
    lo=g[g['T']<=10]; hi=g[g['T']>100]
    r['exc_curtos']=lo.frac_exc.median(); r['exc_longos']=hi.frac_exc.median(); r['maior_exc_frac_longos']=(hi.max_exc/hi['T']).median()
    rows.append(r)
pd.set_option('display.width',250); print(pd.DataFrame(rows).round(3).to_string())
