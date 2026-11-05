"""E33b: o residuo diminui se exigirmos mais embaralhamentos (menos memoria do inicio)?"""
import numpy as np, pandas as pd
from scipy import stats
import an33 as A
ff = pd.read_csv('ffrand.csv'); ff = ff[ff.status == 1]
for name, chans in A.SETS.items():
    tabs = [A.table(f'abs4_r20_{ma},{mb},{ms}.csv', 'nSf') for (ma, mb, ms), _, _ in chans]
    cdf0 = A.pred_cdf(tabs, chans, [K / N for _, _, K, N in tabs])
    line = []
    for m in (5, 10, 20, 40):
        q = ff[(ff.set == name) & (ff.nscram >= m)]; n = len(q)
        ks = stats.kstest(q.ecc, lambda v: np.interp(v, A.e, cdf0)).statistic
        hi = (q.ecc >= 0.95).mean(); hp = 1 - np.interp(0.95, A.e, cdf0)
        line.append(f'>= {m:2d}: n={n:4d} KS {ks:.3f} (ingenuo {1.36/np.sqrt(n):.3f}) frac e>=0.95 med {hi:.3f} prev {hp:.3f}')
    print(name + '\n   ' + '\n   '.join(line))
