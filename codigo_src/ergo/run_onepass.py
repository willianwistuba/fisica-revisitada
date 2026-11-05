"""E24: o que acontece na primeira passagem. Registra a energia do par mais ligado no instante da primeira saida
(inicio da primeira excursao ou deteccao do escape), o tipo de saida e os embaralhamentos ate ela."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS
from run_absorb4 import state
E0 = -1.0
def first_exit(rec, m):
    t = rec[:, 0]; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]
    prod = np.array([m[PAIRS[q, 0]] * m[PAIRS[q, 1]] for q in range(3)])
    with np.errstate(divide='ignore', invalid='ignore'):
        apq = np.where(Ep < 0, -prod / (2 * Ep), np.inf)
    binex = ((Ep < 0) & (Rk > 2 * apq)).any(1)
    scr = np.where(binex[:-1] & ~binex[1:])[0] + 1
    if len(scr) == 0: return None
    k0 = scr[0]
    p = np.argmin(Ep, 1); idx = np.arange(len(t))
    mi = m[PAIRS[p, 0]]; mj = m[PAIRS[p, 1]]; mk = m[p]; E = Ep[idx, p]
    with np.errstate(divide='ignore', invalid='ignore'):
        a = np.where(E < 0, -mi * mj / (2 * E), np.inf)
    Rt = (2 * (mi + mj) * mk / (mi * mj)) ** (1 / 3) * 2 * a
    sep = (E < 0) & (Rk[idx, p] > Rt)
    after = np.where(sep & (idx > k0))[0]
    # primeira separacao que dura: tercero alem do raio de mare por mais de um periodo, ou ate o fim
    for k in after:
        j = k
        while j + 1 < len(t) and sep[j + 1] and p[j + 1] == p[k]: j += 1
        P = 2 * np.pi * np.sqrt(a[k] ** 3 / (mi[k] + mj[k]))
        if t[j] - t[k] > P or j == len(t) - 1:
            nS = int(((scr >= k0) & (scr < k)).sum())
            return dict(xnew=E[k] / E0, body=int(p[k]), bound=bool(E0 - E[k] < 0), nS1=nS, t1=t[k])
    return None
def task(a):
    x, e, m, r = a; mm = np.array(m, float)
    rng = np.random.default_rng(40_000_000 + int(x * 1000) * 1000 + int(e * 100) * 10 + r * 7919 + int(sum(v * 10 ** i for i, v in enumerate(m))))
    y0 = state(x, e, m, rng, 20.0)
    if y0 is None: return dict(x=x, e=e, ch=','.join(str(int(v)) for v in m), ok=0)
    M = mm.sum(); tcr = M ** 2.5 / (2 * abs(E0)) ** 1.5
    out = integrate_ar(y0, mm, 30 * tcr, 0.01 * tcr, 1e-12, PAIRS, 200_000, 20_000_000)
    fe = first_exit(out[9], mm)
    row = dict(x=x, e=e, ch=','.join(str(int(v)) for v in m), ok=1 if fe else 2)
    if fe: row.update(fe)
    return row
if __name__ == '__main__':
    N = int(sys.argv[1]); outf = sys.argv[2]
    CH = [(1, 1, 1), (1, 3, 1), (1, 1, 3), (3, 3, 1), (3, 1, 3), (2, 3, 1), (1, 3, 2), (1, 2, 3)]
    XS = [1.05, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0]; ES = [0.15, 0.5, 0.85]
    tasks = [(x, e, m, r) for m in CH for x in XS for e in ES for r in range(N)]
    np.random.default_rng(3).shuffle(tasks)
    task(tasks[0]); rows = []; t0 = time.time()
    with Pool(2) as p:
        for r in p.imap_unordered(task, tasks, chunksize=8): rows.append(r)
    keys = ['x', 'e', 'ch', 'ok', 'xnew', 'body', 'bound', 'nS1', 't1']
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore'); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
