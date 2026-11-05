"""E15: mapa de memoria da queda livre (Agekyan-Anosova). A=(-0.5,0), B=(0.5,0), C=(x,y), corpos em repouso."""
import sys, os, time, csv
import numpy as np
from multiprocessing import Pool
from sim import integrate_ar, PAIRS, build_state
TOL = 1e-12
def grid(h):
    pts = []
    for x in np.arange(h / 2, 0.5, h):
        for y in np.arange(h / 2, np.sqrt(3) / 2 + 1e-9, h):
            if (x + 0.5) ** 2 + y ** 2 <= 1.0 and np.hypot(x - 0.5, y) >= 0.01:
                pts.append((round(x, 6), round(y, 6)))
    return pts
def task(a):
    x0, y0c, m, tcap = a; m = np.array(m, float)
    x = np.array([[-0.5, 0.0], [0.5, 0.0], [x0, y0c]])
    y0, E, tcr = build_state(x, np.zeros((3, 2)), m, 'frio')
    out = integrate_ar(y0, m, tcap * tcr, 0.01 * tcr, TOL, PAIRS, 400_000, 80_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    T = (t_ej if status == 1 else t_end) / tcr
    EBf = np.nan
    if status == 1:
        i, j = PAIRS[esc]; EBf = (-m[i] * m[j] / (2 * a_b)) / E
    Ep = rec[:, 1:4]; Rk = rec[:, 4:7]
    prod = np.array([m[PAIRS[p, 0]] * m[PAIRS[p, 1]] for p in range(3)])
    with np.errstate(divide='ignore', invalid='ignore'):
        ap = np.where(Ep < 0, -prod / (2 * Ep), np.inf)
    binex = ((Ep < 0) & (Rk > 2 * ap)).any(1)
    nscram = int(((~binex[1:]) & binex[:-1]).sum() + (0 if binex[0] else 1))
    return dict(x=x0, y=y0c, status=int(status), esc=int(esc), T=T, ecc=ecc, EBf=EBf, dE=dE, nscram=nscram, nsteps=int(nsteps))
if __name__ == '__main__':
    h = float(sys.argv[1]); tcap = float(sys.argv[2]); m = tuple(float(v) for v in sys.argv[3].split(',')); outf = sys.argv[4]
    pts = grid(h)
    done = set(); rows = []
    part = outf + '.part'
    if os.path.exists(part):
        import pandas as pd; p0 = pd.read_csv(part); rows = p0.to_dict('records'); done = set(zip(p0.x.round(6), p0.y.round(6)))
    tasks = [(x, y, m, tcap) for (x, y) in pts if (x, y) not in done]
    rng = np.random.default_rng(1); rng.shuffle(tasks)
    print('pontos', len(pts), 'restantes', len(tasks), flush=True)
    task((0.2, 0.3, m, 1.0)); t0 = time.time()
    def dump(fn):
        with open(fn, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=4)):
            rows.append(r)
            if (j + 1) % 1000 == 0:
                print(len(rows), len(pts), round(time.time() - t0), flush=True); dump(part)
    dump(outf); print('ok', round(time.time() - t0), flush=True)
