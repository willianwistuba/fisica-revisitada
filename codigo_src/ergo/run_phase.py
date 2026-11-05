"""E23: mapa da absortividade em funcao da fase do binario (anomalia media) e da orientacao do periastro na chegada."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS
from run_absorb4 import state
from segs2 import counts_all
E0 = -1.0
class Fixed:
    def __init__(self, vals): self.v = list(vals)
    def uniform(self, a, b): return self.v.pop(0)
def task(a):
    x, e, m, i, j, N = a; mm = np.array(m, float)
    Mm = 2 * np.pi * (i + 0.5) / N; w = 2 * np.pi * (j + 0.5) / N
    y0 = state(x, e, m, Fixed([Mm, w]), 20.0)
    if y0 is None: return dict(i=i, j=j, ok=0)
    M = mm.sum(); tcr = M ** 2.5 / (2 * abs(E0)) ** 1.5
    out = integrate_ar(y0, mm, 300 * tcr, 0.01 * tcr, 1e-12, PAIRS, 200_000, 40_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    nD, nDf, nDl, nx, nS, nSf, nSl = counts_all(rec, mm, E0)
    return dict(i=i, j=j, ok=1, status=int(status), esc=int(esc), nSf=nSf, nS=nS, nexc=nx, T=(t_ej if status == 1 else t_end) / tcr)
if __name__ == '__main__':
    x = float(sys.argv[1]); e = float(sys.argv[2]); m = tuple(float(v) for v in sys.argv[3].split(',')); N = int(sys.argv[4]); outf = sys.argv[5]
    tasks = [(x, e, m, i, j, N) for i in range(N) for j in range(N)]
    task(tasks[0]); rows = []; t0 = time.time()
    with Pool(2) as p:
        for r in p.imap_unordered(task, tasks, chunksize=16): rows.append(r)
    keys = ['i', 'j', 'ok', 'status', 'esc', 'nSf', 'nS', 'nexc', 'T']
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    print(outf, 'ok', round(time.time() - t0), flush=True)
