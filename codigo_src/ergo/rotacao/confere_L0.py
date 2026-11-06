"""Com lam = 0, as tarefas novas devem reproduzir exatamente as corridas antigas (mesmas sementes)."""
import sys, time, numpy as np, pandas as pd
import rot
D = sys.argv[1]
t = time.time(); rot.task_abs((2.0, 0.5, 0, (1., 3., 1.), 20.0, 0.0, 1, 0)); print('aquecimento numba %.1f s' % (time.time() - t))
a = pd.read_csv(f'{D}/pacote_v2/abs4_r20_1,3,1.csv'); a = a[a.ok == 1].sample(12, random_state=3)
bad = 0
for _, r in a.iterrows():
    o = rot.task_abs((r.x, r.e, int(r.rep), (1., 3., 1.), 20.0, 0.0, 1, 0))
    bad += (o['nSf'] != r.nSf) or (o['nS'] != r.nS) or abs(o['T'] - r['T']) > 1e-9
print('absortividade: 12 corridas antigas refeitas, divergencias =', bad)
g = pd.read_csv(f'{D}/escada/age_1-1-2.csv'); runs = sorted(g.run.unique())[:6]; bad = 0
for i in runs:
    rows = rot.task_age(((1., 1., 2.), int(i), 0.0, 9_800_000)); old = g[g.run == i].sort_values('idx')
    bad += (len(rows) != len(old)) or abs(rows[0]['T'] - old['T'].iloc[0]) > 1e-9 or any(r['nS'] != o for r, o in zip(rows, old.nS))
print('queda livre: 6 corridas antigas (1-1-2) refeitas, divergencias =', bad)
