"""E65 (PREREGISTRO_QUENTE.md): 1-1-3 com L = 0 e velocidades sorteadas. Uso: python quente.py <pasta> [n=12000] [conjunto=1-1-3]"""
import sys, os, csv, time, numpy as np
from multiprocessing import Pool
import rot, sim2r
import run_episodes as RE, run_age as ER
from sim2 import PAIRS, initial_conditions
from rodar_tres import KQ
MS = {'1-1-3': ([1., 1., 3.], 1_200_000_000), '1-2-3': ([1., 2., 3.], 1_300_000_000)}
CONJ = sys.argv[3] if len(sys.argv) > 3 else '1-1-3'
def task(i):
    mm = np.array(MS[CONJ][0]); rng = np.random.default_rng(MS[CONJ][1] + i)
    x, v = initial_conditions(rng, mm, 'quente'); x = x - (mm[:, None] * x).sum(0) / mm.sum(); v = v - (mm[:, None] * v).sum(0) / mm.sum()
    I = (mm * (x ** 2).sum(1)).sum(); L = (mm * (x[:, 0] * v[:, 1] - x[:, 1] * v[:, 0])).sum(); v = v - (L / I) * np.c_[-x[:, 1], x[:, 0]]
    W = -sum(mm[a] * mm[b] / np.linalg.norm(x[a] - x[b]) for a, b in ((0, 1), (0, 2), (1, 2))); v = v * np.sqrt(0.5 * abs(W) / (0.5 * (mm * (v ** 2).sum(1)).sum()))
    E = W + 0.5 * (mm * (v ** 2).sum(1)).sum(); tcr = mm.sum() ** 2.5 / (2 * abs(E)) ** 1.5; y0 = np.r_[x.ravel(), v.ravel()]
    out = sim2r.integrate_ar(y0, mm, 1000 * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out; ecc = abs(ecc)
    rows = RE.episodes(rec, mm, E, status, esc, t_end, tcr); ee = ER.exc_ecc(rec, mm, E); q = 0
    for r in rows:
        if r['exit'] == 'exc': r['e_exit'] = ee[q] if q < len(ee) else np.nan; q += 1
        else: r['e_exit'] = ecc if status == 1 else np.nan
        r.update(set=CONJ, run=i, lam=0.0, L=float((mm * (x[:, 0] * v[:, 1] - x[:, 1] * v[:, 0])).sum()), E=E, T=(t_ej if status == 1 else t_end) / tcr,
                 n_epis=len(rows), status=int(status), stride=int(stride), dE=dE, sentido=0)
    return rows
if __name__ == '__main__':
    OUT = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 12000; t0 = time.time()
    with open(f'{OUT}/age_{CONJ}_lam0.0.csv', 'w', newline='') as fh, Pool(2) as pl:
        w = csv.DictWriter(fh, fieldnames=KQ, extrasaction='ignore'); w.writeheader()
        for rr in pl.imap_unordered(task, range(N), chunksize=8):
            for r in rr: w.writerow(r)
    print('fim', round(time.time() - t0), 's', flush=True)
