import numpy as np, pandas as pd
from scipy.optimize import minimize
d=pd.read_csv('speed.csv'); d=d[d.ok==1].reset_index(drop=True)
FR=[0.25,0.5,0.75,0.9]; rng=np.random.default_rng(1)
def acc_argmax(S,y):
    # S: n x 3 scores; ties count fractional
    mx=S.max(1,keepdims=True); tie=np.isclose(S,mx); return (tie[np.arange(len(y)),y]/tie.sum(1)).mean()
def fit(X,y):  # conditional logit, X: n x 3 x p
    p=X.shape[2]
    def nll(b):
        u=X@b; u=u-u.max(1,keepdims=True); return -(u[np.arange(len(y)),y]-np.log(np.exp(u).sum(1))).sum()+1e-3*b@b
    return minimize(nll,np.zeros(p),method='BFGS').x
def cv(X,y,groups,K=5):
    idx=rng.permutation(len(y)); folds=np.array_split(idx,K); pred=np.zeros(len(y),int)
    for f in folds:
        tr=np.setdiff1d(idx,f); b=fit(X[tr],y[tr]); pred[f]=(X[f]@b).argmax(1)
    return pred
lm=np.log(d[['m0','m1','m2']].values); lm=lm-lm.mean(1,keepdims=True); y=d.esc.values.astype(int)
res=[]
for f in FR:
    ri=np.log(np.maximum(d[[f'ri{f}_{k}' for k in range(3)]].values,1e-2)); ra=d[[f'ra{f}_{k}' for k in range(3)]].values
    Xm=lm[:,:,None]; Xs=np.stack([ri,ra],2); Xc=np.concatenate([Xm,Xs],2)
    for ens in ['frio','virial']:
        sel=(d.ens==ens).values
        pm=cv(Xm[sel],y[sel],None); ps=cv(Xs[sel],y[sel],None); pc=cv(Xc[sel],y[sel],None)
        sub=d[sel].reset_index(drop=True)
        for s in ['1-1-1','1-1-3','1-1-10','3-3-1','10-10-1','aleat']:
            g=(sub.set==s).values; yy=y[sel][g]
            res.append(dict(f=f,ens=ens,set=s,n=g.sum(),
              massa=acc_argmax(-lm[sel][g],yy),               # mais leve
              vel_inst=acc_argmax(ri[sel][g],yy), vel_media=acc_argmax(ra[sel][g],yy),
              logit_massa=(pm[g]==yy).mean(), logit_vel=(ps[g]==yy).mean(), logit_ambos=(pc[g]==yy).mean()))
r=pd.DataFrame(res); pd.set_option('display.width',200)
print(r.round(3).to_string()); r.to_csv('speed_summary.csv',index=False)
# coeficientes no conjunto completo, f=0.5
f=0.5; ri=np.log(np.maximum(d[[f'ri{f}_{k}' for k in range(3)]].values,1e-2)); ra=d[[f'ra{f}_{k}' for k in range(3)]].values
for ens in ['frio','virial']:
    sel=(d.ens==ens).values; b=fit(np.concatenate([lm[:,:,None],np.stack([ri,ra],2)],2)[sel],y[sel]); print(ens,'coef [log m, log rho inst, <log rho>]:',b.round(2))
