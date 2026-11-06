"""Exploratorio (E65d): onde, em e, a distribuicao medida se afasta da prevista com L = 0, na queda do repouso e com velocidades sorteadas."""
import sys, numpy as np, pandas as pd
sys.argv = ['x', '/home/claude/quente/dados']
import analise_rot as A
P0 = '/home/claude/estudo/dados/pacote_v2'
def fin(d, k):
    q = d[(d.exit == 'esc') & (d.status == 1) & (d.nS >= k)]; return q.e_exit.values
FAIXAS = [0, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0001]
for nome in ('1-1-3', '1-2-3'):
    chans = A.CONJ[nome]; tabs = [[A.table(A.load(m, 0.0), 3, s) for s in (1, -1)] for m, _, _ in chans]
    W = A.weights(chans, tabs, [[K / N for _, _, K, N in tc] for tc in tabs]); c = A.cdf_of(W)
    prev = np.diff(np.interp(FAIXAS, A.e, c, left=0, right=1))
    fontes = {'repouso': pd.concat([pd.read_csv(f'{P0}/age.csv').query('set == @nome')] + ([pd.read_csv(f'{P0}/age_113_rep.csv')] if nome == '1-1-3' else [])),
              'sorteadas': pd.read_csv(f'/home/claude/quente/dados/age_{nome}_lam0.0.csv')}
    print(f'\n{nome} (k = 3): fração por faixa de e, medida menos prevista, em pontos percentuais')
    print('faixa       ' + ' '.join(f'{a:.2f}-{b:.2f}' for a, b in zip(FAIXAS[:-1], [min(v, 1) for v in FAIXAS[1:]])))
    print('prevista    ' + ' '.join(f'{100*p:9.1f}' for p in prev))
    for lab, d in fontes.items():
        o = fin(d, 3); h = np.histogram(o, FAIXAS)[0] / len(o); se = np.sqrt(h * (1 - h) / len(o))
        print(f'{lab:11s} ' + ' '.join(f'{100*(a-b):+9.1f}' for a, b in zip(h, prev)) + f'   (n = {len(o)}; erro-padrão típico {100*np.median(se):.1f})')
