"""E51: teste dos gemeos. Para fugas com nS>=3 no ultimo episodio, para no inicio do ultimo episodio, cria 20 copias com
perturbacao relativa de 1e-6 nas posicoes e deixa cada uma terminar. Memoria = correlacao entre o e original e o e dos gemeos."""
import sys, time, numpy as np, pandas as pd
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS, initial_conditions, build_state
import sim2c as S
from segs2 import counts_all
NC = 20; DEL = 1e-6
def task(a):
    mset, i, t0r, e_orig = a; mm = np.array(mset, float)
    rng = np.random.default_rng(9_100_000 + i); x, v = initial_conditions(rng, mm, 'frio'); y0, E0, tcr = build_state(x, v, mm, 'frio')
    y = S.integrate_stop(y0, mm, t0r * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)[-1]
    r = y[:6].reshape(3, 2); scale = np.sqrt(((r[:, None] - r[None]) ** 2).sum(-1).max())
    g = np.random.default_rng(77 + i); out = []
    for c in range(NC):
        yc = y.copy(); dr = g.normal(0, 1, (3, 2)) * DEL * scale; dr -= (mm[:, None] * dr).sum(0) / mm.sum()
        yc[:6] += dr.ravel()
        o = integrate_ar(yc, mm, 1000 * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)
        status, esc, t_end, t_ej, dE, ecc, a_b, ns, st, rec = o
        nSl = counts_all(rec, mm, E0)[6] if status == 1 else -1
        out.append(dict(set='-'.join(str(int(q)) for q in mset), run=i, clone=c, e_orig=e_orig, status=int(status), esc=int(esc), e=float(ecc), nSl=int(nSl)))
    return out
if __name__ == '__main__':
    N = int(sys.argv[1]); outf = sys.argv[2]
    d = pd.read_csv('age.csv'); f = d[(d.exit == 'esc') & (d.status == 1) & (d.nS >= 3)]
    tasks = []
    for s in ('1-1-3', '1-2-3'):
        g = f[f.set == s].sample(frac=1, random_state=2).head(N)
        tasks += [(tuple(float(q) for q in s.split('-')), int(r.run), float(r.t0), float(r.e_exit)) for r in g.itertuples()]
    t0 = time.time(); res = []
    with Pool(2) as pl:
        for k, r in enumerate(pl.imap_unordered(task, tasks, chunksize=2)):
            res += r
            if k % 100 == 0: print(k, len(tasks), round(time.time() - t0), flush=True)
    pd.DataFrame(res).to_csv(outf, index=False); print('ok', len(res), round(time.time() - t0), flush=True)
