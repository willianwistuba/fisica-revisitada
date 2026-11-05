"""E34: memoria atraves do caos? Quedas livres com o formato (e) da dupla medido em cada excursao (pela distancia maxima
entre os membros: r_max = a(1+e)) e no escape final. Mesmas condicoes iniciais de run_episodes (sementes novas)."""
import sys, time, csv, numpy as np
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS, initial_conditions, build_state
import run_episodes as RE
def exc_ecc(rec, m, E0):
    t = rec[:, 0]; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]; r = rec[:, 7:10]
    p = np.argmin(Ep, 1); idx = np.arange(len(t)); mi = m[PAIRS[p, 0]]; mj = m[PAIRS[p, 1]]; mk = m[p]; E = Ep[idx, p]
    with np.errstate(divide='ignore', invalid='ignore'):
        a = np.where(E < 0, -mi * mj / (2 * E), np.inf)
    Rt = (2 * (mi + mj) * mk / (mi * mj)) ** (1 / 3) * 2 * a
    cand = (E < 0) & (E0 - E < 0) & (Rk[idx, p] > Rt)
    out = []; k = 0; n = len(t)
    while k < n:
        if cand[k]:
            j = k
            while j + 1 < n and cand[j + 1] and p[j + 1] == p[k]: j += 1
            P = 2 * np.pi * np.sqrt(np.median(a[k:j + 1]) ** 3 / (mi[k] + mj[k]))
            if t[j] - t[k] > P:
                am = np.median(a[k:j + 1]); rr = r[k:j + 1, p[k]]
                out.append(float(np.clip(rr.max() / am - 1, 0, 1)))
            k = j + 1
        else: k += 1
    return out
def task(a):
    mset, i = a; mm = np.array(mset, float)
    rng = np.random.default_rng(9_700_000 + i); x, v = initial_conditions(rng, mm, 'frio'); y0, E, tcr = build_state(x, v, mm, 'frio')
    out = integrate_ar(y0, mm, 1000 * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    rows = RE.episodes(rec, mm, E, status, esc, t_end, tcr); ee = exc_ecc(rec, mm, E)
    s = '-'.join(str(int(v)) for v in mset); T = (t_ej if status == 1 else t_end) / tcr
    q = 0
    for r in rows:
        if r['exit'] == 'exc': r['e_exit'] = ee[q] if q < len(ee) else np.nan; q += 1
        else: r['e_exit'] = ecc if status == 1 else np.nan
        r.update(set=s, run=i, T=T, n_epis=len(rows), status=int(status), stride=int(stride), dE=dE)
    return rows
if __name__ == '__main__':
    N = int(sys.argv[1]); sets = [tuple(float(v) for v in s.split(',')) for s in sys.argv[2].split(';')]; outf = sys.argv[3]
    tasks = [(mset, i) for mset in sets for i in range(N)]; np.random.default_rng(4).shuffle(tasks)
    keys = ['set', 'run', 'T', 'n_epis', 'idx', 't0', 'dur', 'nS', 'nD', 'exit', 'body', 'mbody', 'x', 'exc_dur', 'P_kep', 'e_exit', 'status', 'stride', 'dE']
    t0 = time.time()
    with open(outf, 'w', newline='') as fh, Pool(2) as pl:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore'); w.writeheader()
        for i, rr in enumerate(pl.imap_unordered(task, tasks, chunksize=4)):
            for r in rr: w.writerow(r)
            if i % 2000 == 0: print(i, len(tasks), round(time.time() - t0), flush=True); fh.flush()
    print(outf, 'ok', round(time.time() - t0), flush=True)
