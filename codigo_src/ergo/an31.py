"""E31: mapa do muro com intervalos de confianca; reprodutibilidade contra wall.csv; par desigual (1,2)."""
import numpy as np, pandas as pd
from scipy import stats
def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)
w = pd.read_csv('wall2.csv'); w = w[w.ok == 1]
print('corridas validas', len(w), '| nao terminadas (status!=1):', round((w.status != 1).mean(), 3), '| max |dE|', w.dE.abs().max())
w['abs'] = (w.nS >= 2).astype(int)
g = w.groupby(['ma', 'mb', 'ms', 'x', 'e'])['abs'].agg(['sum', 'size']).reset_index()
g['p'] = g['sum'] / g['size']; ci = [wilson(k, n) for k, n in zip(g['sum'], g['size'])]; g['lo'] = [c[0] for c in ci]; g['hi'] = [c[1] for c in ci]

def wall_edge(s, thr=0.02):
    """menor e cuja absortividade e significativamente > 0 (limite inferior do IC > 0) e todas as celulas abaixo com zero absorcoes."""
    s = s.sort_values('e'); es = s.e.values; k = s['sum'].values; lo = s.lo.values
    if k[0] > 0: return 0.0, 0.0
    first = np.argmax(k > 0)
    if k[first] == 0: return np.nan, np.nan
    return es[first - 1], es[first]   # o muro fica entre estes dois valores de e

print('\nA) par (1,1): absortividade por celula (% com IC95); "0/300" = nenhuma absorcao em 300')
A = g[(g.ma == 1) & (g.mb == 1)]
for q, s in A.groupby('ms'):
    print(f'\n q = {q:.3f}')
    print('   x \\ e ' + ' '.join(f'{e:>7.2f}' for e in sorted(s.e.unique())))
    for x, sx in s.groupby('x'):
        cells = ' '.join((f'{100*p:6.1f}%' if k > 0 else f'  0/{n}') for p, k, n in zip(sx.sort_values('e').p, sx.sort_values('e')['sum'], sx.sort_values('e')['size']))
        a, b = wall_edge(sx)
        print(f'   {x:5.2f}  {cells}   muro entre e={a} e {b}')

print('\nlimite superior (95%) para celulas sem nenhuma absorcao: 3/n =', round(3 / 300 * 100, 1), '% com n=300')
zero = A[A['sum'] == 0]; print('celulas do par (1,1) sem absorcao:', len(zero), 'de', len(A), '| corridas nelas:', int(zero['size'].sum()))

print('\nB) reprodutibilidade: wall.csv (40 por celula, sementes antigas) x wall2.csv (300, sementes novas), celulas em comum')
o = pd.read_csv('wall.csv'); o = o[o.ok == 1]; o['abs'] = (o.nS >= 2).astype(int)
go = o.groupby([o.q.round(3), 'x', 'e'])['abs'].agg(['sum', 'size']).reset_index().rename(columns={'q': 'ms'})
A2 = A.assign(ms=A.ms.round(3)); m = go.merge(A2, on=['ms', 'x', 'e'], suffixes=('_old', ''))
chi = []
for r in m.itertuples():
    tab = np.array([[r.sum_old, r.size_old - r.sum_old], [r._6 if False else r.sum, r.size - r.sum]])
    if tab[:, 0].sum() > 0 and tab[:, 1].sum() > 0: chi.append(stats.fisher_exact(tab)[1])
chi = np.array(chi)
print(f'  celulas comparadas {len(m)}; com diferenca significativa a 5%: {(chi < 0.05).sum()} (esperado por acaso: ~{0.05*len(chi):.0f})')
print(f'  correlacao das absortividades: {np.corrcoef(m.sum_old/m.size_old, m.p)[0,1]:.3f}')

print('\nC) par desigual (1,2): onde fica o muro?')
B = g[(g.ma == 1) & (g.mb == 2)]
for ms, s in B.groupby('ms'):
    edges = [wall_edge(sx) for _, sx in s.groupby('x')]
    tag = '; '.join(f'x={x}: {a}-{b}' for x, (a, b) in zip(sorted(s.x.unique()), edges))
    print(f'  ms={ms:.1f} (ms/m_leve={ms/1:.2f}, ms/m_pesada={ms/2:.2f}): {tag}')
g.to_csv('wall2_cells.csv', index=False)
