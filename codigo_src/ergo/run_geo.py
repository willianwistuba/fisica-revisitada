"""E49: geometria do ultimo episodio das fugas com nS>=3 (1-1-3 e controle 1-2-3), refazendo as mesmas quedas livres de run_age."""
import sys, time, json, numpy as np, pandas as pd
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS, initial_conditions, build_state
def task(a):
    mset, i, t0r, esc_body = a; mm = np.array(mset, float)
    rng = np.random.default_rng(9_100_000 + i); x, v = initial_conditions(rng, mm, 'frio'); y0, E0, tcr = build_state(x, v, mm, 'frio')
    out = integrate_ar(y0, mm, 1000 * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    t = rec[:, 0]; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]; r = rec[:, 7:10]
    w = (t >= t0r * tcr) & (t <= t_ej); t, Ep, Rk, r = t[w], Ep[w], Rk[w], r[w]
    if len(t) < 5: return None
    dt = np.gradient(t); dt = dt / dt.sum()
    RH = 3 * r.min(1) ** 2 / (r ** 2).sum(1)
    p = np.argmin(Ep, 1); idx = np.arange(len(t)); Eb = Ep[idx, p]
    prod = np.array([mm[PAIRS[q, 0]] * mm[PAIRS[q, 1]] for q in range(3)])
    with np.errstate(divide='ignore', invalid='ignore'):
        a_ = np.where(Eb < 0, -prod[p] / (2 * Eb), np.inf)
    hier = (Eb < 0) & (Rk[idx, p] > 2 * a_)
    heavy = int(np.argmax(mm)); fin = int(esc)               # indice do par = indice do corpo de fora (convencao de PAIRS)
    sw = int((p[1:] != p[:-1]).sum())
    return dict(set='-'.join(str(int(v)) for v in mset), run=i, ok=int(status == 1 and esc == esc_body), e_fim=float(ecc),
                frac_dem=float((dt * (RH > 0.33)).sum()), frac_hier=float((dt * hier).sum()), trocas=sw, dur=float((t[-1] - t[0]) / tcr),
                frac_par_final=float((dt * (p == fin)).sum()), frac_pesado_no_par=float((dt * (p != heavy)).sum()))
if __name__ == '__main__':
    N = int(sys.argv[1]); outf = sys.argv[2]
    d = pd.read_csv('age.csv'); f = d[(d.exit == 'esc') & (d.status == 1) & (d.nS >= 3)]
    tasks = []
    for s in ('1-1-3', '1-2-3'):
        g = f[f.set == s].sample(frac=1, random_state=1).head(N)
        tasks += [(tuple(float(v) for v in s.split('-')), int(r.run), float(r.t0), int(r.body)) for r in g.itertuples()]
    t0 = time.time(); res = []
    with Pool(2) as pl:
        for k, r in enumerate(pl.imap_unordered(task, tasks, chunksize=2)):
            if r: res.append(r)
            if k % 100 == 0: print(k, len(tasks), round(time.time() - t0), flush=True)
    pd.DataFrame(res).to_csv(outf, index=False); print('ok', len(res), round(time.time() - t0))
