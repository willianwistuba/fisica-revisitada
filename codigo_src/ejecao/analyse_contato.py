import numpy as np, pandas as pd, sys
fn=sys.argv[1] if len(sys.argv)>1 else 'contato.csv'
d=pd.read_csv(fn); d=d[(d.status==1)&(d.dE<1e-4)&(d.t_ej>0)]
def wilson(k,n,z=1.96):
    if n==0: return (np.nan,np.nan,np.nan)
    p=k/n; den=1+z*z/n; c=(p+z*z/(2*n))/den; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den; return p,c-h,c+h
rows=[]
for (fam,q),g in d.groupby(['fam','q']):
    L=g[g.esc.isin([0,1])]
    pn=wilson(int((L.esc!=L.nearer).sum()),len(L))
    for f in [0.1,0.2,0.3]:
        c=f'c{f}'; G=L[L[c]>=0]
        p=wilson(int((G.esc!=G[c]).sum()),len(G))
        D=G[G[c]!=G.nearer]; pd_=wilson(int((D.esc!=D[c]).sum()),len(D))
        late=G[G[f'tc{f}']>1.0]; pl=wilson(int((late.esc!=late[c]).sum()),len(late))
        rows.append(dict(fam=fam,q=q,f=f,ej_leve=len(L),frac_leve=len(L)/len(g),n=len(G),contato_fica=p[0],ic_lo=p[1],ic_hi=p[2],
            perto_fica=pn[0],n_discord=len(D),discord_contato_fica=pd_[0],dlo=pd_[1],dhi=pd_[2],n_tarde=len(late),tarde_fica=pl[0],tlo=pl[1],thi=pl[2]))
r=pd.DataFrame(rows); pd.set_option('display.width',250); print(r.round(3).to_string()); r.to_csv('contato_summary.csv',index=False)
