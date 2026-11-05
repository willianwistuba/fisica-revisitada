"""E32: primeira passagem no regime de corpo leve (ramo troca/passagem e se o corpo que sai fica ligado).
Pares (1,1) e (1,2); a razao exata 1/3 do par (1,1) fica de FORA de proposito (e o canal 3,3,1 do teste)."""
import sys, time, csv, numpy as np
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS
from run_absorb4 import state
from run_onepass import first_exit
E0 = -1.0
CH = [(1.0, 1.0, q) for q in (0.15, 0.25, 0.30, 0.36, 0.40, 0.50, 0.60)] + [(1.0, 2.0, ms) for ms in (0.3, 0.4, 0.5, 0.7)]
XS = [1.05, 1.2, 1.5, 2.0, 3.0, 5.0]; ES = [0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95]
def task(a):
    x, e, m, r = a; mm = np.array(m, float)
    rng = np.random.default_rng(50_000_000 + int(x * 1000) * 1000 + int(e * 100) * 10 + r * 7919 + int(m[2] * 1000) * 13 + int(m[1] * 100))
    y0 = state(x, e, m, rng, 20.0)
    base = dict(x=x, e=e, ma=m[0], mb=m[1], ms=m[2])
    if y0 is None: return dict(base, ok=0)
    M = mm.sum(); tcr = M ** 2.5 / (2 * abs(E0)) ** 1.5
    out = integrate_ar(y0, mm, 30 * tcr, 0.01 * tcr, 1e-12, PAIRS, 200_000, 20_000_000)
    fe = first_exit(out[9], mm)
    row = dict(base, ok=1 if fe else 2)
    if fe: row.update(fe)
    return row
if __name__ == '__main__':
    N = int(sys.argv[1]); outf = sys.argv[2]
    tasks = [(x, e, m, r) for m in CH for x in XS for e in ES for r in range(N)]
    np.random.default_rng(7).shuffle(tasks); t0 = time.time()
    keys = ['ma', 'mb', 'ms', 'x', 'e', 'ok', 'xnew', 'body', 'bound', 'nS1', 't1']
    with open(outf, 'w', newline='') as fh, Pool(2) as p:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore'); w.writeheader()
        for i, r in enumerate(p.imap_unordered(task, tasks, chunksize=16)):
            w.writerow(r)
            if i % 10000 == 0: print(i, len(tasks), round(time.time() - t0), flush=True); fh.flush()
    print(outf, 'ok', len(tasks), round(time.time() - t0), flush=True)
