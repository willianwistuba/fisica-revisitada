import numpy as np, pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy import stats
from ergo_theory import weights
x = np.exp(np.linspace(0, np.log(1e3), 1200)); u = (np.arange(1500) + .5) / 1500; e = 1 - (1 - u) ** 2
X, Ee = np.meshgrid(x, e, indexing='ij')
BASE = X ** -2.0 * Ee / np.sqrt(1 - Ee ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
def absorb_grid(fn, thr=2):
    a = pd.read_csv(fn); a = a[a.ok == 1]; a['chaos'] = (a.nscram >= thr).astype(float)
    A = a.pivot_table(index='x', columns='e', values='chaos', aggfunc='mean'); XS = A.index.values; ES = A.columns.values
    Ai = RegularGridInterpolator((np.log(XS), ES), A.values, bounds_error=False, fill_value=None)
    lx = np.clip(np.log(X), np.log(XS[0]), np.log(XS[-1])); ee = np.clip(Ee, ES[0], ES[-1])
    Av = np.clip(Ai(np.c_[lx.ravel(), ee.ravel()]).reshape(X.shape), 0, 1)
    r = np.clip(A.loc[XS[-1]].values / np.maximum(A.loc[XS[-2]].values, 1e-6), 1e-3, 1)
    sl = np.interp(ee, ES, np.log(r) / np.log(XS[-1] / XS[-2]))
    Av = np.where(X > XS[-1], Av * (X / XS[-1]) ** sl, Av)
    return Av, len(a), a.dE.max()
SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)],
        '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)],
        '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
ff = pd.read_csv('ffrand.csv')
for thr in (2, 3):
    print(f'\n=== criterio de caos: nscram >= {thr} ===')
    for name, chans in SETS.items():
        g = ff[(ff.set == name) & (ff.status == 1)]
        res = []
        for (ma, mb, ms), msc, mult in chans:
            Av, n, dEm = absorb_grid(f'abs_{ma},{mb},{ms}.csv'.replace('.0', ''), thr)
            pref = (ma * mb) ** 3 / (ma + mb)
            WA = pref * BASE * Av; W0 = pref * BASE
            _, _, Wsl = weights(ma, mb, ms, alpha=2, crit='AE', nx=500, ne=300)
            res.append((msc, mult, mult * W0.sum(), mult * WA.sum(), mult * Wsl.sum(), WA))
        P0 = np.array([r[2] for r in res]); PA = np.array([r[3] for r in res]); PS = np.array([r[4] for r in res])
        P0 /= P0.sum(); PA /= PA.sum(); PS /= PS.sum()
        print(f'{name}: (n queda livre = {len(g)})')
        for lo in (0, 2, 5):
            q = g[g.nscram >= lo]
            meas = np.array([(q.mesc == r[0]).mean() for r in res])
            se = np.sqrt(meas * (1 - meas) / len(q))
            print(f'   medido nscram>={lo} (n={len(q):5d}): ' + '  '.join(f'm={r[0]}: {v:.3f}±{s:.3f}' for r, v, s in zip(res, meas, se)))
        print('   Stone-Leigh planar       : ' + '  '.join(f'm={r[0]}: {v:.3f}' for r, v in zip(res, PS)))
        print('   fluxo puro (A=1)         : ' + '  '.join(f'm={r[0]}: {v:.3f}' for r, v in zip(res, P0)))
        print('   fluxo x absortividade    : ' + '  '.join(f'm={r[0]}: {v:.3f}' for r, v in zip(res, PA)))
        # excentricidade agregada
        WAt = sum(r[5] * r[1] for r in res); fe = WAt.sum(0); fe /= fe.sum()
        q = g[g.nscram >= 5]
        ks = stats.kstest(q.ecc, lambda v: np.interp(v, e, np.cumsum(fe))).statistic
        print(f'   excentricidade (nscram>=5): <e> medido={q.ecc.mean():.3f} previsto={np.sum(fe*e):.3f} KS={ks:.3f}')
