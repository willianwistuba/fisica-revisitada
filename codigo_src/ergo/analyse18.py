import sys, numpy as np, pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy import stats
x = np.exp(np.linspace(0, np.log(1e3), 1000)); u = (np.arange(1200) + .5) / 1200; e = 1 - (1 - u) ** 2
X, Ee = np.meshgrid(x, e, indexing='ij')
BASE = X ** -2.0 * Ee / np.sqrt(1 - Ee ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
def grid(fn, col, k, rf=None):
    a = pd.read_csv(fn); a = a[a.ok == 1]; a['c'] = (a[col] >= k).astype(float)
    T = a.pivot_table(index='x', columns='e', values='c', aggfunc='mean'); XS = T.index.values; ES = T.columns.values
    Ai = RegularGridInterpolator((np.log(XS), ES), T.values, bounds_error=False, fill_value=None)
    lx = np.clip(np.log(X), np.log(XS[0]), np.log(XS[-1])); ee = np.clip(Ee, ES[0], ES[-1])
    Av = np.clip(Ai(np.c_[lx.ravel(), ee.ravel()]).reshape(X.shape), 0, 1)
    r = np.clip(T.values[-1] / np.maximum(T.values[-2], 1e-6), 1e-3, 1)
    sl = np.interp(ee, ES, np.log(r) / np.log(XS[-1] / XS[-2])); Av = np.where(X > XS[-1], Av * (X / XS[-1]) ** sl, Av)
    return Av, T
SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)],
        '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
pre = sys.argv[1] if len(sys.argv) > 1 else 'abs3_'; colA = sys.argv[2] if len(sys.argv) > 2 else 'nfirst'; colM = sys.argv[3] if len(sys.argv) > 3 else 'nlast'
ff = pd.read_csv('ffrand2.csv'); ff = ff[ff.status == 1]
tot_err = {}
for k in (3, 4, 5, 6):
    errs = []
    print(f'\n=== k = {k}: absortividade por {colA}>=k ; medido por {colM}>=k ===')
    # massas iguais
    Av, T = grid(f'{pre}1,1,1.csv', colA, k); W = BASE * Av; fe = W.sum(0); fe /= fe.sum(); fx = W.sum(1); fx /= fx.sum()
    q = ff[(ff.set == '1-1-1') & (ff[colM] >= k)]
    if len(q):
        ke = stats.kstest(q.ecc, lambda v: np.interp(v, e, np.cumsum(fe))).statistic; kx = stats.kstest(q.EBf, lambda v: np.interp(v, x, np.cumsum(fx))).statistic
        print(f'  1-1-1 n={len(q)} <e> med={q.ecc.mean():.3f} prev={np.sum(fe*e):.3f} KS_e={ke:.3f} KS_E={kx:.3f}')
    for name, chans in SETS.items():
        q = ff[(ff.set == name) & (ff[colM] >= k)]
        P = np.array([mult * (ma * mb) ** 3 / (ma + mb) * (BASE * grid(f'{pre}{ma},{mb},{ms}.csv', colA, k)[0]).sum() for (ma, mb, ms), msc, mult in chans]); P /= P.sum()
        meas = np.array([(q.mesc == c[1]).mean() for c in chans]); se = np.sqrt(meas * (1 - meas) / max(len(q), 1))
        errs += list(np.abs(P - meas)[[1]] if len(chans) == 2 else np.abs(P - meas))
        print(f'  {name} n={len(q)}: ' + '  '.join(f'm={c[1]}: med {mv:.3f}±{s:.3f} prev {pv:.3f}' for c, mv, s, pv in zip(chans, meas, se, P)))
    print(f'  erro absoluto medio (5 fracoes): {np.mean(errs)*100:.2f} pontos')
