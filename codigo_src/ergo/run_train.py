"""E36: mapa de treino da absortividade para a formula final. 12 combinacoes de massas FORA dos canais de teste
(os 7 canais de abs4 e as quedas livres 1-1-3, 3-3-1, 1-2-3); x de 1,03 a 20; e de 0,05 a 0,97; 200 corridas por celula."""
import sys, time, csv, numpy as np
from multiprocessing import Pool
import run_absorb4 as R
CH = [(1, 1, 1), (1, 1, 0.5), (1, 1, 1.5), (1, 1, 2), (1, 1, 5), (1, 0.5, 0.4), (1, 0.5, 1.5), (1, 0.5, 4), (1, 0.25, 1), (1, 0.25, 3), (1, 0.7, 0.25), (1, 0.6, 0.8), (1, 0.8, 10)]
XS = [1.03, 1.1, 1.3, 1.6, 2.0, 3.0, 5.0, 10.0, 20.0]
ES = [0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.9, 0.97]
keys = ['ma', 'mb', 'ms', 'x', 'e', 'rep', 'ok', 'status', 'esc', 'T', 'nD', 'nDf', 'nexc', 'nS', 'nSf', 'dE']
def job(a):
    r = R.task(a); r['ma'], r['mb'], r['ms'] = a[3]; return r
if __name__ == '__main__':
    N = int(sys.argv[1]); outf = sys.argv[2]
    tasks = [(x, e, 2000 + r, tuple(float(v) for v in m), 20.0) for m in CH for x in XS for e in ES for r in range(N)]
    np.random.default_rng(21).shuffle(tasks); t0 = time.time()
    with open(outf, 'w', newline='') as fh, Pool(2) as p:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore'); w.writeheader()
        for i, r in enumerate(p.imap_unordered(job, tasks, chunksize=16)):
            w.writerow(r)
            if i % 20000 == 0: print(i, len(tasks), round(time.time() - t0), flush=True); fh.flush()
    print(outf, 'ok', len(tasks), round(time.time() - t0), flush=True)
