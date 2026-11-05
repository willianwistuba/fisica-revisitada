import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
d = pd.read_csv('b2_rows.csv')
d['combo'] = d.ma.astype(str) + '-' + d.mb.astype(str) + '-' + d.ms.astype(str)
d['lx'] = np.log(d.x); d['lmo'] = np.log(d.m_out / (d.m1 + d.m2)); d['lms'] = np.log(d.ms / (d.ma + d.mb))
d['lk'] = np.log(d.m1 * d.m2 / (d.m1 + d.m2) / (d.ma * d.mb / (d.ma + d.mb)))   # razao das massas reduzidas
d['e2'] = d.e ** 2
SETS = {
 'so energia (x)': ['lx'],
 'x e excentricidade': ['lx', 'e', 'e2'],
 'x, e e massas': ['lx', 'e', 'e2', 'lmo', 'lms', 'D0', 'lk'],
 'x, e, massas e cruzados': ['lx', 'e', 'e2', 'lmo', 'lms', 'D0', 'lk', 'lxD0', 'lxlmo', 'lxe', 'eD0'],
}
d['lxD0'] = d.lx * d.D0; d['lxlmo'] = d.lx * d.lmo; d['lxe'] = d.lx * d.e; d['eD0'] = d.e * d.D0
for br, g in d.groupby('branch'):
    cell = g.groupby(['combo', 'x', 'e', 'body']).bound.agg(['mean', 'size']); cell = cell[cell['size'] >= 15]
    noise = np.mean(cell['mean'] * (1 - cell['mean']) / cell['size']); ceil = 1 - noise / cell['mean'].var()
    print(f'== {br} (teto pelo ruido {ceil:.2f}) ==')
    for lab, cols in SETS.items():
        pred = pd.Series(np.nan, index=g.index)
        for cb in g.combo.unique():
            tr = g.combo != cb
            if g[tr].bound.nunique() < 2: continue
            mdl = LogisticRegression(C=10, max_iter=2000).fit(g.loc[tr, cols], g.loc[tr, 'bound'])
            pred[~tr] = mdl.predict_proba(g.loc[~tr, cols])[:, 1]
        g2 = g.assign(p=pred)
        cp = g2.groupby(['combo', 'x', 'e', 'body']).p.mean().reindex(cell.index)
        r2 = 1 - ((cell['mean'] - cp) ** 2).mean() / cell['mean'].var()
        print(f'  {lab:32s} R2 nas celulas, combinacao deixada de fora: {r2:.2f}  erro medio {np.abs(cell["mean"]-cp).mean():.3f}')
