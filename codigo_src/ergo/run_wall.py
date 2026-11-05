"""E30d: mapa do 'muro' de excentricidade: par (1,1), corpo que chega com massa q; grade fina em e."""
import sys, time, csv, numpy as np
from multiprocessing import Pool
import run_absorb4 as R
QS = [0.15, 0.25, 1/3, 0.4, 0.6, 0.8]
XS = [1.03, 1.1, 1.3, 2.0]
ES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.7, 0.85, 0.95]
N = int(sys.argv[1]); outf = sys.argv[2]
tasks = [(x, e, r, (1.0, 1.0, round(q, 4)), 20.0) for q in QS for x in XS for e in ES for r in range(N)]
np.random.default_rng(5).shuffle(tasks)
rows = []; t0 = time.time()
keys = ['q', 'x', 'e', 'rep', 'ok', 'status', 'esc', 'T', 'nD', 'nDf', 'nexc', 'nS', 'nSf', 'dE']
def job(a):
    r = R.task(a); r['q'] = a[3][2]; return r
if __name__ == '__main__':
    with Pool(2) as p:
        for i, r in enumerate(p.imap_unordered(job, tasks, chunksize=8)):
            rows.append(r)
            if i % 1000 == 0: print(i, len(tasks), round(time.time() - t0), flush=True)
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in rows]
    print(outf, 'ok', round(time.time() - t0), flush=True)
