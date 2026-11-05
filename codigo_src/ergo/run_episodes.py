"""Teste das equacoes de evolucao estatistica de Kol (2021, eq. 2.35).
Cada corrida de queda livre e dividida em episodios: fases caoticas separadas por excursoes
(terceiro corpo ligado, alem do raio de mare 2a(2 m_bin m3/(m1 m2))^(1/3), por mais de um periodo do binario).
Para cada episodio caotico registramos duracao, embaralhamentos, configuracoes democraticas e como ele termina
(excursao de qual corpo, com que energia, ou escape final)."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS, initial_conditions, build_state
def episodes(rec, m, E0, status, esc, t_end, tcr):
    t = rec[:, 0]; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]; r = rec[:, 7:10]
    RH = 3 * r.min(1) ** 2 / (r ** 2).sum(1); up = RH > 0.33
    dem = np.where(up[:-1] & ~up[1:])[0] + 1
    prod = np.array([m[PAIRS[q, 0]] * m[PAIRS[q, 1]] for q in range(3)])
    with np.errstate(divide='ignore', invalid='ignore'):
        apq = np.where(Ep < 0, -prod / (2 * Ep), np.inf)
    binex = ((Ep < 0) & (Rk > 2 * apq)).any(1)
    scr = np.where(binex[:-1] & ~binex[1:])[0] + 1
    if not binex[0]: scr = np.r_[0, scr]
    p = np.argmin(Ep, 1); idx = np.arange(len(t))
    mi = m[PAIRS[p, 0]]; mj = m[PAIRS[p, 1]]; mk = m[p]
    E = Ep[idx, p]
    with np.errstate(divide='ignore', invalid='ignore'):
        a = np.where(E < 0, -mi * mj / (2 * E), np.inf)
    Rt = (2 * (mi + mj) * mk / (mi * mj)) ** (1 / 3) * 2 * a
    cand = (E < 0) & (E0 - E < 0) & (Rk[idx, p] > Rt)
    exc = []; k = 0; n = len(t)
    while k < n:
        if cand[k]:
            j = k
            while j + 1 < n and cand[j + 1] and p[j + 1] == p[k]: j += 1
            P = 2 * np.pi * np.sqrt(np.median(a[k:j + 1]) ** 3 / (mi[k] + mj[k]))
            if t[j] - t[k] > P: exc.append((k, j))
            k = j + 1
        else: k += 1
    rows = []; s0 = 0
    for q, kj in enumerate(exc + [None]):
        k, j = kj if kj is not None else (n, n)
        e0 = s0; e1 = (k if q < len(exc) else n)
        nS = int(((scr >= e0) & (scr < e1)).sum()); nD = int(((dem >= e0) & (dem < e1)).sum())
        row = dict(idx=q, t0=t[e0] / tcr if e0 < n else np.nan, dur=((t[e1] if e1 < n else t_end) - t[e0]) / tcr if e0 < n else 0.0, nS=nS, nD=nD)
        if q < len(exc):
            pp = p[k]; EF = E0 - E[k]; MB = mi[k] + mj[k]; Mt = MB + mk[k]
            aF = mk[k] * MB / (2 * abs(EF)); PF = 2 * np.pi * np.sqrt(aF ** 3 / Mt)
            row.update(exit='exc', body=int(pp), mbody=float(m[pp]), x=E[k] / E0, exc_dur=(t[j] - t[k]) / tcr, P_kep=PF / tcr)
            s0 = j + 1
        else:
            row.update(exit='esc' if status == 1 else 'cens', body=int(esc) if status == 1 else -1, mbody=float(m[esc]) if status == 1 else np.nan, x=np.nan, exc_dur=np.nan, P_kep=np.nan)
        rows.append(row)
    return rows
def task(a):
    mset, i = a; mm = np.array(mset, float)
    rng = np.random.default_rng(7_000_000 + i); x, v = initial_conditions(rng, mm, 'frio'); y0, E, tcr = build_state(x, v, mm, 'frio')
    out = integrate_ar(y0, mm, 1000 * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    T = (t_ej if status == 1 else t_end) / tcr
    rows = episodes(rec, mm, E, status, esc, t_end, tcr)
    s = '-'.join(str(int(v)) for v in mset)
    for r in rows: r.update(set=s, run=i, T=T, n_epis=len(rows), ecc=ecc if status == 1 else np.nan, stride=int(stride))
    return rows
if __name__ == '__main__':
    N = int(sys.argv[1]); sets = [tuple(float(v) for v in s.split(',')) for s in sys.argv[2].split(';')]; outf = sys.argv[3]
    tasks = [(mset, i) for mset in sets for i in range(N)]
    task((sets[0], 0)); rows = []; t0 = time.time()
    with Pool(2) as pl:
        for rr in pl.imap_unordered(task, tasks, chunksize=4): rows += rr
    keys = ['set', 'run', 'T', 'n_epis', 'idx', 't0', 'dur', 'nS', 'nD', 'exit', 'body', 'mbody', 'x', 'exc_dur', 'P_kep', 'ecc', 'stride']
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
