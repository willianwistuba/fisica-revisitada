"""Quedas livres aleatorias v2: registra embaralhamentos totais e apos a ultima excursao."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS, initial_conditions, build_state
from segs2 import counts_all
def task(a):
    m, i = a; mm = np.array(m, float)
    rng = np.random.default_rng(7_000_000 + i); x, v = initial_conditions(rng, mm, 'frio'); y0, E, tcr = build_state(x, v, mm, 'frio')
    out = integrate_ar(y0, mm, 1000 * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    nD, nDf, nDl, nx, nS, nSf, nSl = counts_all(rec, mm, E)
    EBf = np.nan
    if status == 1:
        p, q = PAIRS[esc]; EBf = (-mm[p] * mm[q] / (2 * a_b)) / E
    return dict(set='-'.join(str(int(v)) for v in m), run=i, status=int(status), esc=int(esc), mesc=mm[esc] if status == 1 else np.nan, T=(t_ej if status == 1 else t_end) / tcr, ecc=ecc, EBf=EBf, nD=nD, nDl=nDl, nexc=nx, nS=nS, nSl=nSl, dE=dE)
if __name__ == '__main__':
    N = int(sys.argv[1]); sets = [tuple(float(v) for v in s.split(',')) for s in sys.argv[2].split(';')]; outf = sys.argv[3]
    tasks = [(m, i) for m in sets for i in range(N)]
    task((sets[0], 0)); rows = []; t0 = time.time()
    with Pool(2) as p:
        for r in p.imap_unordered(task, tasks, chunksize=4): rows.append(r)
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
