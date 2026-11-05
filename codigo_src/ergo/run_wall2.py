"""E31: mapa do muro com estatistica suficiente.
Parte A: par (1,1), 12 massas q do corpo que chega, 5 valores de x, 10 de e, 300 corridas por celula.
Parte B: par desigual (1,2), 6 massas, 150 corridas por celula (o muro segue o membro mais leve ou o mais pesado?).
Sementes novas (rep a partir de 1000), independentes de wall.csv."""
import sys, time, csv, numpy as np
from multiprocessing import Pool
import run_absorb4 as R
XS = [1.03, 1.1, 1.3, 2.0, 3.0]
ES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
A = [(1.0, 1.0, round(q, 4)) for q in (0.10, 0.15, 0.20, 0.25, 0.30, 1/3, 0.36, 0.40, 0.45, 0.50, 0.60, 0.80)]
B = [(1.0, 2.0, ms) for ms in (0.2, 0.3, 0.4, 0.5, 0.7, 1.0)]
tasks = [(x, e, 1000 + r, m, 20.0) for m in A for x in XS for e in ES for r in range(300)]
tasks += [(x, e, 1000 + r, m, 20.0) for m in B for x in XS for e in ES for r in range(150)]
np.random.default_rng(11).shuffle(tasks)
keys = ['ma', 'mb', 'ms', 'x', 'e', 'rep', 'ok', 'status', 'esc', 'T', 'nD', 'nDf', 'nexc', 'nS', 'nSf', 'dE']
def job(a):
    r = R.task(a); r['ma'], r['mb'], r['ms'] = a[3]; return r
if __name__ == '__main__':
    outf = sys.argv[1]; t0 = time.time()
    with open(outf, 'w', newline='') as fh, Pool(2) as p:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore'); w.writeheader()
        for i, r in enumerate(p.imap_unordered(job, tasks, chunksize=16)):
            w.writerow(r)
            if i % 20000 == 0: print(i, len(tasks), round(time.time() - t0), flush=True); fh.flush()
    print(outf, 'ok', len(tasks), round(time.time() - t0), flush=True)
