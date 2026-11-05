"""FR-TC-08: meia-vida e cauda da distribuição de tempos de vida; excursões longas (voos de Lévy)."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim import integrate_ar, PAIRS, initial_conditions, build_state
SETS = {'1-1-1': (1, 1, 1), '1-1-10': (1, 1, 10), '10-10-1': (10, 10, 1)}
ENS = ['frio', 'virial']; TOL = 1e-12
def task(a):
    name, ens, i, tcap = a; m = np.array(SETS[name], float)
    seed = 3_000_000 + (0 if ens == 'frio' else 1_000_000) + i
    rng = np.random.default_rng(seed); x, v = initial_conditions(rng, m, ens); y0, E, tcr = build_state(x, v, m, ens)
    out = integrate_ar(y0, m, tcap * tcr, 0.01 * tcr, TOL, PAIRS, 400_000, 60_000_000)
    status, esc, t_end, t_ej, dE, rec = out[0], out[1], out[2], out[3], out[4], out[9]
    T = (t_ej if status == 1 else t_end) / tcr
    row = dict(set=name, ens=ens, run=i, status=int(status), esc=int(esc), T=T, dE=dE)
    t = rec[:, 0] / tcr; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]
    mb = np.argmin(Ep, 1); idx = np.arange(len(t))
    Eb = Ep[idx, mb]; a = np.where(Eb < 0, -np.array([m[[q for q in range(3) if q != k]].prod() for k in mb]) / (2 * np.minimum(Eb, -1e-300)), np.inf)
    hier = (Eb < 0) & (Rk[idx, mb] > 5 * a)          # um corpo longe do par mais ligado: excursão
    dt = np.diff(t); h = hier[:-1]
    row['frac_exc'] = float((dt * h).sum() / max(dt.sum(), 1e-300))
    # excursões contínuas
    lens = []; cur = 0.0
    for k in range(len(dt)):
        if h[k]: cur += dt[k]
        elif cur > 0: lens.append(cur); cur = 0.0
    if cur > 0: lens.append(cur)
    row['n_exc'] = len(lens); row['max_exc'] = max(lens) if lens else 0.0
    row['nsteps'] = int(out[7])
    return row
if __name__ == '__main__':
    N = int(sys.argv[1]); tcap = float(sys.argv[2])
    tasks = [(s, e, i, tcap) for s in SETS for e in ENS for i in range(N)]
    rng = np.random.default_rng(0); rng.shuffle(tasks)
    import os, pandas as pd
    done = set()
    if len(sys.argv) > 3 and os.path.exists(sys.argv[3]):
        p0 = pd.read_csv(sys.argv[3]); done = set(zip(p0.set, p0.ens, p0.run)); prev = p0.to_dict('records')
    else: prev = []
    tasks = [t for t in tasks if (t[0], t[1], t[2]) not in done]
    print('restantes', len(tasks), flush=True)
    task(('1-1-1', 'frio', 0, 1.0)); rows = list(prev); t0 = time.time()
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=2)):
            rows.append(r)
            if (j + 1) % 500 == 0:
                print(len(rows), len(tasks) + len(prev), round(time.time() - t0), flush=True)
                with open('vida_partial.csv', 'w', newline='') as fh:
                    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(x) for x in rows]
    with open('vida.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
