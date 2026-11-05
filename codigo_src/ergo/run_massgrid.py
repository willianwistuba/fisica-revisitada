"""E26: grade de massas da primeira passagem (espalhamento). Par (1, mb) com mb <= 1, chega ms. Registra quem sai na 1a saida."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS
from run_absorb4 import state
from run_onepass import first_exit
E0 = -1.0
def task(a):
    mb, ms, x, e, r = a; m = (1.0, mb, ms); mm = np.array(m)
    rng = np.random.default_rng(60_000_000 + int(mb * 1000) * 1000003 + int(ms * 1000) * 1009 + int(x * 100) * 31 + int(e * 100) + r * 7919)
    y0 = state(x, e, m, rng, 20.0)
    if y0 is None: return dict(mb=mb, ms=ms, x=x, e=e, ok=0)
    tcr = mm.sum() ** 2.5 / (2 * abs(E0)) ** 1.5
    out = integrate_ar(y0, mm, 30 * tcr, 0.01 * tcr, 1e-12, PAIRS, 200_000, 20_000_000)
    fe = first_exit(out[9], mm)
    if not fe: return dict(mb=mb, ms=ms, x=x, e=e, ok=2)
    return dict(mb=mb, ms=ms, x=x, e=e, ok=1, first=fe['body'], bound=int(fe['bound']), nS1=fe['nS1'], xnew=fe['xnew'])
if __name__ == '__main__':
    N = int(sys.argv[1]); outf = sys.argv[2]
    MB = [0.1, 0.25, 0.5, 1.0]; MS = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 10.0]; XS = [1.2, 2.0, 5.0]; ES = [0.15, 0.5, 0.85]
    tasks = [(mb, ms, x, e, r) for mb in MB for ms in MS for x in XS for e in ES for r in range(N)]
    np.random.default_rng(5).shuffle(tasks)
    task(tasks[0]); rows = []; t0 = time.time()
    with Pool(2) as p:
        for r in p.imap_unordered(task, tasks, chunksize=8): rows.append(r)
    keys = ['mb', 'ms', 'x', 'e', 'ok', 'first', 'bound', 'nS1', 'xnew']
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
