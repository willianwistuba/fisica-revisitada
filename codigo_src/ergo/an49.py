"""E48: troca de parceiro e evolucao do e do par ao longo das excursoes (age.csv), fugas com nS>=3 no ultimo episodio."""
import numpy as np, pandas as pd
from scipy import stats
d = pd.read_csv('age.csv'); d = d[d.status == 1]
fin = d[d.exit == 'esc']; deep = fin[fin.nS >= 3][['set', 'run', 'body', 'e_exit']].rename(columns={'body': 'b_fim', 'e_exit': 'e_fim'})
g = d.merge(deep, on=['set', 'run']).sort_values(['set', 'run', 'idx'])
rows = []
for (s, r), h in g.groupby(['set', 'run']):
    b = h.body.values; ex = h[h.exit == 'exc']
    trocas = int((b[1:] != b[:-1]).sum())                # mudancas de quem fica de fora = trocas de parceiro
    e_prev = ex.e_exit.values[-1] if len(ex) else np.nan  # e do par na ultima excursao
    mesmo = len(ex) > 0 and ex.body.values[-1] == h.body.values[-1]
    rows.append(dict(set=s, n_exc=len(ex), trocas=trocas, tx=trocas / max(1, len(b) - 1), e_prev=e_prev, e_fim=h.e_fim.values[0], mesmo_par=mesmo,
                     slope=(stats.spearmanr(np.arange(len(ex)), ex.e_exit.values).statistic if len(ex) >= 4 else np.nan)))
R = pd.DataFrame(rows)
for s, h in R.groupby('set'):
    hp = h.dropna(subset=['e_prev'])
    print(f"{s}: n={len(h)} | excursoes medianas {h.n_exc.median():.0f} | taxa de troca de parceiro {h.tx.mean():.3f} | "
          f"e na ultima excursao {hp.e_prev.mean():.3f} -> e final {hp.e_fim.mean():.3f} | mesmo par no fim {h.mesmo_par.mean():.2f} | "
          f"tendencia do e ao longo das excursoes (rho medio) {h.slope.mean():.3f}")
    hm = hp[hp.mesmo_par]; ho = hp[~hp.mesmo_par]
    print(f"     final com o mesmo par da ultima excursao: e final {hm.e_fim.mean():.3f} (n={len(hm)}); com troca: {ho.e_fim.mean():.3f} (n={len(ho)})")
