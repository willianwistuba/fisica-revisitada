"""Efeito do primeiro contato: com massas (1,1,q), a leve que primeiro se aproxima da pesada fica com ela?"""
import sys, time, csv, zlib
import numpy as np
from multiprocessing import Pool
from sim import integrate_ar, PAIRS, initial_conditions, build_state
from run_dissid2 import state as lagr_state, sides
QS = [2, 3, 10, 30]; FAMS = ['lagr', 'frio', 'virial']; FS = [0.1, 0.2, 0.3]; TOL = 1e-13
def task(a):
    fam, q, i = a; m = np.array([1.0, 1.0, float(q)])
    seed = zlib.crc32(f'{fam}-{q}'.encode()) + i
    rng = np.random.default_rng(seed)
    if fam == 'lagr':
        y0, tcr, _ = lagr_state(m, 1e-3, rng)
    else:
        x, v = initial_conditions(rng, m, fam); y0, E, tcr = build_state(x, v, m, fam)
    x0 = y0[:6].reshape(3, 2)
    W0 = -sum(m[i_] * m[j] / np.linalg.norm(x0[i_] - x0[j]) for i_, j in ((0, 1), (0, 2), (1, 2)))
    rvir = (m[0]*m[1] + m[0]*m[2] + m[1]*m[2]) / abs(W0)
    out = integrate_ar(y0, m, 500 * tcr, 0.01 * tcr, TOL, PAIRS, 1_000_000, 20_000_000)
    status, esc, t_ej, dE, stride, rec = out[0], out[1], out[3], out[4], out[8], out[9]
    row = dict(fam=fam, q=q, run=i, seed=seed, status=int(status), esc=int(esc), t_ej=t_ej, tcr=tcr, dE=dE, stride=int(stride))
    s = sides(rec[:, 4:7], m)          # s[:,0]=d(1,2), s[:,1]=d(0,2), s[:,2]=d(0,1)
    row['nearer'] = 0 if s[0, 1] < s[0, 0] else 1
    hl = np.minimum(s[:, 0], s[:, 1]) / rvir
    ll = s[:, 2] / rvir
    for f in FS:
        n = np.argmax(hl < f)
        if hl[n] < f:
            row[f'c{f}'] = 0 if s[n, 1] < s[n, 0] else 1      # leve do primeiro contato
            row[f'tc{f}'] = rec[n, 0] / tcr
            nl = np.argmax(ll < f); row[f'll_first{f}'] = int(ll[nl] < f and nl < n)
        else:
            row[f'c{f}'] = -1; row[f'tc{f}'] = np.nan; row[f'll_first{f}'] = 0
    return row
if __name__ == '__main__':
    N = int(sys.argv[1]); tasks = [(f, q, i) for f in FAMS for q in QS for i in range(N)]
    task(('lagr', 3, 0)); rows = []; t0 = time.time()
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=8)):
            rows.append(r)
            if (j + 1) % 1000 == 0:
                print(j + 1, len(tasks), round(time.time() - t0), flush=True)
                if (j + 1) % 4000 == 0:
                    with open('contato_partial.csv', 'w', newline='') as fh:
                        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(x) for x in rows]
    with open('contato.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
