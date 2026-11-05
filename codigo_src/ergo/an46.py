"""E34c: teste coerente (Kirchhoff): mesmo limiar k de embaralhamentos na absortividade (antes da 1a excursao, nSf>=k)
e no escape (ultimo episodio com nS>=k)."""
import numpy as np, pandas as pd
from scipy import stats
import an33 as A
rng = np.random.default_rng(5)
d = pd.read_csv('age.csv'); fin = d[(d.exit == 'esc') & (d.status == 1)]
def table_k(fn, k):
    a = pd.read_csv(fn); a = a[a.ok == 1]
    t = a.groupby(['x', 'e']).nSf.agg(K=lambda v: (v >= k).sum(), N='size').reset_index()
    xs = np.sort(t.x.unique()); es = np.sort(t.e.unique())
    return xs, es, t.pivot(index='x', columns='e', values='K').values, t.pivot(index='x', columns='e', values='N').values
res = []
for k in (3, 4):
    for name, chans in A.SETS.items():
        tabs = [table_k(f'abs4_r20_{ma},{mb},{ms}.csv', k) for (ma, mb, ms), _, _ in chans]
        P0 = [K / N for _, _, K, N in tabs]; cdf0 = A.pred_cdf(tabs, chans, P0)
        cdfb = [A.pred_cdf(tabs, chans, [rng.binomial(N, K / N) / N for _, _, K, N in tabs]) for _ in range(200)]
        q = fin[(fin.set == name) & (fin.nS >= k)]; n = len(q)
        ks = stats.kstest(q.e_exit, lambda v: np.interp(v, A.e, cdf0)).statistic
        null = np.array([stats.kstest(np.interp(rng.uniform(0, 1, n), cb, A.e), lambda v: np.interp(v, A.e, cdf0)).statistic for cb in cdfb])
        W = [mult * (ma * mb) ** 3 / (ma + mb) * A.BASE * A.field(xs, es, P, 'linear') for ((ma, mb, ms), msc, mult), (xs, es, K, N), P in zip(chans, tabs, P0)]
        Ps = np.array([w.sum() for w in W]); Ps /= Ps.sum(); meas = np.array([(q.mbody == c[1]).mean() for c in chans]); se = np.sqrt(meas * (1 - meas) / n)
        pe = np.mean(null >= ks)
        # fracoes de escape: teste qui2 de aderencia
        obs = np.array([(q.mbody == c[1]).sum() for c in chans]); chi = stats.chisquare(obs, Ps * n)
        res.append((k, name, n, ks, np.quantile(null, .95), pe, q.e_exit.mean(), float(np.sum(np.diff(np.r_[0, cdf0]) * A.e)), np.round(meas, 3), np.round(Ps, 3), chi.pvalue))
R = pd.DataFrame(res, columns=['k', 'conjunto', 'n', 'KS', 'critico95', 'p_e', 'e_med', 'e_prev', 'escapes_med', 'escapes_prev', 'p_escapes'])
from statsmodels.stats.multitest import multipletests
R['e_ok_holm'] = ~multipletests(R.p_e, 0.05, 'holm')[0]; R['esc_ok_holm'] = ~multipletests(R.p_escapes, 0.05, 'holm')[0]
pd.set_option('display.width', 250); print(R.round(3).to_string(index=False))
