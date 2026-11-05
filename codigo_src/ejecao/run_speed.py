"""FR-TC-06: velocidade de giro do par versus velocidade de chegada do terceiro.
Para cada corrida guarda, em frações f de t_ej, rho_k = v_orb(par sem k) / V_k (velocidade de k
relativa ao CM do par), instantâneo e média temporal de log(rho) em [0, f t_ej]."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim import run_one_ar

FIXED = {'1-1-1': (1, 1, 1), '1-1-3': (1, 1, 3), '1-1-10': (1, 1, 10), '3-3-1': (3, 3, 1), '10-10-1': (10, 10, 1)}
ENS = ['frio', 'virial']; FRACS = [0.25, 0.5, 0.75, 0.9]; TCAP = 2000.0; TOL = 1e-13

def rho_series(rec, m):
    t = rec[:, 0]; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]; Ek = rec[:, 7:10]
    M = m.sum(); out = np.zeros((len(t), 3))
    for k in range(3):
        i, j = [q for q in range(3) if q != k]; mij = m[i] + m[j]
        mu = m[i] * m[j] / mij; muk = m[k] * mij / (m[k] + mij)
        V2 = 2 * (Ek[:, k] + m[k] * mij / Rk[:, k]) / muk
        vo2 = np.where(Ep[:, k] < 0, 2 * np.abs(Ep[:, k]) / mu, 0.0)
        out[:, k] = np.sqrt(vo2 / np.maximum(V2, 1e-300))
    return t, out

def task(a):
    name, ens, i, m = a
    seed = (i if ens == 'frio' else 1_000_000 + i) + (0 if name != 'aleat' else 2_000_000)
    if name == 'aleat':
        m = 10 ** np.random.default_rng(seed + 7).random(3)
    m = np.asarray(m, float)
    o, E, tcr = run_one_ar(m, ens, seed, tcap=TCAP, tol=TOL)
    row = dict(set=name, ens=ens, run=i, seed=seed, m0=m[0], m1=m[1], m2=m[2], status=int(o['status']),
               esc=int(o['esc']), t_ej=o['t_ej'], tcr=tcr, dE=o['dE'])
    ok = o['status'] == 1 and o['dE'] < 1e-4 and o['t_ej'] > 0
    row['ok'] = int(ok)
    if ok:
        t, rho = rho_series(o['rec'], m); tej = o['t_ej']
        lr = np.log(np.maximum(rho, 1e-2))
        for f in FRACS:
            n = max(int(np.searchsorted(t, f * tej, 'right') - 1), 0)
            for k in range(3):
                row[f'ri{f}_{k}'] = rho[n, k]
            sl = slice(0, n + 1); dt = np.diff(t[:n + 2]) if n + 1 < len(t) else np.diff(t[:n + 1])
            w = dt[:n + 1] if len(dt) >= n + 1 else np.r_[dt, 0.0][:n + 1]
            for k in range(3):
                row[f'ra{f}_{k}'] = float((w * lr[sl, k]).sum() / max(w.sum(), 1e-300)) if w.sum() > 0 else lr[0, k]
    return row

if __name__ == '__main__':
    N = int(sys.argv[1]); NR = int(sys.argv[2])
    tasks = [(n, e, i, FIXED[n]) for n in FIXED for e in ENS for i in range(N)] + [('aleat', e, i, None) for e in ENS for i in range(NR)]
    run_one_ar((1, 1, 1), 'frio', 0, tcap=1)
    rows = []; t0 = time.time()
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=4)):
            rows.append(r)
            if (j + 1) % 200 == 0: print(j + 1, len(tasks), round(time.time() - t0), flush=True)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open('speed.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
