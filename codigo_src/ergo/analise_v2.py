"""Passo 2: teste coerente da teoria de fluxo com a absortividade medida, agora incluindo a borda e > 0,995 (arquivos abs5).
Interpolacao em (ln x, j), com j = sqrt(1 - e^2). Gera resultado_v2.json e imprime um resumo.
Uso: python analise_v2.py [reamostragens=2000]"""
import sys, json, glob, numpy as np, pandas as pd
from scipy import stats
from scipy.interpolate import RegularGridInterpolator
B = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
rng = np.random.default_rng(2026)
x = np.exp(np.linspace(0, np.log(1e3), 900)); u = (np.arange(700) + .5) / 700; e = 1 - (1 - u) ** 2
X, E = np.meshgrid(x, e, indexing='ij'); J = np.sqrt(1 - E ** 2)
BASE = X ** -2.0 * E / np.sqrt(1 - E ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)],
        '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
CUT = 0.995

def load(m):
    fs = ['abs4_r20_%d,%d,%d.csv' % m, 'abs5_cauda_%d,%d,%d.csv' % m]
    a = pd.concat([pd.read_csv(f) for f in fs if glob.glob(f)]); return a[a.ok == 1]

def table(a, k):
    t = a.groupby(['x', 'e']).nSf.agg(K=lambda v: (v >= k).sum(), N='size').reset_index()
    t['j'] = np.sqrt(np.clip(1 - t.e ** 2, 0, None)).round(6)
    xs = np.sort(t.x.unique()); js = np.sort(t.j.unique())
    K = t.pivot(index='x', columns='j', values='K').reindex(index=xs, columns=js).values
    N = t.pivot(index='x', columns='j', values='N').reindex(index=xs, columns=js).values
    return xs, js, K, N

def field(xs, js, P):
    f = RegularGridInterpolator((np.log(xs), js), P, method='linear', bounds_error=False, fill_value=None)
    Lx = np.clip(np.log(X), np.log(xs[0]), np.log(xs[-1])); Jc = np.clip(J, js[0], js[-1])
    return np.clip(f(np.stack([Lx, Jc], -1)), 0, 1)

def weights(tabs, chans, Ps):
    return [mult * (ma * mb) ** 3 / (ma + mb) * BASE * field(xs, js, P) for ((ma, mb, ms), msc, mult), (xs, js, K, N), P in zip(chans, tabs, Ps)]

def cdf_of(W, mask=None):
    fe = sum(W).sum(0)
    if mask is not None: fe = fe * mask
    return np.cumsum(fe) / fe.sum()

d = pd.read_csv('age.csv'); fin = d[(d.exit == 'esc') & (d.status == 1)]
res = []
for k in (3, 4):
    for name, chans in SETS.items():
        tabs = [table(load(m), k) for m, _, _ in chans]
        P0 = [K / N for _, _, K, N in tabs]; W0 = weights(tabs, chans, P0)
        Ps = np.array([w.sum() for w in W0]); Ps /= Ps.sum()
        q = fin[(fin.set == name) & (fin.nS >= k)]; n = len(q); obs = q.e_exit.values
        c_all = cdf_of(W0); c_lo = cdf_of(W0, e <= CUT)
        lo = obs[obs <= CUT]; nlo = len(lo)
        ks = stats.kstest(obs, lambda v: np.interp(v, e, c_all)).statistic
        ks_lo = stats.kstest(lo, lambda v: np.interp(v, e, c_lo)).statistic
        null, null_lo = [], []
        for _ in range(B):
            Wb = weights(tabs, chans, [rng.binomial(N.astype(int), K / N) / N for _, _, K, N in tabs])
            cb = cdf_of(Wb); cbl = cdf_of(Wb, e <= CUT)
            null.append(stats.kstest(np.interp(rng.uniform(0, 1, n), cb, e), lambda v: np.interp(v, e, c_all)).statistic)
            null_lo.append(stats.kstest(np.interp(rng.uniform(0, 1, nlo), cbl, e), lambda v: np.interp(v, e, c_lo)).statistic)
        null, null_lo = np.array(null), np.array(null_lo)
        cnt = np.array([(q.mbody == c[1]).sum() for c in chans]); chi = stats.chisquare(cnt, Ps * n)
        fe = np.diff(np.r_[0, c_all])
        row = dict(k=k, conjunto=name, n=n, KS=float(ks), KS_critico95=float(np.quantile(null, .95)), p_KS=float((1 + (null >= ks).sum()) / (B + 1)),
                   n_ate_0995=nlo, KS_ate_0995=float(ks_lo), critico_ate_0995=float(np.quantile(null_lo, .95)), p_ate_0995=float((1 + (null_lo >= ks_lo).sum()) / (B + 1)),
                   e_medio_medido=float(obs.mean()), e_medio_previsto=float((fe * e).sum()),
                   frac_acima_0995_medida=float((obs > CUT).mean()), frac_acima_0995_prevista=float(fe[e > CUT].sum()),
                   escapes_medidos=(cnt / n).tolist(), escapes_previstos=Ps.tolist(), p_escapes=float(chi.pvalue))
        if name == '1-1-3':                                   # canal em que sobra o par 3-1 (fuga de um corpo leve)
            Wc = W0[0]; fc = Wc.sum(0) / Wc.sum(); l = q[q.mbody == 1].e_exit.values
            row['canal_par_3_1'] = dict(n=len(l), frac_e_ate_0872_medida=float((l <= 0.872).mean()), frac_e_ate_0872_prevista=float(fc[e <= 0.872].sum()))
        res.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
def holm(ps):
    o = np.argsort(ps); m = len(ps); ok = np.ones(m, bool)
    for r, i in enumerate(o):
        if ps[i] <= 0.05 / (m - r): ok[i] = False
        else: break
    return ok
for key, out in (('p_KS', 'formato_passa_holm'), ('p_ate_0995', 'formato_ate_0995_passa_holm'), ('p_escapes', 'escapes_passa_holm')):
    for r, v in zip(res, holm(np.array([r[key] for r in res]))): r[out] = bool(v)
json.dump(dict(reamostragens=B, corte=CUT, testes=res), open('resultado_v2.json', 'w'), indent=1, ensure_ascii=False)
print('\nRESUMO')
for r in res:
    print(f"k={r['k']} {r['conjunto']}: KS {r['KS']:.3f} (crit {r['KS_critico95']:.3f}, p={r['p_KS']:.4f}) {'PASSA' if r['formato_passa_holm'] else 'reprova'} | "
          f"ate 0,995: KS {r['KS_ate_0995']:.3f} (crit {r['critico_ate_0995']:.3f}, p={r['p_ate_0995']:.4f}) {'PASSA' if r['formato_ate_0995_passa_holm'] else 'reprova'} | "
          f"e {r['e_medio_medido']:.3f}/{r['e_medio_previsto']:.3f} | escapes {'PASSA' if r['escapes_passa_holm'] else 'reprova'}")
print('Arquivo gerado: resultado_v2.json')
