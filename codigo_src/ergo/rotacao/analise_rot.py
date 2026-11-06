"""Analise do estudo de rotacao (PREREGISTRO.md): 8 testes confirmatorios (KS do formato, conjunto x lam x k, Holm)
e exploratorios (ate e <= 0,995; escapes por corpo; razao prograda/retrograda; delta e).
Uso: python analise_rot.py <pasta_dados> [reamostragens=500]. Gera resultado_rotacao.json."""
import sys, json, numpy as np, pandas as pd
from scipy import stats
from scipy.interpolate import RegularGridInterpolator
from multiprocessing import Pool
D = sys.argv[1]; B = int(sys.argv[2]) if len(sys.argv) > 2 else 500
x = np.exp(np.linspace(0, np.log(1e3), 900)); u = (np.arange(700) + .5) / 700; e = 1 - (1 - u) ** 2
X, E = np.meshgrid(x, e, indexing='ij'); J = np.sqrt(1 - E ** 2)
BASE = X ** -2.0 * E / np.sqrt(1 - E ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
CUT = 0.995
CONJ = {'1-1-3': [((1., 3., 1.), 1., 2), ((1., 1., 3.), 3., 1)],
        '1-2-3': [((2., 3., 1.), 1., 1), ((1., 3., 2.), 2., 1), ((1., 2., 3.), 3., 1)]}
fmt = lambda m: ','.join('%g' % v for v in m)
def load(m, lam):
    return pd.concat([pd.read_csv(f'{D}/{t}_{fmt(m)}_lam{lam}.csv') for t in ('abs4_r20', 'abs5_cauda')])
def table(a, k, s):
    a = a[a.s == s].copy(); a['hit'] = (a.ok == 1) & (a.nSf >= k)          # sem alcance (ok = 0) conta como nao absorvida
    a = a[(a.ok == 1) | (a.alcance == 0)]
    t = a.groupby(['x', 'e']).hit.agg(K='sum', N='size').reset_index()
    t['j'] = np.sqrt(np.clip(1 - t.e ** 2, 0, None)).round(6)
    xs = np.sort(t.x.unique()); js = np.sort(t.j.unique())
    P = lambda c: t.pivot(index='x', columns='j', values=c).reindex(index=xs, columns=js).values
    return xs, js, P('K'), P('N')
def field(xs, js, P):
    f = RegularGridInterpolator((np.log(xs), js), P, method='linear', bounds_error=False, fill_value=None)
    return np.clip(f(np.stack([np.clip(np.log(X), np.log(xs[0]), np.log(xs[-1])), np.clip(J, js[0], js[-1])], -1)), 0, 1)
def weights(chans, tabs, Ps):
    """lista por canal de (W_pro, W_ret)."""
    out = []
    for ((ma, mb, ms), msc, mult), tc, pc in zip(chans, tabs, Ps):
        fac = mult * (ma * mb) ** 3 / (ma + mb) * BASE
        out.append(tuple(fac * field(xs, js, P) for (xs, js, K, N), P in zip(tc, pc)))
    return out
def cdf_of(W, mask=None):
    fe = sum(w[0] + w[1] for w in W).sum(0)
    if mask is not None: fe = fe * mask
    return np.cumsum(fe) / fe.sum()
def teste(arg):
    nome, lam, k = arg; chans = CONJ[nome]; rng = np.random.default_rng(int(1000 * lam) + 10 * k + len(nome) + (0 if nome == '1-1-3' else 5))
    d = pd.read_csv(f'{D}/age_{nome}_lam{lam}.csv'); fin = d[(d.exit == 'esc') & (d.status == 1)]
    q = fin[fin.nS >= k]; n = len(q); obs = q.e_exit.values; lo = obs[obs <= CUT]
    tabs = [[table(load(m, lam), k, s) for s in (1, -1)] for m, _, _ in chans]
    P0 = [[K / N for _, _, K, N in tc] for tc in tabs]; W0 = weights(chans, tabs, P0)
    c_all = cdf_of(W0); c_lo = cdf_of(W0, e <= CUT)
    ks = stats.kstest(obs, lambda v: np.interp(v, e, c_all)).statistic; ks_lo = stats.kstest(lo, lambda v: np.interp(v, e, c_lo)).statistic
    fe0 = np.diff(np.r_[0, c_all]); eprev = float((fe0 * e).sum())
    tot = np.array([[w.sum() for w in ww] for ww in W0]); Pesc = tot.sum(1) / tot.sum(); fpro = tot[:, 0].sum() / tot.sum()
    null, null_lo, dboot, proboot = [], [], [], []
    for _ in range(B):
        Pb = [[rng.binomial(N.astype(int), K / N) / N for _, _, K, N in tc] for tc in tabs]; Wb = weights(chans, tabs, Pb)
        cb = cdf_of(Wb); cbl = cdf_of(Wb, e <= CUT)
        null.append(stats.kstest(np.interp(rng.uniform(0, 1, n), cb, e), lambda v: np.interp(v, e, c_all)).statistic)
        null_lo.append(stats.kstest(np.interp(rng.uniform(0, 1, len(lo)), cbl, e), lambda v: np.interp(v, e, c_lo)).statistic)
        dboot.append(rng.choice(obs, n).mean() - float((np.diff(np.r_[0, cb]) * e).sum()))
        tb = np.array([[w.sum() for w in ww] for ww in Wb]); proboot.append(tb[:, 0].sum() / tb.sum())
    null, null_lo, dboot, proboot = map(np.array, (null, null_lo, dboot, proboot))
    cnt = np.array([(q.mbody == c[1]).sum() for c in chans]); chi = stats.chisquare(cnt, Pesc * n)
    npro = int((q.sentido > 0).sum()); fpro_med = npro / n
    # p bicaudal da fracao prograda: binomial da amostra mais incerteza da previsao
    sd = np.sqrt(fpro_med * (1 - fpro_med) / n + proboot.var()); z = (fpro_med - fpro) / sd
    return dict(conjunto=nome, lam=lam, k=k, n=n, KS=float(ks), KS_critico95=float(np.quantile(null, .95)), p_KS=float((1 + (null >= ks).sum()) / (B + 1)),
                KS_ate_0995=float(ks_lo), critico_ate_0995=float(np.quantile(null_lo, .95)), p_ate_0995=float((1 + (null_lo >= ks_lo).sum()) / (B + 1)),
                e_medido=float(obs.mean()), e_previsto=eprev, delta=float(obs.mean() - eprev), delta_ic95=[float(v) for v in np.quantile(dboot, [.025, .975])],
                escapes_medidos=(cnt / n).tolist(), escapes_previstos=Pesc.tolist(), p_escapes=float(chi.pvalue),
                fracao_prograda_medida=fpro_med, fracao_prograda_prevista=float(fpro), p_prograda=float(2 * stats.norm.sf(abs(z))),
                razao_pro_ret_medida=npro / max(n - npro, 1), razao_pro_ret_prevista=float(fpro / (1 - fpro)),
                corridas=int(d.run.nunique()), fugas=int(len(fin)))
def holm(ps):
    o = np.argsort(ps); m = len(ps); ok = np.ones(m, bool)
    for r, i in enumerate(o):
        if ps[i] <= 0.05 / (m - r): ok[i] = False
        else: break
    return ok
if __name__ == '__main__':
    args = [(n, l, k) for n in CONJ for l in (0.3, 0.7) for k in (3, 4)]
    with Pool(2) as pl: res = pl.map(teste, args)
    for r, v in zip(res, holm(np.array([r['p_KS'] for r in res]))): r['formato_passa_holm'] = bool(v)
    for key, out in (('p_ate_0995', 'ate_0995_passa_holm_expl'), ('p_escapes', 'escapes_passa_holm_expl'), ('p_prograda', 'prograda_passa_holm_expl')):
        for r, v in zip(res, holm(np.array([r[key] for r in res]))): r[out] = bool(v)
    json.dump(dict(reamostragens=B, testes=res), open(f'{D}/resultado_rotacao.json', 'w'), indent=1, ensure_ascii=False)
    for r in res:
        print(f"{r['conjunto']} lam={r['lam']} k={r['k']}: n={r['n']} KS {r['KS']:.3f}/{r['KS_critico95']:.3f} p={r['p_KS']:.3f} {'PASSA' if r['formato_passa_holm'] else 'REPROVA'} | "
              f"ate0995 p={r['p_ate_0995']:.3f} | e {r['e_medido']:.3f}/{r['e_previsto']:.3f} delta {r['delta']:+.3f} | "
              f"escapes {np.round(r['escapes_medidos'], 3).tolist()}/{np.round(r['escapes_previstos'], 3).tolist()} p={r['p_escapes']:.3f} | "
              f"pro/ret {r['razao_pro_ret_medida']:.2f}/{r['razao_pro_ret_prevista']:.2f} p={r['p_prograda']:.3f}")
