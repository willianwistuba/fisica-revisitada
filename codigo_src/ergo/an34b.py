"""E34b: teste da teoria (fluxo x A medida) com o corte ergodico certo: embaralhamentos no ULTIMO episodio."""
import numpy as np, pandas as pd
from scipy import stats
import an33 as A
rng = np.random.default_rng(3)
d = pd.read_csv('age.csv'); fin = d[(d.exit == 'esc') & (d.status == 1)]
for crit in ('nS', 'nSf'):
    print(f'== absortividade com criterio {crit}')
    for name, chans in A.SETS.items():
        tabs = [A.table(f'abs4_r20_{ma},{mb},{ms}.csv', crit) for (ma, mb, ms), _, _ in chans]
        P0 = [K / N for _, _, K, N in tabs]; cdf0 = A.pred_cdf(tabs, chans, P0)
        Pboot = [[rng.binomial(N, K / N) / N for _, _, K, N in tabs] for _ in range(200)]; cdfb = [A.pred_cdf(tabs, chans, Pb) for Pb in Pboot]
        for cut in (1, 3, 5):
            q = fin[(fin.set == name) & (fin.nS >= cut)]; n = len(q)
            ks = stats.kstest(q.e_exit, lambda v: np.interp(v, A.e, cdf0)).statistic
            null = [stats.kstest(np.interp(rng.uniform(0, 1, n), cb, A.e), lambda v: np.interp(v, A.e, cdf0)).statistic for cb in cdfb]
            c95 = np.quantile(null, 0.95); p = np.mean(np.array(null) >= ks)
            meas = np.array([(q.mbody == c[1]).mean() for c in chans])
            W = [mult * (ma * mb) ** 3 / (ma + mb) * A.BASE * A.field(xs, es, P, 'linear') for ((ma, mb, ms), msc, mult), (xs, es, K, N), P in zip(chans, tabs, P0)]
            Ps = np.array([w.sum() for w in W]); Ps /= Ps.sum(); se = np.sqrt(meas * (1 - meas) / n)
            print(f'   {name} ultimo episodio >= {cut}: n={n:5d} | KS {ks:.3f} critico {c95:.3f} p={p:.3f} {"PASSA" if ks < c95 else "rejeita"} | <e> {q.e_exit.mean():.3f} x {np.sum(np.diff(np.r_[0, cdf0]) * A.e):.3f} | escapes {np.round(meas,3)} x {np.round(Ps,3)} {"dentro" if np.all(np.abs(Ps-meas) <= 1.96*se) else "fora"}')
