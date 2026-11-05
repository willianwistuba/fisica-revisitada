"""E25: regra de massas. Par (M, m) com M = 1 e m = q, corpo que chega com massa M = 1.
Registra quem sai na primeira saida (e se sai ligado) e quem escapa no fim."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS
from run_absorb4 import state
from run_onepass import first_exit
E0 = -1.0
def task(a):
    q, x, e, r = a; m = (1.0, q, 1.0); mm = np.array(m)
    rng = np.random.default_rng(50_000_000 + int(q * 1000) * 100000 + int(x * 100) * 100 + int(e * 100) + r * 7919)
    y0 = state(x, e, m, rng, 20.0)
    if y0 is None: return dict(q=q, x=x, e=e, ok=0)
    M = mm.sum(); tcr = M ** 2.5 / (2 * abs(E0)) ** 1.5
    out = integrate_ar(y0, mm, 300 * tcr, 0.01 * tcr, 1e-12, PAIRS, 300_000, 40_000_000)
    status, esc = out[0], out[1]
    fe = first_exit(out[9], mm)
    row = dict(q=q, x=x, e=e, ok=1, final=int(esc) if status == 1 else -1)
    if fe: row.update(first=fe['body'], bound=int(fe['bound']), nS1=fe['nS1'])
    else: row.update(first=-1, bound=-1, nS1=-1)
    return row
if __name__ == '__main__':
    N = int(sys.argv[1]); outf = sys.argv[2]
    QS = [1.0, 0.8, 0.5, 0.33, 0.2, 0.1]; XS = [1.2, 2.0, 5.0]; ES = [0.15, 0.5, 0.85]
    tasks = [(q, x, e, r) for q in QS for x in XS for e in ES for r in range(N)]
    np.random.default_rng(4).shuffle(tasks)
    task(tasks[0]); rows = []; t0 = time.time()
    with Pool(2) as p:
        for r in p.imap_unordered(task, tasks, chunksize=8): rows.append(r)
    keys = ['q', 'x', 'e', 'ok', 'first', 'bound', 'nS1', 'final']
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
