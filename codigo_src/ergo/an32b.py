"""E32b: teto do teste - fluxo x absortividade MEDIDA (abs4, 200 por celula) nas quedas livres, com o mesmo criterio de 95%."""
import numpy as np, pandas as pd
from scipy import stats
from an30 import A_meas_interp, BASE, X, E, e
SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)], '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
ff = pd.read_csv('ffrand.csv'); ff = ff[(ff.status == 1) & (ff.nscram >= 5)]
for crit_col in ('nS', 'nSf'):
    errs = []
    for name, chans in SETS.items():
        Ws = []
        for (ma, mb, ms), msc, mult in chans:
            Am, _ = A_meas_interp(f'abs4_r20_{ma},{mb},{ms}.csv', crit_col); Ws.append(mult * (ma * mb) ** 3 / (ma + mb) * BASE * Am)
        Ps = np.array([W.sum() for W in Ws]); Ps /= Ps.sum()
        q = ff[ff.set == name]; n = len(q); meas = np.array([(q.mesc == c[1]).mean() for c in chans]); se = np.sqrt(meas * (1 - meas) / n)
        fe = sum(Ws).sum(0); fe /= fe.sum(); ks = stats.kstest(q.ecc, lambda v: np.interp(v, e, np.cumsum(fe))).statistic
        print(f'A medida ({crit_col}) {name}: n={n} escapes {np.round(meas,3)} x {np.round(Ps,3)} {"dentro" if np.all(np.abs(Ps-meas)<=1.96*se) else "FORA"} | <e> {q.ecc.mean():.3f} x {np.sum(fe*e):.3f} | KS {ks:.3f} (critico {1.36/np.sqrt(n):.3f})')
        errs += list(np.abs(Ps - meas)[[1]] if len(chans) == 2 else np.abs(Ps - meas))
    print(f'   erro medio escapes {np.mean(errs)*100:.2f} pontos')
