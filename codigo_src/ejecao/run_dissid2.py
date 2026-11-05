"""Primeiro dissidente com massas desiguais (triângulo de Lagrange instável)."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim import integrate_ar, PAIRS
SETS = {'1-1-3': (1, 1, 3), '1-1-10': (1, 1, 10), '3-3-1': (3, 3, 1), '10-10-1': (10, 10, 1)}
TOL = 1e-13
def state(m, eps, rng):
    ang = np.pi / 2 + 2 * np.pi * np.arange(3) / 3
    x = (1 / np.sqrt(3)) * np.c_[np.cos(ang), np.sin(ang)]   # lado 1
    x -= (m[:, None] * x).sum(0) / m.sum()
    Om = np.sqrt(m.sum()); v = Om * np.c_[-x[:, 1], x[:, 0]]
    d = rng.normal(size=(3, 4)) * eps
    x = x + d[:, :2]; v = v + d[:, 2:] * Om
    x -= (m[:, None] * x).sum(0) / m.sum(); v -= (m[:, None] * v).sum(0) / m.sum()
    E = 0.5 * (m * (v ** 2).sum(1)).sum() - sum(m[i] * m[j] / np.linalg.norm(x[i] - x[j]) for i, j in ((0, 1), (0, 2), (1, 2)))
    return np.r_[x.ravel(), v.ravel()], m.sum() ** 2.5 / (2 * abs(E)) ** 1.5, np.linalg.norm(d[:, :2], axis=1)
def sides(Rk, m):
    # R_k^2 = (m_i s_ki^2 + m_j s_kj^2)/M_ij - m_i m_j/M_ij^2 s_ij^2 ; incognitas S[k] = lado oposto a k ao quadrado
    A = np.zeros((3, 3))
    for k in range(3):
        i, j = [q for q in range(3) if q != k]; M = m[i] + m[j]
        A[k, k] = -m[i] * m[j] / M ** 2      # s_ij oposto a k
        A[k, j] += m[i] / M                  # s_ki oposto a j
        A[k, i] += m[j] / M                  # s_kj oposto a i
    S = np.linalg.solve(A, (Rk ** 2).T).T
    return np.sqrt(np.maximum(S, 0))
def task(a):
    name, eps, i = a; m = np.array(SETS[name], float)
    import zlib; rng = np.random.default_rng(zlib.crc32(name.encode()) + 100000 * int(abs(np.log10(eps))) + i)
    y0, tcr, dpos = state(m, eps, rng)
    out = integrate_ar(y0, m, 500 * tcr, 0.01 * tcr, TOL, PAIRS, 1_000_000, 20_000_000)
    status, esc, t_ej, dE, rec = out[0], out[1], out[3], out[4], out[9]
    row = dict(set=name, eps=eps, run=i, status=int(status), esc=int(esc), t_ej=t_ej, tcr=tcr, dE=dE, d0=int(np.argmax(dpos)), light=int(np.argmin(m)) if len(set(m)) == 3 else -1)
    t = rec[:, 0]; Rk = rec[:, 4:7]; s = sides(Rk, m); R0 = Rk[0]
    dev = np.abs(s - 1).max(1)
    for lim in (0.1, 0.3):
        n = np.argmax(dev > lim)
        ok = dev[n] > lim
        row[f't{lim}'] = t[n] if ok else np.nan
        row[f'far{lim}'] = int(np.argmax(Rk[n] / R0)) if ok else -1
        row[f'short{lim}'] = int(np.argmin(s[n])) if ok else -1
    c = s.min(1) < 0.2; n = np.argmax(c)
    row['excl_enc'] = int(np.argmin(s[n])) if c[n] else -1
    row['n_enc'] = int(((c[1:]) & (~c[:-1])).sum() + c[0])
    return row
if __name__ == '__main__':
    N = int(sys.argv[1]); tasks = [(s, e, i) for s in SETS for e in (1e-5, 1e-3) for i in range(N)]
    task(('1-1-3', 1e-3, 0)); rows = []; t0 = time.time()
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=4)):
            rows.append(r)
            if (j + 1) % 400 == 0: print(j + 1, len(tasks), round(time.time() - t0), flush=True)
    with open('dissid2.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
