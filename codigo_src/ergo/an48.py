"""E47: marcas indiretas da hipotese 4 (sol com dois planetas) nos dados de age.csv."""
import numpy as np, pandas as pd
from scipy import stats
d = pd.read_csv('age.csv'); f = d[(d.exit == 'esc') & (d.status == 1)].copy()
f['dps'] = f.dur / f.nS.clip(lower=1)          # duracao por embaralhamento no ultimo episodio
print('duracao por embaralhamento no ultimo episodio (mediana) por profundidade:')
print(f[f.nS >= 1].assign(k=lambda s: s.nS.clip(upper=6)).pivot_table(index='k', columns='set', values='dps', aggfunc='median').round(3).to_string())
print('\nfugas com nS>=3: correlacao de Spearman entre e final e duracao por embaralhamento; e medio por quartil de dps')
for s, g in f[f.nS >= 3].groupby('set'):
    r = stats.spearmanr(g.e_exit, g.dps); qs = pd.qcut(g.dps, 4, labels=False)
    print(f'  {s}: n={len(g)} rho={r.statistic:.3f} p={r.pvalue:.1e} | e medio por quartil {g.groupby(qs).e_exit.mean().round(3).tolist()}')
print('\nfugas com nS>=3: correlacao entre e final e nS (controle de profundidade)')
for s, g in f[f.nS >= 3].groupby('set'):
    r = stats.spearmanr(g.e_exit, g.nS); print(f'  {s}: rho={r.statistic:.3f} p={r.pvalue:.1e}')
print('\nexcursoes antes da fuga (nS>=3): fracao feita pelo corpo mais leve')
runs = f[f.nS >= 3][['set', 'run']]
ex = d[d.exit == 'exc'].merge(runs, on=['set', 'run'])
for s, g in ex.groupby('set'):
    print(f'  {s}: excursoes {len(g)}, por massa {g.mbody.value_counts(normalize=True).round(3).to_dict()}')
