import sys, numpy as np, pandas as pd
from scipy import stats
from ergo_theory import weights
f = sys.argv[1]; h = float(sys.argv[2])
d = pd.read_csv(f); d['i'] = np.rint(d.x / h - 0.5).astype(int); d['j'] = np.rint(d.y / h - 0.5).astype(int)
ok = d.status == 1
print('N', len(d), 'escaparam', ok.mean().round(4), 'dE max', d.dE.max())
print('fracao por corpo que escapa (A,B,C):', (np.bincount(d.esc[ok], minlength=3) / ok.sum()).round(4))
# teoria
x, e, W = weights(1, 1, 1, alpha=2, crit='AE', nx=800, ne=400); fe = W.sum(0); cdf_e = np.cumsum(fe) / fe.sum()
Fe = lambda v: np.interp(v, e, cdf_e)
fx = W.sum(1); cdf_x = np.cumsum(fx) / fx.sum(); Fx = lambda v: np.interp(v, x, cdf_x)
def comp(sub, lab):
    ks_e = stats.kstest(sub.ecc, Fe); ks_x = stats.kstest(sub.EBf, Fx)
    print(f'{lab:22s} n={len(sub):6d} <e>={sub.ecc.mean():.3f} KS_e={ks_e.statistic:.3f} KS_EB={ks_x.statistic:.3f} medEB={sub.EBf.median():.2f}')
th_e = (fe / fe.sum() * e).sum(); print('teoria <e>=%.3f' % th_e)
s = d[ok]
comp(s, 'todos')
for lo, hi in ((0, 1), (2, 4), (5, 9), (10, 10**9)):
    comp(s[(s.nscram >= lo) & (s.nscram <= hi)], f'nscram {lo}-{hi}')
def lab(sub): return (np.bincount(sub.esc, minlength=3) / len(sub)).round(3)
for lo, hi in ((0, 1), (2, 4), (5, 9), (10, 10**9)):
    q = s[(s.nscram >= lo) & (s.nscram <= hi)]; print('   A,B,C nscram', lo, hi, lab(q))
for lo, hi in ((0, 3), (3, 10), (10, 30), (30, 1e9)):
    q = s[(s['T'] >= lo) & (s['T'] < hi)]; print('   A,B,C T', lo, hi, lab(q))
    comp(s[(s['T'] >= lo) & (s['T'] < hi)], f'T {lo}-{hi}')
# incerteza: fracao de vizinhos a distancia k*h com desfecho diferente
G = {(a, b): v for a, b, v in zip(d.i, d.j, np.where(ok, d.esc, -1))}
print('\nexpoente de incerteza (desfecho = corpo que escapa)')
fs = []
for k in (1, 2, 4, 8, 16):
    n = dif = 0
    for (a, b), v in G.items():
        for (da, db) in ((k, 0), (0, k)):
            w = G.get((a + da, b + db))
            if w is not None: n += 1; dif += (w != v)
    fs.append(dif / n); print(f'  eps={k*h:.3f}  f={dif/n:.3f}')

hist, edges = np.histogram(s.ecc, bins=10, range=(0, 1)); hist = hist / hist.sum()
th = np.array([np.interp(edges[k+1], e, cdf_e) - np.interp(edges[k], e, cdf_e) for k in range(10)])
th0 = np.array([(np.sqrt(1-edges[k]**2)-np.sqrt(1-edges[k+1]**2)) for k in range(10)])
print('\nbin e   medido  ergodico(AE,a=2)  uniforme-em-l  termico')
for k in range(10): print(f'{edges[k]:.1f}-{edges[k+1]:.1f}  {hist[k]:.3f}  {th[k]:.3f}  {th0[k]:.3f}  {edges[k+1]**2-edges[k]**2:.3f}')
