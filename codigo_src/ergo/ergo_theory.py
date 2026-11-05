"""Previsao ergodica PLANAR (L0=0), analoga a Stone & Leigh (2019) eq. 2, refeita em 2D com elementos de Delaunay.
f(E_B, e_B) ~ |dLambda/dE_B| * |dL_h/dE_s| * l_max(R) * dl/de ; G=1."""
import numpy as np
def weights(ma, mb, ms, E0=-1.0, alpha=2.0, crit='AE', nx=1500, ne=800, xmax=1e4):
    mB = ma + mb; M = mB + ms; muB = ma * mb / mB; mus = ms * mB / M
    x = np.exp(np.linspace(0, np.log(xmax), nx))           # x = E_B/E0 >= 1
    u = (np.arange(ne) + 0.5) / ne; e = 1 - (1 - u) ** 2      # malha densa perto de e=1
    de = np.gradient(e)
    X, Ee = np.meshgrid(x, e, indexing='ij')
    EB = X * E0; Es = E0 - EB                                 # Es >= 0
    aB = ma * mb / (2 * np.abs(EB)); Lam = muB * np.sqrt(mB * aB)
    l = Lam * np.sqrt(1 - Ee ** 2)
    with np.errstate(divide='ignore', invalid='ignore'):
        a_s = ms * mB / (2 * Es); Lh = mus * np.sqrt(M * a_s)
        es = np.sqrt(1 + l ** 2 / (mus ** 2 * M * a_s))
        R = alpha * aB * ((1 + Ee) if crit == 'AE' else 1.0)
        q = a_s * (es - 1)
        arg = (R / a_s) ** 2 + 2 * R / a_s + 1 - es ** 2
        lmax = np.sqrt(np.maximum(arg, 0)) - np.arccosh(np.maximum((R / a_s + 1) / es, 1))
        lmax = np.where((q <= R) & (Es > 0), np.maximum(lmax, 0), 0.0)
        w = (Lam / (2 * np.abs(EB))) * (Lh / (2 * np.where(Es > 0, Es, np.inf))) * lmax * Lam * Ee / np.sqrt(1 - Ee ** 2)
    w = np.nan_to_num(w)
    dx = np.gradient(x) * abs(E0)
    W = w * dx[:, None] * de[None, :]
    return x, e, W
def marginals(ma, mb, ms, **k):
    x, e, W = weights(ma, mb, ms, **k)
    return x, e, W.sum(1), W.sum(0), W.sum()
if __name__ == '__main__':
    for crit in ('SE', 'AE'):
        for alpha in (1, 2, 5):
            x, e, fx, fe, tot = marginals(1, 1, 1, alpha=alpha, crit=crit)
            fe = fe / fe.sum(); fx = fx / fx.sum()
            # inclinacao em energia: ajuste em 3<x<100
            dxl = np.gradient(x); s = (x > 3) & (x < 100)
            sl = np.polyfit(np.log(x[s]), np.log(fx[s] / dxl[s]), 1)[0]
            print(crit, alpha, 'mean e %.3f' % (fe * e).sum(), 'P(e>0.9) %.3f' % fe[e > 0.9].sum(), 'slope dP/dx %.2f' % sl, 'median x %.2f' % x[np.searchsorted(np.cumsum(fx), 0.5)])
    for ms in ((1, 1, 1), (1, 1, 10), (10, 10, 1), (1, 10, 10), (10, 1, 1)):
        pass
