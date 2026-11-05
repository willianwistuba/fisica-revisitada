"""E33: o residuo na distribuicao de e e real ou vem da incerteza da propria previsao?
Teste justo: valor critico do KS obtido por simulacao, incluindo (i) o ruido binomial da absortividade medida (200 por celula,
reamostrada por bootstrap) e (ii) o sorteio de n finais. Tambem: onde a diferenca se concentra e sensibilidade a interpolacao."""
import numpy as np, pandas as pd
from scipy import stats
from scipy.interpolate import RegularGridInterpolator
rng = np.random.default_rng(1)
x = np.exp(np.linspace(0, np.log(1e3), 900)); u = (np.arange(700) + .5) / 700; e = 1 - (1 - u) ** 2
X, E = np.meshgrid(x, e, indexing='ij'); BASE = X ** -2.0 * E / np.sqrt(1 - E ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)], '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
ff = pd.read_csv('ffrand.csv'); ff = ff[(ff.status == 1) & (ff.nscram >= 5)]

def table(fn, crit):
    a = pd.read_csv(fn); a = a[a.ok == 1]
    t = a.groupby(['x', 'e'])[crit].agg(k=lambda v: (v >= 2).sum(), n='size').reset_index()
    xs = np.sort(t.x.unique()); es = np.sort(t.e.unique())
    K = t.pivot(index='x', columns='e', values='k').reindex(index=xs, columns=es).values
    N = t.pivot(index='x', columns='e', values='n').reindex(index=xs, columns=es).values
    return xs, es, K, N

def field(xs, es, P, method):
    f = RegularGridInterpolator((np.log(xs), es), P, method=method, bounds_error=False, fill_value=None)
    Lx = np.clip(np.log(X), np.log(xs[0]), np.log(xs[-1])); Ec = np.clip(E, es[0], es[-1])
    return np.clip(f(np.stack([Lx, Ec], -1)), 0, 1)

def pred_cdf(tabs, chans, Ps_list, method='linear'):
    W = 0
    for ((ma, mb, ms), msc, mult), (xs, es, K, N), P in zip(chans, tabs, Ps_list):
        W = W + mult * (ma * mb) ** 3 / (ma + mb) * BASE * field(xs, es, P, method)
    fe = W.sum(0); fe /= fe.sum(); return np.cumsum(fe)

if __name__ == '__main__':
    for crit in ('nS', 'nSf'):
        print(f'\n===== criterio de absorcao {crit} =====')
        for name, chans in SETS.items():
            tabs = [table(f'abs4_r20_{ma},{mb},{ms}.csv', crit) for (ma, mb, ms), _, _ in chans]
            P0 = [K / N for _, _, K, N in tabs]
            cdf0 = pred_cdf(tabs, chans, P0)
            q = ff[ff.set == name]; n = len(q); obs = np.sort(q.ecc.values)
            ks_obs = stats.kstest(obs, lambda v: np.interp(v, e, cdf0)).statistic
            # nulo: a verdade e uma tabela bootstrap; o "medido" sao n sorteios dela; comparamos com a previsao nominal
            null = []
            for b in range(300):
                Pb = [rng.binomial(N, K / N) / N for _, _, K, N in tabs]
                cdfb = pred_cdf(tabs, chans, Pb)
                sample = np.interp(rng.uniform(0, 1, n), cdfb, e)
                null.append(stats.kstest(sample, lambda v: np.interp(v, e, cdf0)).statistic)
            null = np.array(null); crit95 = np.quantile(null, 0.95); pval = (null >= ks_obs).mean()
            # onde fica a maior diferenca
            F_obs = np.searchsorted(obs, e, side='right') / n; dif = F_obs - cdf0; k = np.argmax(np.abs(dif))
            cdfn = pred_cdf(tabs, chans, P0, 'nearest'); ks_near = stats.kstest(obs, lambda v: np.interp(v, e, cdfn)).statistic
            print(f'{name}: n={n} KS {ks_obs:.3f} | critico ingenuo {1.36/np.sqrt(n):.3f} | critico com incerteza da previsao {crit95:.3f} (p={pval:.3f}) | '
                  f'maior diferenca em e={e[k]:.3f} ({"medido acima" if dif[k] > 0 else "medido abaixo"}) | KS com interpolacao vizinha {ks_near:.3f}')
            # diferenca por faixas de e
            bins = [0, .5, .8, .9, .95, .98, 1.0001]
            h_obs = np.histogram(obs, bins)[0] / n; c = np.interp(bins, e, cdf0, left=0, right=1); h_pr = np.diff(c)
            print('      faixa de e        ' + ' '.join(f'[{a:.2f},{b:.2f})' for a, b in zip(bins[:-1], bins[1:])))
            print('      medido            ' + ' '.join(f'{v:11.3f}' for v in h_obs))
            print('      previsto          ' + ' '.join(f'{v:11.3f}' for v in h_pr))
