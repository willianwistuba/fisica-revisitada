"""Custo medido (apos aquecimento) no regime L >= L0 de Dandekar et al. 2026: 10-15-20 (lam 1,0567) e 5-15-25 (lam 1,0263)."""
import time, json, numpy as np
from multiprocessing import Pool
import rot
CONJ = {'10-15-20': (1.0567, [(15., 20., 10.), (10., 20., 15.), (10., 15., 20.)]),
        '5-15-25': (1.0263, [(15., 25., 5.), (5., 25., 15.), (5., 15., 25.)])}
XS = [1.05, 1.5, 3.0, 10.0]; ES = [0.25, 0.65, 0.92, 0.995]
def warm(_):
    rot.task_abs((2.0, 0.5, 0, (1., 3., 1.), 20.0, 0.0, 1, 0)); rot.task_age(((1., 1., 3.), 0, 0.0, 1)); return 0
if __name__ == '__main__':
    res = {}
    with Pool(2) as pl:
        pl.map(warm, [0, 1])
        for nome, (lam, chans) in CONJ.items():
            m = tuple(float(v) for v in nome.split('-')); L = lam * np.sqrt(rot.kB_principal(m) / 2)
            tasks = [(x, e, r, ch, 20.0, L, s, 300_000_000_000) for ch in chans for s in (1, -1) for x in XS for e in ES for r in range(10)]
            t = time.time(); out = pl.map(rot.task_abs, tasks, chunksize=4); ta = (time.time() - t) / len(tasks)
            sem = sum(o['ok'] == 0 for o in out)
            at = [(m, i, lam, 400_000_000) for i in range(600)]
            t = time.time(); rows = pl.map(rot.task_age, at, chunksize=2); tq = (time.time() - t) / len(at)
            runs = [rr for rr in rows if rr]; fin = [rr[-1] for rr in runs if rr[-1]['exit'] == 'esc' and rr[-1]['status'] == 1]
            k3 = [r for r in fin if r['nS'] >= 3]
            res[nome] = dict(lam=lam, s_abs=ta, sem_alcance=int(sem), n_abs=len(tasks), s_queda=tq, n_queda=len(at),
                             nao_terminadas=float(np.mean([rr[0]['status'] != 1 for rr in runs])), frac_k3=len(k3) / len(at),
                             pro_k3=float(np.mean([r['sentido'] > 0 for r in k3])) if k3 else None,
                             escapes_k3={str(b): float(np.mean([r['mbody'] == b for r in k3])) for b in m} if k3 else None)
            print(nome, json.dumps(res[nome]), flush=True)
    json.dump(res, open('bench_dandekar.json', 'w'), indent=1)
