"""Ajuste da v11 nos dados de treino e conferencia rapida nas quedas livres (sem bootstrap)."""
import json, time, numpy as np, pandas as pd
from scipy import stats
import prova11 as P
C = pd.read_csv('treino_celulas.csv'); t0 = time.time()
p, f = P.fit(C, C.K.values.astype(float), P.P0, 4)
print('ajuste', round(time.time() - t0), 's | nll', round(f, 1), '| parametros', len(p))
json.dump(dict(zip(P.NAMES, map(float, p))), open('formula_v11_referencia.json', 'w'), indent=1)
EX = dict(zip(P.EXTRA, p[-len(P.EXTRA):])); print({k: round(v, 3) for k, v in EX.items()})
pr = P.predict(p); ff = pd.read_csv('quedas_livres.csv')
for name, chans in P.SETS.items():
    q = ff[ff.set == name]; n = len(q); cdf = np.array(pr[name]['cdf']); Ps = np.array(pr[name]['Ps'])
    ks = stats.kstest(q.e_exit.values, lambda v: np.interp(v, P.eg, cdf)).statistic
    obs = np.array([(q.mbody == c[1]).sum() for c in chans])
    print(f'{name}: n={n} KS={ks:.3f} | escapes medidos {np.round(obs/n,3)} formula {np.round(Ps,3)}')
