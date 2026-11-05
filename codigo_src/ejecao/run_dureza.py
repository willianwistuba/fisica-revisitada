"""FR-TC-08: o par do primeiro contato nasce duro? Mesmas sementes de run_contato.py."""
import sys, time, csv, zlib
import numpy as np
from multiprocessing import Pool
from sim import integrate_ar, PAIRS, initial_conditions, build_state
from run_dissid2 import state as lagr_state, sides
QS = [2, 3, 10, 30]; FAMS = ['lagr', 'frio', 'virial']; TOL = 1e-13; F = 0.1
def hard(Ep, Rk, Ek, m, k):
    """dureza do par sem k diante de k: -E_par / (1/2 mu_k V_k^2)"""
    i, j = [q for q in range(3) if q != k]; M = m[i] + m[j]; muk = m[k] * M / (m[k] + M)
    K = Ek[k] + m[k] * M / Rk[k]          # 1/2 mu_k V^2
    return -Ep[k] / K
def task(a):
    fam, q, i = a; m = np.array([1.0, 1.0, float(q)])
    seed = zlib.crc32(f'{fam}-{q}'.encode()) + i; rng = np.random.default_rng(seed)
    if fam == 'lagr': y0, tcr, _ = lagr_state(m, 1e-3, rng); E0 = None
    else:
        x, v = initial_conditions(rng, m, fam); y0, E0, tcr = build_state(x, v, m, fam)
    x0 = y0[:6].reshape(3, 2); v0 = y0[6:].reshape(3, 2)
    W0 = -sum(m[a_] * m[b] / np.linalg.norm(x0[a_] - x0[b]) for a_, b in ((0, 1), (0, 2), (1, 2)))
    Etot = W0 + 0.5 * (m * (v0 ** 2).sum(1)).sum()
    rvir = (m[0]*m[1] + m[0]*m[2] + m[1]*m[2]) / abs(W0)
    out = integrate_ar(y0, m, 500 * tcr, 0.01 * tcr, TOL, PAIRS, 1_000_000, 20_000_000)
    status, esc, t_ej, dE, rec = out[0], out[1], out[3], out[4], out[9]
    row = dict(fam=fam, q=q, run=i, status=int(status), esc=int(esc), t_ej=t_ej, tcr=tcr, dE=dE)
    t = rec[:, 0]; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]; Ek = rec[:, 7:10]
    s = sides(Rk, m); hl = np.minimum(s[:, 0], s[:, 1]) / rvir
    n = np.argmax(hl < F)
    if hl[n] < F:
        c = 0 if s[n, 1] < s[n, 0] else 1; o = 1 - c       # c: leve do contato; o: outra leve
        row['c'] = c; row['tc'] = t[n] / tcr
        # par (c, pesada) exclui o corpo o; par (o, pesada) exclui c
        row['bound_c'] = int(Ep[n, o] < 0); row['h_c'] = hard(Ep[n], Rk[n], Ek[n], m, o); row['eb_c'] = -Ep[n, o] / abs(Etot)
        row['bound_o'] = int(Ep[n, c] < 0); row['h_o'] = hard(Ep[n], Rk[n], Ek[n], m, c); row['eb_o'] = -Ep[n, c] / abs(Etot)
        # dureza do par do contato ao fim do encontro: 1 t_cr depois
        n2 = min(int(np.searchsorted(t, t[n] + tcr)), len(t) - 1)
        row['bound_c_1t'] = int(Ep[n2, o] < 0); row['h_c_1t'] = hard(Ep[n2], Rk[n2], Ek[n2], m, o)
        row['mb_1t'] = int(np.argmin(Ep[n2]))              # par mais ligado 1 t_cr depois (exclui este corpo)
    else:
        row['c'] = -1
    return row
if __name__ == '__main__':
    N = int(sys.argv[1]); tasks = [(f, q, i) for f in FAMS for q in QS for i in range(N)]
    task(('lagr', 3, 0)); rows = []; t0 = time.time()
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=8)):
            rows.append(r)
            if (j + 1) % 1000 == 0: print(j + 1, len(tasks), round(time.time() - t0), flush=True)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with open('dureza.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
