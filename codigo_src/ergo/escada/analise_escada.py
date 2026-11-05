"""Escada de massas 1-1-M: teste coerente (k = 3 e 4) com a absortividade medida (grade principal mais borda em j),
delta com sinal, canal de fuga leve, geometria do ultimo episodio e tendencias contra ln M. Gera escada_aqui.json."""
import sys, json, glob, numpy as np, pandas as pd
from scipy import stats
from scipy.interpolate import RegularGridInterpolator
from multiprocessing import Pool
B = int(sys.argv[1]) if len(sys.argv) > 1 else 500
x = np.exp(np.linspace(0, np.log(1e3), 900)); u = (np.arange(700) + .5) / 700; e = 1 - (1 - u) ** 2
X, E = np.meshgrid(x, e, indexing='ij'); J = np.sqrt(1 - E ** 2)
BASE = X ** -2.0 * E / np.sqrt(1 - E ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
CUT = 0.995
fmt = lambda m: ','.join('%g' % v for v in m)
# M = 3: dados da nota 15 (sementes originais) e replica independente; absortividade em ../pacote_v2
FONTES = {2: 'age_1-1-2.csv', 2.5: 'age_1-1-2.5.csv', 2.75: 'age_1-1-2.75.csv', 3.25: 'age_1-1-3.25.csv', 3.5: 'age_1-1-3.5.csv',
          4: 'age_1-1-4.csv', 5: 'age_1-1-5.csv', '3 original': '../exp/ergo/age.csv', '3 replica': '../pacote_v2/age_113_rep.csv'}
def load(m):
    fs = [f'abs4_r20_{fmt(m)}.csv', f'abs5_cauda_{fmt(m)}.csv']
    if m in ((1., 3., 1.), (1., 1., 3.)): fs = ['../pacote_v2/abs4_r20_%d,%d,%d.csv' % m, '../pacote_v2/abs5_cauda_%d,%d,%d.csv' % m]
    a = pd.concat([pd.read_csv(f) for f in fs]); return a[a.ok == 1]
def table(a, k):
    t = a.groupby(['x', 'e']).nSf.agg(K=lambda v: (v >= k).sum(), N='size').reset_index()
    t['j'] = np.sqrt(np.clip(1 - t.e ** 2, 0, None)).round(6)
    xs = np.sort(t.x.unique()); js = np.sort(t.j.unique())
    return xs, js, t.pivot(index='x', columns='j', values='K').reindex(index=xs, columns=js).values, t.pivot(index='x', columns='j', values='N').reindex(index=xs, columns=js).values
def field(xs, js, P):
    f = RegularGridInterpolator((np.log(xs), js), P, method='linear', bounds_error=False, fill_value=None)
    return np.clip(f(np.stack([np.clip(np.log(X), np.log(xs[0]), np.log(xs[-1])), np.clip(J, js[0], js[-1])], -1)), 0, 1)
def weights(tabs, chans, Ps):
    return [mult * (ma * mb) ** 3 / (ma + mb) * BASE * field(xs, js, P) for ((ma, mb, ms), msc, mult), (xs, js, K, N), P in zip(chans, tabs, Ps)]
def cdf_of(W, mask=None):
    fe = sum(W).sum(0)
    if mask is not None: fe = fe * mask
    return np.cumsum(fe) / fe.sum()
def teste(arg):
    lab, k = arg; M = 3.0 if isinstance(lab, str) else float(lab); rng = np.random.default_rng(int(1000 * M) + k + (7 if lab == '3 replica' else 0))
    chans = [((1., M, 1.), 1., 2), ((1., 1., M), M, 1)]
    d = pd.read_csv(FONTES[lab]); fin = d[(d.exit == 'esc') & (d.status == 1)]
    if lab == '3 original': fin = fin[fin.set == '1-1-3']
    q = fin[fin.nS >= k]; n = len(q); obs = q.e_exit.values
    tabs = [table(load(m), k) for m, _, _ in chans]; W0 = weights(tabs, chans, [K / N for _, _, K, N in tabs])
    Ps = np.array([w.sum() for w in W0]); Ps /= Ps.sum()
    c_all = cdf_of(W0); c_lo = cdf_of(W0, e <= CUT); lo = obs[obs <= CUT]
    ks = stats.kstest(obs, lambda v: np.interp(v, e, c_all)).statistic; ks_lo = stats.kstest(lo, lambda v: np.interp(v, e, c_lo)).statistic
    fe0 = np.diff(np.r_[0, c_all]); eprev = float((fe0 * e).sum()); delta = float(obs.mean() - eprev)
    null, null_lo, dboot = [], [], []
    for _ in range(B):
        Wb = weights(tabs, chans, [rng.binomial(N.astype(int), K / N) / N for _, _, K, N in tabs]); cb = cdf_of(Wb); cbl = cdf_of(Wb, e <= CUT)
        null.append(stats.kstest(np.interp(rng.uniform(0, 1, n), cb, e), lambda v: np.interp(v, e, c_all)).statistic)
        null_lo.append(stats.kstest(np.interp(rng.uniform(0, 1, len(lo)), cbl, e), lambda v: np.interp(v, e, c_lo)).statistic)
        dboot.append(rng.choice(obs, n).mean() - float((np.diff(np.r_[0, cb]) * e).sum()))
    null, null_lo, dboot = map(np.array, (null, null_lo, dboot))
    cnt = np.array([(q.mbody == c[1]).sum() for c in chans]); chi = stats.chisquare(cnt, Ps * n)
    fc = W0[0].sum(0) / W0[0].sum(); l = q[q.mbody == 1].e_exit.values
    return dict(degrau=str(lab), M=M, k=k, n=n, KS=float(ks), KS_critico95=float(np.quantile(null, .95)), p_KS=float((1 + (null >= ks).sum()) / (B + 1)),
                KS_ate_0995=float(ks_lo), critico_ate_0995=float(np.quantile(null_lo, .95)), p_ate_0995=float((1 + (null_lo >= ks_lo).sum()) / (B + 1)),
                e_medido=float(obs.mean()), e_previsto=eprev, delta=delta, delta_ic95=[float(v) for v in np.quantile(dboot, [.025, .975])], delta_var=float(dboot.var()),
                escapes_medidos=(cnt / n).tolist(), escapes_previstos=Ps.tolist(), p_escapes=float(chi.pvalue),
                canal_leve=dict(n=len(l), medida=float((l <= 0.872).mean()), prevista=float(fc[e <= 0.872].sum())))
if __name__ == '__main__':
    labs = [2, 2.5, 2.75, '3 original', '3 replica', 3.25, 3.5, 4, 5]
    with Pool(2) as pl: res = pl.map(teste, [(l, k) for l in labs for k in (3, 4)])
    def holm(ps):
        o = np.argsort(ps); m = len(ps); ok = np.ones(m, bool)
        for r, i in enumerate(o):
            if ps[i] <= 0.05 / (m - r): ok[i] = False
            else: break
        return ok
    novos = [r for r in res if r['degrau'] != '3 original']           # Holm sobre os testes com dados novos
    for key, out in (('p_KS', 'formato_passa'), ('p_ate_0995', 'formato_ate_0995_passa'), ('p_escapes', 'escapes_passa')):
        for r, v in zip(novos, holm(np.array([r[key] for r in novos]))): r[out] = bool(v)
    tend = {}
    for k in (3, 4):
        rr = [r for r in novos if r['k'] == k]; xm = np.log([r['M'] for r in rr]); y = np.array([r['delta'] for r in rr]); w = 1 / np.array([r['delta_var'] for r in rr])
        A = np.vstack([np.ones_like(xm), xm]).T; Wm = np.diag(w); cov = np.linalg.inv(A.T @ Wm @ A); b = cov @ A.T @ Wm @ y
        res_ = y - A @ b; s2 = (w * res_ ** 2).sum() / (len(y) - 2); se = np.sqrt(cov[1, 1] * s2); t = b[1] / se
        tend[str(k)] = dict(inclinacao=float(b[1]), erro_padrao=float(se), p=float(2 * stats.t.sf(abs(t), len(y) - 2)))
    json.dump(dict(reamostragens=B, testes=res, tendencia_delta=tend), open('escada_aqui.json', 'w'), indent=1)
    for r in sorted(res, key=lambda r: (r['k'], r['M'], r['degrau'])):
        print(f"k={r['k']} {r['degrau']:>10}: n={r['n']} KS {r['KS']:.3f}/{r['KS_critico95']:.3f} p={r['p_KS']:.3f} | ate0995 p={r['p_ate_0995']:.3f} | "
              f"delta {r['delta']:+.3f} [{r['delta_ic95'][0]:+.3f},{r['delta_ic95'][1]:+.3f}] | canal leve {r['canal_leve']['medida']:.3f}/{r['canal_leve']['prevista']:.3f} | "
              f"escapes p={r['p_escapes']:.3f} | {'' if r['degrau'] == '3 original' else ('formato OK' if r['formato_passa'] else 'FORMATO REPROVA')}")
    print('tendencia de delta contra ln M:', tend)
