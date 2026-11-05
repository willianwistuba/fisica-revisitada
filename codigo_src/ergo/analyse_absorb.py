import sys, numpy as np, pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy import stats
from ergo_theory import weights
a = pd.read_csv(sys.argv[1]); ff = pd.read_csv(sys.argv[2]); thr = int(sys.argv[3]) if len(sys.argv) > 3 else 2
a = a[a.ok == 1]
print('runs', len(a), 'dE max', a.dE.max(), '|L| max', a.L.abs().max())
a['chaos'] = ((a.nscram >= thr) if thr > 0 else (a['T'] > 1.0)).astype(float)
A = a.pivot_table(index='x', columns='e', values='chaos', aggfunc='mean')
print('absortividade A(x,e), criterio nscram>=%d' % thr); print(A.round(2).to_string())
XS = A.index.values; ES = A.columns.values
Ai = RegularGridInterpolator((np.log(XS), ES), A.values, bounds_error=False, fill_value=None)
# previsao: fluxo planar ~ x^-2 * e/sqrt(1-e^2) * A
x = np.exp(np.linspace(0, np.log(1e3), 1200)); u = (np.arange(1500) + .5) / 1500; e = 1 - (1 - u) ** 2
X, Ee = np.meshgrid(x, e, indexing='ij')
lx = np.clip(np.log(X), np.log(XS[0]), np.log(XS[-1])); ee = np.clip(Ee, ES[0], ES[-1])
Av = np.clip(Ai(np.c_[lx.ravel(), ee.ravel()]).reshape(X.shape), 0, 1)
# acima de x=10: extrapola A ~ potencia ajustada nos dois ultimos x
r = np.clip(A.loc[XS[-1]].values / np.maximum(A.loc[XS[-2]].values, 1e-6), 1e-3, 1)
slope = np.log(r) / np.log(XS[-1] / XS[-2]); sl = np.interp(ee, ES, slope)
Av = np.where(X > XS[-1], Av * (X / XS[-1]) ** sl, Av)
W0 = X ** -2.0 * Ee / np.sqrt(1 - Ee ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
for lab, W in (('fluxo (Kol, A=1)', W0), ('fluxo x absortividade', W0 * Av)):
    fe = W.sum(0); fe /= fe.sum(); fx = W.sum(1); fx /= fx.sum()
    cdf_e = np.cumsum(fe); cdf_x = np.cumsum(fx)
    for lo in (2, 5):
        s = ff[(ff.status == 1) & (ff.nscram >= lo)]
        ke = stats.kstest(s.ecc, lambda v: np.interp(v, e, cdf_e)).statistic
        kx = stats.kstest(s.EBf, lambda v: np.interp(v, x, cdf_x)).statistic
        print(f'{lab:24s} vs queda livre nscram>={lo}: KS_e={ke:.3f} KS_EB={kx:.3f}  <e> teoria={np.sum(fe*e):.3f} medido={s.ecc.mean():.3f}')
    globals()['FE_' + ('A' if 'abs' in lab else '0')] = (fe, e)
s = ff[(ff.status == 1) & (ff.nscram >= 5)]
h, ed = np.histogram(s.ecc, bins=10, range=(0, 1)); h = h / h.sum()
print('\nbin e   medido  fluxo  fluxo*A  ergodicoSL')
xs_, es_, Wsl = weights(1, 1, 1, alpha=2, crit='AE', nx=800, ne=400); fsl = Wsl.sum(0); csl = np.cumsum(fsl) / fsl.sum()
for k in range(10):
    vals = []
    for fe, ee_ in (FE_0, FE_A):
        c = np.cumsum(fe); vals.append(np.interp(ed[k + 1], ee_, c) - np.interp(ed[k], ee_, c))
    vsl = np.interp(ed[k + 1], es_, csl) - np.interp(ed[k], es_, csl)
    print(f'{ed[k]:.1f}-{ed[k+1]:.1f}  {h[k]:.3f}  {vals[0]:.3f}  {vals[1]:.3f}  {vsl:.3f}')
