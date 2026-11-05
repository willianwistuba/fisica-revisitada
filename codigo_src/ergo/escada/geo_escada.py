"""Geometria do ultimo episodio nas fugas com nS >= 3, por degrau (mesmas sementes de run_age.py daqui: 9.800.000 + i)."""
import sys, json, numpy as np, pandas as pd
from multiprocessing import Pool
from scipy import stats
from sim2 import integrate_ar, PAIRS, initial_conditions, build_state
def task(a):
    M, i, t0r, esc_body = a; mm = np.array([1., 1., M])
    rng = np.random.default_rng(9_800_000 + i); x, v = initial_conditions(rng, mm, 'frio'); y0, E0, tcr = build_state(x, v, mm, 'frio')
    o = integrate_ar(y0, mm, 1000 * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, ns, st, rec = o
    t = rec[:, 0]; w = (t >= t0r * tcr) & (t <= t_ej); t, Ep, Rk = t[w], rec[w, 1:4], rec[w, 4:7]
    if len(t) < 5 or esc != esc_body: return None
    dt = np.gradient(t); dt /= dt.sum(); p = np.argmin(Ep, 1); idx = np.arange(len(t)); Eb = Ep[idx, p]
    prod = np.array([mm[PAIRS[q, 0]] * mm[PAIRS[q, 1]] for q in range(3)])
    with np.errstate(divide='ignore', invalid='ignore'): a_ = np.where(Eb < 0, -prod[p] / (2 * Eb), np.inf)
    return M, float(ecc), float((dt * ((Eb < 0) & (Rk[idx, p] > 2 * a_))).sum())
if __name__ == '__main__':
    out = {}
    tasks = []
    for M in (2, 2.5, 2.75, 3.25, 3.5, 4, 5):
        d = pd.read_csv(f'age_1-1-{M:g}.csv'); f = d[(d.exit == 'esc') & (d.status == 1) & (d.nS >= 3)]
        tasks += [(float(M), int(r.run), float(r.t0), int(r.body)) for r in f.itertuples()]
    with Pool(2) as pl: res = [r for r in pl.map(task, tasks, chunksize=8) if r]
    R = pd.DataFrame(res, columns=['M', 'e', 'hier'])
    for M, h in R.groupby('M'):
        r = stats.spearmanr(h.e, h.hier); z = np.arctanh(r.statistic); s = 1 / np.sqrt(len(h) - 3)
        out[f'{M:g}'] = dict(n=len(h), hier_mediana=float(h.hier.median()), rho=float(r.statistic), ic95=[float(np.tanh(z - 1.96 * s)), float(np.tanh(z + 1.96 * s))])
        print(f'{M:g}', out[f'{M:g}'])
    json.dump(out, open('geo_escada.json', 'w'), indent=1)
