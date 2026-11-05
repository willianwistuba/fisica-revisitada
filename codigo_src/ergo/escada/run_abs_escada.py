"""Absortividade dos dois canais de 1-1-M: grade principal (11 x por 12 e) e borda (11 x por 7 j), 200 corridas por celula."""
import sys, os, time, csv, numpy as np
from multiprocessing import Pool
import run_absorb4 as R
XS = [1.01, 1.03, 1.05, 1.1, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]
ES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92, 0.97, 0.995]
JS = [0.09, 0.07, 0.05, 0.03, 0.02, 0.01, 0.005]
KEYS = ['x', 'e', 'rep', 'ok', 'status', 'esc', 'T', 'nD', 'nDf', 'nexc', 'nS', 'nSf', 'dE']
fmt = lambda m: ','.join('%g' % v for v in m)
if __name__ == '__main__':
    M = float(sys.argv[1]); N = 200
    for ic, m in enumerate([(1., M, 1.), (1., 1., M)]):
        base = 8_000_000 + 1_000_000 * ic
        for tag, grid in (('abs4_r20', [(x, e, base + 10_000 * ie + r) for x in XS for ie, e in enumerate(ES) for r in range(N)]),
                          ('abs5_cauda', [(x, float(np.sqrt(1 - j * j)), base + 500_000 + 10_000 * ij + r) for x in XS for ij, j in enumerate(JS) for r in range(N)])):
            tasks = [(x, e, rep, m, 20.0) for x, e, rep in grid]
            with open(f'{tag}_{fmt(m)}.csv', 'w', newline='') as fh, Pool(2) as pl:
                w = csv.DictWriter(fh, fieldnames=KEYS, extrasaction='ignore'); w.writeheader()
                for r in pl.imap_unordered(R.task, tasks, chunksize=16): w.writerow(r)
