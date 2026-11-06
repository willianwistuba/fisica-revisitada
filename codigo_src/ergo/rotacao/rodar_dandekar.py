"""Rodada E61 (PREREGISTRO_DANDEKAR.md): quedas livres e absortividade nos conjuntos e rotacoes de Dandekar et al. (2026).
Uso: python rodar_dandekar.py <pasta_saida> [processos=2]"""
import sys, os, time, csv, numpy as np
from multiprocessing import Pool
import rot
from rodar import XS, ES, JS, KA, KQ, fmt, warm, log
OUT = sys.argv[1]; NP = int(sys.argv[2]) if len(sys.argv) > 2 else 2
os.makedirs(OUT, exist_ok=True)
CONJ = {'10-15-20': (1.0567, [(15., 20., 10.), (10., 20., 15.), (10., 15., 20.)]),
        '5-15-25': (1.0263, [(15., 25., 5.), (5., 25., 15.), (5., 15., 25.)])}
if __name__ == '__main__':
    t0 = time.time()
    with Pool(NP) as pl:
        pl.map(warm, range(NP))
        for ic, (nome, (lam, _)) in enumerate(CONJ.items()):
            f = f'{OUT}/age_{nome}_lam{lam}.csv'
            if os.path.exists(f + '.ok'): continue
            mset = tuple(float(v) for v in nome.split('-')); base = 500_000_000 + 1_000_000 * ic
            with open(f, 'w', newline='') as fh:
                w = csv.DictWriter(fh, fieldnames=KQ, extrasaction='ignore'); w.writeheader()
                for rr in pl.imap_unordered(rot.task_age, [(mset, i, lam, base) for i in range(12_000)], chunksize=8):
                    for r in rr: w.writerow(r)
            open(f + '.ok', 'w').close(); log('queda livre', nome, lam, 'ok', round(time.time() - t0))
        for nome, (lam, chans) in CONJ.items():
            Ltot = lam * np.sqrt(rot.kB_principal([float(v) for v in nome.split('-')]) / 2)
            for m in chans:
                for tag, grid in (('abs4_r20', [(x, e, 10_000 * ie + r) for x in XS for ie, e in enumerate(ES) for r in range(200)]),
                                  ('abs5_cauda', [(x, float(np.sqrt(1 - j * j)), 500_000 + 10_000 * ij + r) for x in XS for ij, j in enumerate(JS) for r in range(200)])):
                    f = f'{OUT}/{tag}_{fmt(m)}_lam{lam}.csv'
                    if os.path.exists(f + '.ok'): continue
                    tasks = [(x, e, rep, m, 20.0, Ltot, s, 500_000_000_000 + (500_000 if s < 0 else 0)) for x, e, rep in grid for s in (1, -1)]
                    with open(f, 'w', newline='') as fh:
                        w = csv.DictWriter(fh, fieldnames=KA, extrasaction='ignore'); w.writeheader()
                        for r in pl.imap_unordered(rot.task_abs, tasks, chunksize=32): w.writerow(r)
                    open(f + '.ok', 'w').close(); log(tag, fmt(m), lam, 'ok', round(time.time() - t0))
    log('fim', round(time.time() - t0))
