"""Exploratorio (E61b): condicao inicial de Dandekar et al. 2026 (par circular dos dois mais pesados com a = 5, corpo leve em repouso
a d = 100 do centro de massa do par, fase sorteada), com o nosso integrador e a nossa regua de embaralhamentos.
Uso: python ci_dandekar.py <pasta> [n=12000]"""
import sys, os, csv, time, numpy as np
from multiprocessing import Pool
import rot, sim2r
import run_episodes as RE, run_age as ER
from sim2 import PAIRS
from rodar import KQ
def estado(m, phi):
    ma, mb, ms = m; mB = ma + mb; M = mB + ms; a = 5.0; d = 100.0
    rb = a * np.array([np.cos(phi), np.sin(phi)]); vb = np.sqrt(mB / a) * np.array([-np.sin(phi), np.cos(phi)])   # par circular, sentido anti-horario
    X = np.array([-mb / mB * rb, ma / mB * rb, [d, 0.0]]); V = np.array([-mb / mB * vb, ma / mB * vb, [0.0, 0.0]])
    w = np.array(m)[:, None]; X -= (w * X).sum(0) / M; V -= (w * V).sum(0) / M
    mm = np.array(m); r = lambda i, j: np.linalg.norm(X[i] - X[j])
    E = 0.5 * (mm * (V ** 2).sum(1)).sum() - sum(mm[i] * mm[j] / r(i, j) for i, j in ((0, 1), (0, 2), (1, 2)))
    L = (mm * (X[:, 0] * V[:, 1] - X[:, 1] * V[:, 0])).sum()
    return np.r_[X.ravel(), V.ravel()], E, L
def task(a):
    nome, m, i = a; mm = np.array(m); rng = np.random.default_rng(700_000_000 + 1000_000 * len(nome) + i)
    y0, E, L = estado(m, rng.uniform(0, 2 * np.pi)); tcr = mm.sum() ** 2.5 / (2 * abs(E)) ** 1.5
    out = sim2r.integrate_ar(y0, mm, 1000 * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    sent = int(np.sign(ecc)) if status == 1 else 0; ecc = abs(ecc)
    rows = RE.episodes(rec, mm, E, status, esc, t_end, tcr); ee = ER.exc_ecc(rec, mm, E); q = 0; T = (t_ej if status == 1 else t_end) / tcr
    for r in rows:
        if r['exit'] == 'exc': r['e_exit'] = ee[q] if q < len(ee) else np.nan; q += 1
        else: r['e_exit'] = ecc if status == 1 else np.nan
        r.update(set=nome, run=i, lam=L / np.sqrt(rot.kB_principal(m) / (-2 * E)), L=L, E=E, T=T, n_epis=len(rows), status=int(status), stride=int(stride), dE=dE,
                 sentido=sent if r['exit'] == 'esc' else 0)
    return rows
if __name__ == '__main__':
    OUT = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 12000
    # ordem das massas: par (os dois mais pesados) primeiro, corpo leve por ultimo
    for nome, m in (('5-15-25', (15., 25., 5.)), ('10-15-20', (15., 20., 10.))):
        y0, E, L = estado(m, 0.3); print(nome, 'L/L0 exato = %.4f' % (L / np.sqrt(rot.kB_principal(m) / (-2 * E))), flush=True)
        t0 = time.time()
        with open(f'{OUT}/ci_{nome}.csv', 'w', newline='') as fh, Pool(2) as pl:
            w = csv.DictWriter(fh, fieldnames=KQ, extrasaction='ignore'); w.writeheader()
            for rr in pl.imap_unordered(task, [(nome, m, i) for i in range(N)], chunksize=8):
                for r in rr: w.writerow(r)
        print(nome, 'ok', round(time.time() - t0), flush=True)
