import sys, numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f = sys.argv[1]; h = float(sys.argv[2]); C = int(sys.argv[3]) if len(sys.argv) > 3 else 10
d = pd.read_csv(f); d['i'] = np.rint(d.x / h - 0.5).astype(int); d['j'] = np.rint(d.y / h - 0.5).astype(int)
d['ci'] = d.i // C; d['cj'] = d.j // C
s = d[(d.status == 1)]
# memoria local por celula, separando por embaralhamentos
for lo in (0, 2, 5, 10):
    q = s[s.nscram >= lo]
    g = q.groupby(['ci', 'cj'])
    rows = []
    for k, c in g:
        if len(c) < 20: continue
        cnt = np.bincount(c.esc, minlength=3); n = cnt.sum(); p0 = np.bincount(q.esc, minlength=3) / len(q)
        chi = ((cnt - n * p0) ** 2 / (n * p0)).sum()
        rows.append((n, chi, c.ecc.mean(), c.ecc.var(ddof=1)))
    r = np.array(rows); n = r[:, 0]
    chi_tot = r[:, 1].sum(); dof = 2 * len(r)
    # ecc: ANOVA
    F, pF = stats.f_oneway(*[c.ecc.values for k, c in g if len(c) >= 20])
    print(f'nscram>={lo:2d} celulas={len(r)} n={int(n.sum())}  quem sai: chi2/dof={chi_tot/dof:.2f} (p={stats.chi2.sf(chi_tot,dof):.1e})  ecc: F={F:.2f} (p={pF:.1e})')
# figura
fig, ax = plt.subplots(1, 3, figsize=(18, 7))
cm = {0: '#d7263d', 1: '#1b998b', 2: '#2e294e', -1: '#cccccc'}
col = [cm[e] if st == 1 else cm[-1] for e, st in zip(d.esc, d.status)]
ax[0].scatter(d.x, d.y, c=col, s=1.2, marker='s', lw=0); ax[0].set_title('quem sai (A vermelho, B verde, C roxo)')
sc = ax[1].scatter(d.x, d.y, c=np.log10(d['T']), s=1.2, marker='s', lw=0, cmap='viridis'); plt.colorbar(sc, ax=ax[1]); ax[1].set_title('log10 vida (t_cr)')
sc = ax[2].scatter(d.x, d.y, c=np.minimum(d.nscram, 30), s=1.2, marker='s', lw=0, cmap='magma'); plt.colorbar(sc, ax=ax[2]); ax[2].set_title('embaralhamentos')
for a in ax: a.set_aspect('equal'); a.set_xlim(0, .5); a.set_ylim(0, .87)
plt.tight_layout(); plt.savefig(f.replace('.csv', '').replace('.part', '') + '_map.png', dpi=110)
