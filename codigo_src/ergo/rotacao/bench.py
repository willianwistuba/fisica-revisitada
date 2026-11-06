"""Custo medido (apos aquecimento do numba) por corrida, com 2 processos, para lam = 0; 0,3; 0,7."""
import time, json, numpy as np
from multiprocessing import Pool
import rot
XS = [1.05, 1.5, 3.0, 10.0]; ES = [0.25, 0.65, 0.92, 0.995]
def warm(_):
    rot.task_abs((2.0, 0.5, 0, (1., 3., 1.), 20.0, 0.0, 1, 0)); rot.task_age(((1., 1., 3.), 0, 0.0, 1)); return 0
if __name__ == '__main__':
    res = {}
    with Pool(2) as pl:
        pl.map(warm, [0, 1])
        for lam in (0.0, 0.3, 0.7):
            L = lam * np.sqrt(rot.kB_principal((1, 1, 3)) / 2)
            tasks = [(x, e, r, ch, 20.0, L, s, 777_000) for ch in ((1., 3., 1.), (1., 1., 3.)) for s in (1, -1) for x in XS for e in ES for r in range(25)]
            t = time.time(); out = pl.map(rot.task_abs, tasks, chunksize=4); ta = (time.time() - t) / len(tasks)
            A = {f'{ch} s={s:+d}': float(np.mean([o.get('nSf', 0) >= 3 for o, tk in zip(out, tasks) if tk[3] == ch and tk[6] == s])) for ch in ((1., 3., 1.), (1., 1., 3.)) for s in (1, -1)}
            at = [(((1., 1., 3.)), i, lam, 55_000_000) for i in range(2000)]
            t = time.time(); rows = pl.map(rot.task_age, at, chunksize=2); tq = (time.time() - t) / len(at)
            fin = [r for rr in rows for r in rr if r['exit'] == 'esc' and r['status'] == 1]
            res[lam] = dict(seg_por_corrida_abs=ta, seg_por_queda_livre=tq, n_abs=len(tasks), n_queda=len(at),
                            frac_fugas_com_k3=float(np.mean([r['nS'] >= 3 for r in fin])) if fin else None, A_k3_amostra=A)
            print(lam, json.dumps(res[lam]), flush=True)
    json.dump(res, open('bench.json', 'w'), indent=1)
