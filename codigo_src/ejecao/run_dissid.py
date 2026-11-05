"""O primeiro 'dissidente' do triângulo de Lagrange de massas iguais é o corpo ejetado?"""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim import integrate_ar, PAIRS

m = np.ones(3); TOL = 1e-13
def lagrange_state(eps, rng):
    ang = np.pi / 2 + 2 * np.pi * np.arange(3) / 3
    R = 1 / np.sqrt(3)                      # lado 1
    x = R * np.c_[np.cos(ang), np.sin(ang)]
    Om = np.sqrt(3.0)                       # Omega^2 = G M / lado^3
    v = Om * np.c_[-x[:, 1], x[:, 0]]
    d = rng.normal(size=(3, 4)) * eps       # perturbação em posição e velocidade
    x = x + d[:, :2]; v = v + d[:, 2:] * Om
    x -= x.mean(0); v -= v.mean(0)
    E = 0.5 * (v ** 2).sum() - sum(1 / np.linalg.norm(x[i] - x[j]) for i, j in ((0, 1), (0, 2), (1, 2)))
    tcr = 3 ** 2.5 / (2 * abs(E)) ** 1.5
    return np.r_[x.ravel(), v.ravel()], tcr, np.linalg.norm(d[:, :2], axis=1)

def sides(Rk):
    # medianas (massas iguais) -> lados: r_ij^2 = 4/9 (2Ri^2 + 2Rj^2 - Rk^2), r_ij oposto a k
    s = np.zeros_like(Rk)
    for k in range(3):
        i, j = [q for q in range(3) if q != k]
        s[:, k] = np.sqrt(np.maximum(4 / 9 * (2 * Rk[:, i] ** 2 + 2 * Rk[:, j] ** 2 - Rk[:, k] ** 2), 0))
    return s

def task(a):
    eps, i = a
    rng = np.random.default_rng(int(abs(np.log10(eps)) * 1e6) + i)
    y0, tcr, dpos = lagrange_state(eps, rng)
    out = integrate_ar(y0, m, 500 * tcr, 0.01 * tcr, TOL, PAIRS, 1_000_000, 20_000_000)
    status, esc, t_end, t_ej, dE = out[0], out[1], out[2], out[3], out[4]; rec = out[9]
    row = dict(eps=eps, run=i, status=int(status), esc=int(esc), t_ej=t_ej, tcr=tcr, dE=dE, d0=int(np.argmax(dpos)))
    t = rec[:, 0]; Rk = rec[:, 4:7]; s = sides(Rk)
    dev = np.abs(s - 1).max(1)
    for lim in (0.1, 0.3):
        n = np.argmax(dev > lim)
        if dev[n] > lim:
            row[f't{lim}'] = t[n]
            row[f'far{lim}'] = int(np.argmax(Rk[n]))          # mais afastado do par oposto
            row[f'near{lim}'] = int(np.argmin(Rk[n]))
            row[f'short{lim}'] = int(np.argmin(s[n]))          # par mais curto -> excluído = índice k
        else:
            row[f't{lim}'] = np.nan; row[f'far{lim}'] = row[f'near{lim}'] = row[f'short{lim}'] = -1
    n = np.argmax(s.min(1) < 0.2)                               # primeiro encontro próximo
    row['t_enc'] = t[n] if s.min(1)[n] < 0.2 else np.nan
    row['excl_enc'] = int(np.argmin(s[n])) if s.min(1)[n] < 0.2 else -1
    # número de encontros próximos (entradas em s.min<0.2)
    c = s.min(1) < 0.2; row['n_enc'] = int(((c[1:]) & (~c[:-1])).sum() + c[0])
    return row

if __name__ == '__main__':
    N = int(sys.argv[1]); tasks = [(e, i) for e in (1e-8, 1e-5, 1e-3) for i in range(N)]
    task((1e-3, 0)); rows = []; t0 = time.time()
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=4)):
            rows.append(r)
            if (j + 1) % 300 == 0: print(j + 1, len(tasks), round(time.time() - t0), flush=True)
    keys = list(rows[0].keys())
    with open('dissid.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
