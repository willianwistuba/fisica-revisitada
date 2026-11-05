"""E34: memoria atraves do caos e a dependencia da idade."""
import numpy as np, pandas as pd
from scipy import stats
d = pd.read_csv('age.csv').sort_values(['set', 'run', 'idx'])
d['e_prev'] = d.groupby(['set', 'run']).e_exit.shift(1)
d['exit_prev'] = d.groupby(['set', 'run']).exit.shift(1)
d['body_prev'] = d.groupby(['set', 'run']).body.shift(1)
d['nS_tot'] = d.groupby(['set', 'run']).nS.transform('sum')
fin = d[(d.exit == 'esc') & (d.status == 1)].copy()
print('corridas por conjunto:', d.groupby('set').run.nunique().to_dict(), '| com escape:', fin.groupby('set').size().to_dict())

def holm(ps):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); ok = np.zeros(m, bool)
    for r, i in enumerate(o):
        if ps[i] <= 0.05 / (m - r): ok[i] = True
        else: break
    return ok

print('\n1) MEMORIA: o e final se parece com o e da dupla na excursao anterior? (por embaralhamentos no ultimo episodio)')
rows = []
for s, g in fin[fin.exit_prev == 'exc'].groupby('set'):
    for lab, lo, hi in (('1', 1, 2), ('2', 2, 3), ('3-4', 3, 5), ('5-9', 5, 10), ('>=10', 10, 10 ** 6)):
        h = g[(g.nS >= lo) & (g.nS < hi)]
        if len(h) < 40: continue
        same = h.body == h.body_prev
        r = stats.spearmanr(h.e_exit, h.e_prev)
        rs = stats.spearmanr(h[same].e_exit, h[same].e_prev) if same.sum() > 30 else None
        rows.append((s, lab, len(h), r.statistic, r.pvalue, same.mean(), rs.statistic if rs else np.nan))
R = pd.DataFrame(rows, columns=['set', 'nS_ultimo', 'n', 'rho', 'p', 'frac_mesmo_par', 'rho_mesmo_par'])
R['sig95_holm'] = holm(R.p.values)
print(R.round(3).to_string(index=False))

print('\n2) IDADE x ULTIMO EPISODIO: a dependencia da idade some quando o ultimo episodio e bem embaralhado?')
ps = []; out = []
for s, g in fin.groupby('set'):
    g = g[g.nS_tot >= 5]
    for cut in (1, 3, 5):
        h = g[g.nS >= cut]; a = h[h.nS_tot < 10].e_exit; b = h[h.nS_tot >= 10].e_exit
        if len(a) > 30 and len(b) > 30:
            r = stats.ks_2samp(a, b); ps.append(r.pvalue)
            out.append((s, cut, len(a), len(b), a.mean(), b.mean(), r.pvalue))
O = pd.DataFrame(out, columns=['set', 'nS_ultimo>=', 'n_jovem', 'n_velho', 'e_jovem', 'e_velho', 'p']); O['sig95_holm'] = holm(O.p.values)
print(O.round(4).to_string(index=False))

print('\n3) quanto do conjunto final vem de ultimos episodios curtos, por idade')
for s, g in fin[fin.nS_tot >= 5].groupby('set'):
    print(f'   {s}: fracao com ultimo episodio de 1-2 embaralhamentos: jovem {(g[g.nS_tot<10].nS<=2).mean():.3f} x velho {(g[g.nS_tot>=10].nS<=2).mean():.3f}')

print('\n4) o e da dupla nas excursoes muda com a ordem da excursao? (1a, 2a, 3a...)')
ex = d[d.exit == 'exc']
for s, g in ex.groupby('set'):
    r = stats.spearmanr(g.idx, g.e_exit); m = g.groupby(np.minimum(g.idx, 5)).e_exit.mean().round(3).to_dict()
    print(f'   {s}: rho(ordem, e)={r.statistic:.3f} p={r.pvalue:.1e} | <e> por ordem {m}')
print('\n5) e na excursao x duracao da excursao (excursoes longas selecionam formato?)')
for s, g in ex.groupby('set'):
    r = stats.spearmanr(g.exc_dur, g.e_exit); print(f'   {s}: rho(duracao, e)={r.statistic:.3f} p={r.pvalue:.1e}')
