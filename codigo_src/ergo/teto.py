"""Teto da teoria: previsao das quedas livres usando a absortividade MEDIDA (celulas abs4) no lugar da formula."""
import numpy as np, pandas as pd, prova11 as P
from scipy import stats
ff = pd.read_csv('quedas_livres.csv'); tab = {}
for name, chans in P.SETS.items():
    Ws = []
    for (ma, mb, ms), msc, mult in chans:
        ch = f'{int(ma)},{int(mb)},{int(ms)}'; d = pd.read_csv(f'abs4_r20_{ch}.csv')
        d['A'] = (d.nSf >= 2).astype(int); c = d.groupby(['x', 'e']).A.mean().unstack()
        xs, es = c.index.values, c.columns.values
        ix = np.abs(np.log(P.XG[..., None]) - np.log(xs)).argmin(-1); ie = np.abs(P.EG[..., None] - es).argmin(-1)
        Ws.append(mult * (ma * mb) ** 3 / (ma + mb) * P.BASE * c.values[ix, ie])
    Ps = np.array([W.sum() for W in Ws]); Ps /= Ps.sum(); fe = sum(Ws).sum(0); cdf = np.cumsum(fe) / fe.sum()
    q = ff[ff.set == name]; n = len(q)
    ks = stats.kstest(q.e_exit.values, lambda v: np.interp(v, P.eg, cdf)).statistic
    obs = np.array([(q.mbody == c[1]).sum() for c in chans]) / n
    print(f'{name}: KS com absortividade medida {ks:.3f} | escapes medidos {np.round(obs,3)} previstos {np.round(Ps,3)}')
