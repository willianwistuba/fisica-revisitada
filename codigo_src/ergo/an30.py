"""E30: de onde vem o excesso de excentricidade final no conjunto 3-3-1?"""
import numpy as np, pandas as pd, json
from scipy import stats
import formula_v2 as F2
P = json.load(open('formula_v2.json'))

# grade fina de (x, e) e peso de fluxo planar (sem k_s; k_s e multiplicidade entram por canal)
x = np.exp(np.linspace(0, np.log(1e3), 900)); u = (np.arange(700) + .5) / 700; e = 1 - (1 - u) ** 2
X, E = np.meshgrid(x, e, indexing='ij')
BASE = X ** -2.0 * E / np.sqrt(1 - E ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]

def A_meas_interp(fn, crit='nS'):
    a = pd.read_csv(fn); a = a[a.ok == 1]
    t = a.groupby(['x', 'e'])[crit].apply(lambda v: (v >= 2).mean()).unstack()
    xs = np.array(t.index); es = np.array(t.columns); V = t.values
    # interpolacao bilinear em (ln x, e), constante fora da grade medida
    from scipy.interpolate import RegularGridInterpolator
    f = RegularGridInterpolator((np.log(xs), es), V, bounds_error=False, fill_value=None)
    Lx = np.clip(np.log(X), np.log(xs[0]), np.log(xs[-1])); Ec = np.clip(E, es[0], es[-1])
    return np.clip(f(np.stack([Lx, Ec], -1)), 0, 1), t

if __name__ == '__main__':
    ff = pd.read_csv('ffrand.csv'); f3 = pd.read_csv('ffrand3.csv')
    d = ff.merge(f3[['set', 'run', 'nD', 'nDl', 'nexc', 'nS', 'nSl']], on=['set', 'run'])
    d = d[(d.status == 1) & (d.nscram >= 5)]
    q = d[d.set == '3-3-1']
    print('3-3-1, finais validos (>=5 embaralhamentos):', len(q))
    
    chans = [((3, 3, 1), 1, 1, 'sai a leve (par 3-3)'), ((3, 1, 3), 3, 2, 'sai uma pesada (par 3-1)')]
    print('\n1) excentricidade final por canal')
    print('   canal                       frac.med  <e> med  <e> formula  <e> A medida  KS formula  KS A medida')
    for (ma, mb, ms), mesc, mult, lab in chans:
        qq = q[q.mesc == mesc]
        W_f = BASE * F2.A(X, E, ma, mb, ms, P); fe_f = W_f.sum(0); fe_f /= fe_f.sum()
        Am, _ = A_meas_interp(f'abs4_r20_{ma},{mb},{ms}.csv'); W_m = BASE * Am; fe_m = W_m.sum(0); fe_m /= fe_m.sum()
        ks_f = stats.kstest(qq.ecc, lambda v: np.interp(v, e, np.cumsum(fe_f))).statistic
        ks_m = stats.kstest(qq.ecc, lambda v: np.interp(v, e, np.cumsum(fe_m))).statistic
        print(f'   {lab:27s} {len(qq)/len(q):8.3f} {qq.ecc.mean():8.3f} {np.sum(fe_f*e):12.3f} {np.sum(fe_m*e):13.3f} {ks_f:11.3f} {ks_m:12.3f}')
    
    print('\n2) a absortividade da formula x medida, canal (3,3,1), media sobre x com peso de fluxo, por faixa de e')
    Am, t = A_meas_interp('abs4_r20_3,3,1.csv'); Af = F2.A(X, E, 3, 3, 1, P)
    wx = (X ** -2.0 * np.gradient(x)[:, None])
    for lo, hi in ((0, .3), (.3, .6), (.6, .8), (.8, .9), (.9, .95), (.95, 1)):
        m = (E[0] >= lo) & (E[0] < hi)
        am = (Am[:, m] * wx[:, m]).sum() / wx[:, m].sum(); af = (Af[:, m] * wx[:, m]).sum() / wx[:, m].sum()
        print(f'   e em [{lo:.2f},{hi:.2f}): A medida {am:.3f}  A formula {af:.3f}  razao {af/am:.2f}')
    
    print('\n3) <e> final do canal "sai a leve" pelo numero de embaralhamentos no ultimo episodio (nSl)')
    qq = q[q.mesc == 1]
    for lo, hi in ((0, 1), (1, 2), (2, 4), (4, 8), (8, 10 ** 6)):
        s = qq[(qq.nSl >= lo) & (qq.nSl < hi)]
        if len(s) >= 30: print(f'   nSl em [{lo},{hi}): n={len(s):5d}  <e>={s.ecc.mean():.3f}  frac e>0.95 = {(s.ecc>0.95).mean():.3f}')
    print('   (mesma tabela para massas iguais 1-1-1 como referencia)')
    m = pd.read_csv('ff_111.csv'); print('   colunas ff_111:', list(m.columns))
