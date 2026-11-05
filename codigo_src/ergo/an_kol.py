import pandas as pd, numpy as np
from scipy import stats
d = pd.read_csv('epis.csv')
d['chaos'] = d.nS >= 2
d = d.sort_values(['set', 'run', 'idx'])
d['prev_exc'] = d.groupby(['set', 'run']).exc_dur.shift(1)
d['prev_x'] = d.groupby(['set', 'run']).x.shift(1)
d['prev_body'] = d.groupby(['set', 'run']).mbody.shift(1)
H = {'1-1-1': None, '1-1-3': 3.0, '3-3-1': 3.0, '1-2-3': 1.0}
print('=== T1: a saida de um episodio caotico depende da historia? (episodios caoticos apos absorcao, idx>=1) ===')
for s, g in d[(d.idx >= 1) & d.chaos & (d.exit != 'cens')].groupby('set'):
    g = g.copy(); g['k'] = pd.cut(g.idx, [0, 1, 2, 4, 1000], labels=['1', '2', '3-4', '5+'])
    tab = pd.crosstab(g.k, g.exit); chi = stats.chi2_contingency(tab)
    out = f'{s}: P(escape | saida) por indice: ' + ' '.join(f'{k}:{v:.3f}' for k, v in (tab['esc'] / tab.sum(axis=1)).items()) + f'  (qui2 p={chi.pvalue:.2g})'
    if H[s]:
        tb = pd.crosstab(g.k, g.mbody == H[s]); c2 = stats.chi2_contingency(tb)
        out += f' | P(sai m={H[s]:.0f}): ' + ' '.join(f'{k}:{v:.3f}' for k, v in (tb[True] / tb.sum(axis=1)).items()) + f' (p={c2.pvalue:.2g})'
    q = g[g.prev_exc.notna()]; rho = stats.spearmanr(np.log(q.prev_exc), (q.exit == 'esc').astype(int))
    out += f' | escape x duracao da excursao anterior: rho={rho.statistic:.3f} p={rho.pvalue:.2g}'
    print(out)
print('\n=== T1b: o primeiro episodio (queda livre inicial) e diferente? ===')
for s, g in d[d.chaos & (d.exit != 'cens')].groupby('set'):
    a = g[g.idx == 0]; b = g[g.idx >= 1]
    line = f'{s}: P(escape) 1o={ (a.exit=="esc").mean():.3f} demais={(b.exit=="esc").mean():.3f}'
    if H[s]: line += f'  P(sai m={H[s]:.0f}) 1o={(a.mbody==H[s]).mean():.3f} demais={(b.mbody==H[s]).mean():.3f}'
    print(line)
print('\n=== T2: duracao dos episodios caoticos e exponencial (sem memoria)? ===')
for s, g in d[(d.idx >= 1) & d.chaos & (d.exit != 'cens')].groupby('set'):
    du = g.dur.values; cv = du.std() / du.mean()
    ks = stats.kstest(du - du.min(), 'expon', args=(0, (du - du.min()).mean())).statistic
    by = g.groupby(pd.cut(g.idx, [0, 1, 2, 4, 1000])).dur.mean().round(2).tolist()
    print(f'{s}: media {du.mean():.2f} t_cr, CV {cv:.2f} (exponencial = 1), KS vs exponencial {ks:.3f}, media por indice {by}')
print('\n=== T3: duracao da excursao segue o periodo de Kepler da orbita externa? ===')
e = d[d.exit == 'exc']; sl = np.polyfit(np.log(e.P_kep), np.log(e.exc_dur), 1)
print(f'inclinacao log-log {sl[0]:.3f} (Kepler: 1), razao mediana {np.median(e.exc_dur / e.P_kep):.3f}')
print('\n=== T4: absorcao no retorno (fracao de retornos que viram caos) por energia do par ===')
r = d[(d.idx >= 1) & (d.prev_x.notna())]
for s, g in r.groupby('set'):
    t = g.groupby(pd.cut(g.prev_x, [0, .5, .7, .8, .9, .95, 1.0])).chaos.agg(['mean', 'size'])
    print(s, ' '.join(f'{iv}:{m:.2f}({n})' for iv, (m, n) in t.iterrows()))
print('\n=== T5: quem sai no fim, por numero de episodios e tipo do ultimo episodio ===')
f = d[d.exit == 'esc']
for s, g in f.groupby('set'):
    if not H[s]:
        continue
    g = g.copy(); g['ne'] = pd.cut(g.n_epis, [0, 1, 2, 4, 8, 1000], labels=['1', '2', '3-4', '5-8', '9+'])
    for lab, q in (('ultimo caotico', g[g.chaos]), ('ultimo regular', g[~g.chaos])):
        t = q.groupby('ne', observed=True).mbody.apply(lambda v: (v == H[s]).mean()); n = q.groupby('ne', observed=True).size()
        rho = stats.spearmanr(q['T'], (q.mbody == H[s]).astype(int))
        print(f'{s} m={H[s]:.0f} {lab:15s}: ' + ' '.join(f'{k}:{v:.3f}({n[k]})' for k, v in t.items()) + f'  | vs tempo de vida rho={rho.statistic:.3f} p={rho.pvalue:.2g}')
    q = g[(g.chaos) & (g.n_epis >= 2)]; rho = stats.spearmanr(q['T'], (q.mbody == H[s]).astype(int))
    print(f'   so ultimo caotico e pelo menos 2 episodios: n={len(q)} P={((q.mbody==H[s]).mean()):.3f} rho vs T={rho.statistic:.3f} p={rho.pvalue:.2g}')
