import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
exec(open('an_b2c.py').read().split("SETS = {")[0])
d['lxD0'] = d.lx * d.D0
SETS = {'x + D0': ['lx', 'D0'], 'x + massa de quem sai': ['lx', 'lmo'], 'x + D0 + massa de quem sai': ['lx', 'D0', 'lmo'],
        'x + D0 + massa de quem sai + e': ['lx', 'D0', 'lmo', 'e'], 'x + massas reduzidas + massa de quem sai': ['lx', 'lk', 'lmo'], 'x + D0 + lms': ['lx', 'D0', 'lms']}
for br, g in d.groupby('branch'):
    cell = g.groupby(['combo', 'x', 'e', 'body']).bound.agg(['mean', 'size']); cell = cell[cell['size'] >= 15]
    print('==', br, '==')
    for lab, cols in SETS.items():
        pred = pd.Series(np.nan, index=g.index)
        for cb in g.combo.unique():
            tr = g.combo != cb
            mdl = LogisticRegression(C=10, max_iter=2000).fit(g.loc[tr, cols], g.loc[tr, 'bound']); pred[~tr] = mdl.predict_proba(g.loc[~tr, cols])[:, 1]
        cp = g.assign(p=pred).groupby(['combo', 'x', 'e', 'body']).p.mean().reindex(cell.index)
        full = LogisticRegression(C=10, max_iter=2000).fit(g[cols], g.bound)
        print(f'  {lab:42s} R2 fora {1-((cell["mean"]-cp)**2).mean()/cell["mean"].var():.2f} | coef ' + ' '.join(f'{c}={v:+.2f}' for c, v in zip(cols, full.coef_[0])) + f' const={full.intercept_[0]:+.2f}')
