"""E46/E47: testes 1 e 2 do 1-1-3.
H1: sensibilidade da previsao a absortividade acima de x = 20 (constante, zero, dobro) e peso previsto acima de 20.
H2: regua alternativa da literatura, configuracoes democraticas (raio de homologia > 0,33): absorcao nDf>=k, emissao nD>=k."""
import numpy as np, pandas as pd
from scipy import stats
import an33 as A
rng = np.random.default_rng(5)
d = pd.read_csv('age.csv'); fin = d[(d.exit == 'esc') & (d.status == 1)]
def table_k(fn, k, col):
    a = pd.read_csv(fn); a = a[a.ok == 1]
    t = a.groupby(['x', 'e'])[col].agg(K=lambda v: (v >= k).sum(), N='size').reset_index()
    xs = np.sort(t.x.unique()); es = np.sort(t.e.unique())
    return xs, es, t.pivot(index='x', columns='e', values='K').values, t.pivot(index='x', columns='e', values='N').values
hi = A.X > 20.0
def pred(tabs, chans, Ps, mode):
    W = 0
    for ((ma, mb, ms), msc, mult), (xs, es, K, N), P in zip(chans, tabs, Ps):
        F = A.field(xs, es, P, 'linear')
        if mode == 'zero': F = np.where(hi, 0, F)
        if mode == 'dobro': F = np.where(hi, np.clip(2 * F, 0, 1), F)
        W = W + mult * (ma * mb) ** 3 / (ma + mb) * A.BASE * F
    return W
def ks_test(name, chans, k, acol, ecol, mode='const', nb=200):
    tabs = [table_k(f'abs4_r20_{ma},{mb},{ms}.csv', k, acol) for (ma, mb, ms), _, _ in chans]
    P0 = [K / N for _, _, K, N in tabs]
    W0 = pred(tabs, chans, P0, mode); fe = W0.sum(0); cdf0 = np.cumsum(fe) / fe.sum(); whi = W0[hi].sum() / W0.sum()
    q = fin[(fin.set == name) & (fin[ecol] >= k)]; n = len(q)
    ks = stats.kstest(q.e_exit, lambda v: np.interp(v, A.e, cdf0)).statistic
    null = []
    for _ in range(nb):
        Wb = pred(tabs, chans, [rng.binomial(N, K / N) / N for _, _, K, N in tabs], mode); fb = Wb.sum(0); cb = np.cumsum(fb) / fb.sum()
        null.append(stats.kstest(np.interp(rng.uniform(0, 1, n), cb, A.e), lambda v: np.interp(v, A.e, cdf0)).statistic)
    null = np.array(null)
    return dict(conj=name, k=k, regua=acol + '/' + ecol, extrap=mode, n=n, KS=round(ks, 3), crit=round(float(np.quantile(null, .95)), 3),
                p=round(float((null >= ks).mean()), 3), e_med=round(q.e_exit.mean(), 3), e_prev=round(float(np.sum(np.diff(np.r_[0, cdf0]) * A.e)), 3), peso_x20=round(float(whi), 3))
rows = []
ch = A.SETS['1-1-3']
for k in (3, 4):
    for mode in ('const', 'zero', 'dobro'):
        rows.append(ks_test('1-1-3', ch, k, 'nSf', 'nS', mode, nb=100))
for k in (3, 4):
    for name, chans in A.SETS.items():
        rows.append(ks_test(name, chans, k, 'nDf', 'nD', 'const'))
pd.set_option('display.width', 250); print(pd.DataFrame(rows).to_string(index=False))
