"""Passo 1: absortividade na borda e > 0,995, em grade de j = sqrt(1 - e^2), nos 7 canais das quedas livres.
Mesmo metodo das celulas abs4 (lancamento a 20 semieixos, run_absorb4.task). Sementes: rep = 2.000.000 + 10.000 x (indice de j) + r,
esquema dos arquivos publicados; run_absorb4 usa int(e*1000) na semente, e os quatro menores j dariam e*1000 = 999.
Uso: python run_cauda.py [corridas_por_celula=200] [processos=todos]"""
import sys, os, time, csv, numpy as np
from multiprocessing import Pool
import run_absorb4 as R
XS = [1.01, 1.03, 1.05, 1.1, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]
JS = [0.09, 0.07, 0.05, 0.03, 0.02, 0.01, 0.005]                    # e de 0,9959 a 0,99999
CHANNELS = [(1., 3., 1.), (1., 1., 3.), (3., 3., 1.), (3., 1., 3.), (2., 3., 1.), (1., 3., 2.), (1., 2., 3.)]
KEYS = ['x', 'e', 'rep', 'ok', 'status', 'esc', 'T', 'nD', 'nDf', 'nexc', 'nS', 'nSf', 'dE']
if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    P = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count()
    R.task((2.0, 0.5, 1, (1., 3., 1.), 20.0))                         # aquece o compilador
    for m in CHANNELS:
        tasks = [(x, float(np.sqrt(1 - j * j)), 2_000_000 + 10_000 * ij + r, m, 20.0) for x in XS for ij, j in enumerate(JS) for r in range(N)]
        fn = 'abs5_cauda_%d,%d,%d.csv' % tuple(int(v) for v in m); t0 = time.time()
        with open(fn, 'w', newline='') as fh, Pool(P) as pl:
            w = csv.DictWriter(fh, fieldnames=KEYS, extrasaction='ignore'); w.writeheader()
            for r in pl.imap_unordered(R.task, tasks, chunksize=8): w.writerow(r)
        print(fn, len(tasks), 'corridas', round(time.time() - t0), 's', flush=True)
