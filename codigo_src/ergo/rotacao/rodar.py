"""Rodada do estudo de rotacao (ver PREREGISTRO.md e PREREGISTRO_CONF.md).
Uso: python rodar.py <pasta_saida> [processos=2] [lams=0.3,0.7] [base_queda=70000000] [desloc_abs=0]
E59: valores padrao. E60: lams=0.3,0.7,0.1 base_queda=200000000 desloc_abs=100000000000.
Gera age_<conj>_lam<l>.csv e abs4_r20_<canal>_lam<l>.csv, abs5_cauda_<canal>_lam<l>.csv (coluna s = sentido)."""
import sys, os, time, csv, numpy as np
from multiprocessing import Pool
import rot
OUT = sys.argv[1]; NP = int(sys.argv[2]) if len(sys.argv) > 2 else 2
os.makedirs(OUT, exist_ok=True)
CONJ = {'1-1-3': [(1., 3., 1.), (1., 1., 3.)], '1-2-3': [(2., 3., 1.), (1., 3., 2.), (1., 2., 3.)]}
LAMS = [float(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else [0.3, 0.7]
BQ = int(sys.argv[4]) if len(sys.argv) > 4 else 70_000_000
DA = int(sys.argv[5]) if len(sys.argv) > 5 else 0
XS = [1.01, 1.03, 1.05, 1.1, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]
ES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92, 0.97, 0.995]
JS = [0.09, 0.07, 0.05, 0.03, 0.02, 0.01, 0.005]
KA = ['x', 'e', 's', 'rep', 'ok', 'alcance', 'status', 'esc', 'T', 'nD', 'nDf', 'nexc', 'nS', 'nSf', 'dE']
KQ = ['set', 'lam', 'run', 'L', 'E', 'T', 'n_epis', 'idx', 't0', 'dur', 'nS', 'nD', 'exit', 'body', 'mbody', 'x', 'exc_dur', 'P_kep', 'e_exit', 'sentido', 'status', 'stride', 'dE']
fmt = lambda m: ','.join('%g' % v for v in m)
def warm(_):
    rot.task_abs((2.0, 0.5, 0, (1., 3., 1.), 20.0, 0.0, 1, 0)); rot.task_age(((1., 1., 3.), 0, 0.0, 1)); return 0
def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)
if __name__ == '__main__':
    t0 = time.time()
    with Pool(NP) as pl:
        pl.map(warm, range(NP))
        for il, lam in enumerate(LAMS):                                  # quedas livres
            for ic, (nome, _) in enumerate(CONJ.items()):
                f = f'{OUT}/age_{nome}_lam{lam}.csv'
                if os.path.exists(f + '.ok'): continue
                mset = tuple(float(v) for v in nome.split('-')); base = BQ + 10_000_000 * il + 1_000_000 * ic
                tasks = [(mset, i, lam, base) for i in range(12_000)]
                with open(f, 'w', newline='') as fh:
                    w = csv.DictWriter(fh, fieldnames=KQ, extrasaction='ignore'); w.writeheader()
                    for rr in pl.imap_unordered(rot.task_age, tasks, chunksize=8):
                        for r in rr: w.writerow(r)
                open(f + '.ok', 'w').close(); log('queda livre', nome, lam, 'ok', round(time.time() - t0))
        for lam in LAMS:                                                 # absortividade
            canais = sorted({c for cs in CONJ.values() for c in cs})
            for ich, m in enumerate(canais):
                conj = [n for n, cs in CONJ.items() if m in cs][0]
                Ltot = lam * np.sqrt(rot.kB_principal([float(v) for v in conj.split('-')]) / 2)
                for tag, grid in (('abs4_r20', [(x, e, 10_000 * ie + r) for x in XS for ie, e in enumerate(ES) for r in range(200)]),
                                  ('abs5_cauda', [(x, float(np.sqrt(1 - j * j)), 500_000 + 10_000 * ij + r) for x in XS for ij, j in enumerate(JS) for r in range(200)])):
                    f = f'{OUT}/{tag}_{fmt(m)}_lam{lam}.csv'
                    if os.path.exists(f + '.ok'): continue
                    tasks = [(x, e, rep, m, 20.0, Ltot, s, int(1_000_000 * (1 + round(10 * lam))) + (500_000 if s < 0 else 0) + DA)
                             for x, e, rep in grid for s in (1, -1)]
                    with open(f, 'w', newline='') as fh:
                        w = csv.DictWriter(fh, fieldnames=KA, extrasaction='ignore'); w.writeheader()
                        for r in pl.imap_unordered(rot.task_abs, tasks, chunksize=32): w.writerow(r)
                    open(f + '.ok', 'w').close(); log(tag, fmt(m), lam, 'ok', round(time.time() - t0))
    log('fim', round(time.time() - t0))
