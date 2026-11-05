"""E29: dependencia da excentricidade nas partes B1 e B2."""
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
import warnings; warnings.filterwarnings('ignore')
d = pd.read_csv('b2_rows.csv'); mg = pd.read_csv('massgrid.csv'); grid = set(zip(mg.mb.round(3), mg.ms.round(3)))
d['ingrid'] = [(ma == 1.0) and ((round(mb, 3), round(ms, 3)) in grid) for ma, mb, ms in zip(d.ma, d.mb, d.ms)]
d['combo'] = d.ma.astype(str) + '-' + d.mb.astype(str) + '-' + d.ms.astype(str)
mB = d.ma + d.mb; M = mB + d.ms; aB = d.ma * d.mb / (2 * d.x); mus = d.ms * mB / M
vinf = np.sqrt(2 * (d.x - 1) / mus); vorb = np.sqrt(mB / aB); vp = np.sqrt(vinf ** 2 + 2 * M / aB)
d['lx'] = np.log(d.x); d['lms'] = np.log(d.ms / mB); d['lmh'] = np.log(d.ms / np.maximum(d.ma, d.mb)); d['e2'] = d.e ** 2
d['lS'] = np.log(vp / vorb); d['lSapo'] = d.lS - 0.5 * np.log((1 - d.e) / (1 + d.e))
for c1, c2 in (('lms', 'e'), ('lx', 'e'), ('lmh', 'e'), ('D0', 'e'), ('lms', 'lSapo'), ('lmh', 'lSapo')): d[c1 + '_' + c2] = d[c1] * d[c2]
d['exch'] = (d.branch == 'troca').astype(int)
def loo(g, y, cols, key):
    cell = g.groupby(['combo', 'x', 'e'])[y].agg(['mean', 'size']); cell = cell[cell['size'] >= 15]
    pred = pd.Series(np.nan, index=g.index)
    for cb in g.combo.unique():
        tr = g.combo != cb
        if g.loc[tr, y].nunique() < 2: continue
        mdl = LogisticRegression(C=10, max_iter=3000).fit(g.loc[tr, cols], g.loc[tr, y]); pred[~tr] = mdl.predict_proba(g.loc[~tr, cols])[:, 1]
    cp = g.assign(p=pred).groupby(['combo', 'x', 'e']).p.mean().reindex(cell.index)
    return 1 - ((cell['mean'] - cp) ** 2).mean() / cell['mean'].var()
G = d[d.ingrid]
print('B1 (troca ou passagem), grade de massas, R2 deixando combinacao de fora:')
for lab, cols in (('so massas', ['lmh']), ('massas + e', ['lmh', 'e', 'e2']), ('massas + e + cruzado', ['lmh', 'e', 'e2', 'lmh_e']), ('massas + velocidade no apoastro', ['lmh', 'lSapo', 'lmh_lSapo']), ('massas + e + x', ['lmh', 'e', 'e2', 'lmh_e', 'lx', 'lx_e'])):
    print(f'  {lab:34s} {loo(G, "exch", cols, "combo"):.2f}')
for br, cols0 in (('passagem', ['lx', 'lms']), ('troca', ['lx', 'D0'])):
    g = G[G.branch == br]
    print(f'B2 {br}, R2 deixando combinacao de fora:')
    extra = {'base': [], '+ e': ['e', 'e2'], '+ e cruzado': ['e', 'e2', 'lx_e', ('lms_e' if br == 'passagem' else 'D0_e')], '+ velocidade no apoastro': (['lSapo', 'lms_lSapo'] if br == 'passagem' else ['lSapo']), '+ e cruzado + velocidade': ['e', 'e2', 'lx_e', ('lms_e' if br == 'passagem' else 'D0_e'), 'lSapo']}
    for lab, ex in extra.items():
        print(f'  {lab:34s} {loo(g, "bound", cols0 + ex, "combo"):.2f}')
