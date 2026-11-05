"""E30c: o 'muro' de excentricidade explica o erro de <e> no 3-3-1? Diagnostico: formula v2 x muro e > c*vinf/vorb (teto 0,5)."""
import numpy as np, pandas as pd, json
from scipy import stats
import formula_v2 as F2
P = json.load(open('formula_v2.json'))
x = np.exp(np.linspace(0, np.log(1e3), 900)); u = (np.arange(700) + .5) / 700; e = 1 - (1 - u) ** 2
X, E = np.meshgrid(x, e, indexing='ij'); BASE = X ** -2.0 * E / np.sqrt(1 - E ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
def estar(X, ma, mb, ms, c=0.85, cap=0.5):
    mB = ma + mb; M = mB + ms; aB = ma * mb / (2 * X); mus = ms * mB / M
    return np.minimum(c * np.sqrt(2 * (X - 1) / mus) / np.sqrt(mB / aB), cap)
ff = pd.read_csv('ffrand.csv'); q = ff[(ff.set == '3-3-1') & (ff.status == 1) & (ff.nscram >= 5)]
chans = [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)]
for lab, wall in (('v2 sem muro', False), ('v2 com muro no canal 3,3,1', True)):
    Ws = []
    for (ma, mb, ms), mesc, mult in chans:
        Af = F2.A(X, E, ma, mb, ms, P)
        if wall and (ma, mb, ms) == (3, 3, 1): Af = Af * (E > estar(X, ma, mb, ms))
        Ws.append(mult * (ma * mb) ** 3 / (ma + mb) * BASE * Af)
    Ps = np.array([W.sum() for W in Ws]); Ps /= Ps.sum()
    fe = sum(Ws).sum(0); fe /= fe.sum(); ks = stats.kstest(q.ecc, lambda v: np.interp(v, e, np.cumsum(fe))).statistic
    meas = [(q.mesc == c[1]).mean() for c in chans]
    print(f'{lab:30s} escapes medido {np.round(meas,3)} formula {np.round(Ps,3)} | <e> medido {q.ecc.mean():.3f} formula {np.sum(fe*e):.3f} KS {ks:.3f}')
