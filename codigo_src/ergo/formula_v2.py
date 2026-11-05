"""E29: formula v2 da absortividade (B1 + B2 com excentricidade), ajustada so na grade de massas, e teste ponta a ponta."""
import numpy as np, pandas as pd, json, glob
from sklearn.linear_model import LogisticRegression
from scipy import stats
import warnings; warnings.filterwarnings('ignore')
def feats(x, e, ma, mb, ms, D0=None):
    x = np.asarray(x, float); e = np.asarray(e, float)
    mB = ma + mb; M = mB + ms; aB = ma * mb / (2 * x); mus = ms * mB / M
    vinf = np.sqrt(np.maximum(2 * (x - 1), 0) / mus); vorb = np.sqrt(mB / aB); vp = np.sqrt(vinf ** 2 + 2 * M / aB)
    lS = np.log(vp / vorb); lSapo = lS - 0.5 * np.log((1 - e) / (1 + e))
    lx = np.log(x); lms = np.log(ms / mB); lmh = np.log(ms / max(ma, mb))
    F = dict(lx=lx, e=e, e2=e ** 2, lms=lms, lmh=lmh, lSapo=lSapo, lmh_lSapo=lmh * lSapo, lx_e=lx * e, lms_e=lms * e, lms_lSapo=lms * lSapo)
    if D0 is not None: F.update(D0=D0, D0_e=D0 * e)
    return F
C_B1 = ['lmh', 'lSapo', 'lmh_lSapo']
C_FLY = ['lx', 'lms', 'e', 'e2', 'lx_e', 'lms_e', 'lSapo']
C_EXC = ['lx', 'D0', 'lx_e', 'D0_e']
def fit():
    d = pd.read_csv('b2_rows.csv'); mg = pd.read_csv('massgrid.csv'); grid = set(zip(mg.mb.round(3), mg.ms.round(3)))
    d = d[[(ma == 1.0) and ((round(mb, 3), round(ms, 3)) in grid) for ma, mb, ms in zip(d.ma, d.mb, d.ms)]].copy()
    rows = [feats(r.x, r.e, r.ma, r.mb, r.ms, r.D0) for r in d.itertuples()]
    X = pd.DataFrame(rows, index=d.index).astype(float)
    m1 = LogisticRegression(C=10, max_iter=4000).fit(X[C_B1], (d.branch == 'troca').astype(int))
    f = d.branch == 'passagem'; m2 = LogisticRegression(C=10, max_iter=4000).fit(X.loc[f, C_FLY], d.bound[f])
    t = d.branch == 'troca'; m3 = LogisticRegression(C=10, max_iter=4000).fit(X.loc[t, C_EXC], d.bound[t])
    P = {k: dict(const=float(m.intercept_[0]), **{c: float(v) for c, v in zip(cols, m.coef_[0])}) for k, m, cols in (('B1_troca', m1, C_B1), ('B2_passagem', m2, C_FLY), ('B2_troca', m3, C_EXC))}
    json.dump(P, open('formula_v2.json', 'w'), indent=1); return P
def lg(P, F): return 1 / (1 + np.exp(-(P['const'] + sum(P[k] * F[k] for k in P if k != 'const'))))
def A(x, e, ma, mb, ms, P):
    F = feats(x, e, ma, mb, ms)
    pe = lg(P['B1_troca'], F); pf = lg(P['B2_passagem'], F)
    pb = 0
    for out, keep in ((ma, mb), (mb, ma)):
        F2 = feats(x, e, ma, mb, ms, np.log(ms * keep / (ma * mb))); pb = pb + 0.5 * lg(P['B2_troca'], F2)
    return pe * pb + (1 - pe) * pf
if __name__ == '__main__':
    P = fit(); print(json.dumps(P, indent=1))
    # 1) absortividade total por (x, e) nos 7 canais fora da grade
    rows = []
    for fn in sorted(glob.glob('abs4_r20_*.csv')):
        ma, mb, ms = [float(v) for v in fn[9:-4].split(',')]; a = pd.read_csv(fn); a = a[a.ok == 1]
        for (xx, ee), v in a.groupby(['x', 'e']).nS.apply(lambda v: (v >= 2).mean()).items(): rows.append((fn[9:-4], xx, ee, v, float(A(xx, ee, ma, mb, ms, P))))
    r = pd.DataFrame(rows, columns=['ch', 'x', 'e', 'A', 'Af'])
    print('absortividade total, 924 celulas (x, e) fora da amostra: R2 %.2f, erro medio %.3f, correlacao %.3f' % (1 - ((r.A - r.Af) ** 2).mean() / r.A.var(), (r.A - r.Af).abs().mean(), np.corrcoef(r.A, r.Af)[0, 1]))
    # 2) chances de escape e excentricidade, fluxo x formula
    x = np.exp(np.linspace(0, np.log(1e3), 900)); u = (np.arange(700) + .5) / 700; e = 1 - (1 - u) ** 2
    X, Ee = np.meshgrid(x, e, indexing='ij'); BASE = X ** -2.0 * Ee / np.sqrt(1 - Ee ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
    SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)], '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
    ff = pd.read_csv('ffrand.csv'); ff = ff[(ff.status == 1) & (ff.nscram >= 5)]; errs = []
    for name, chans in SETS.items():
        Ws = [mult * (ma * mb) ** 3 / (ma + mb) * BASE * A(X, Ee, ma, mb, ms, P) for (ma, mb, ms), msc, mult in chans]
        Ps = np.array([W.sum() for W in Ws]); Ps /= Ps.sum()
        q = ff[ff.set == name]; meas = np.array([(q.mesc == c[1]).mean() for c in chans])
        fe = sum(Ws).sum(0); fe /= fe.sum(); ks = stats.kstest(q.ecc, lambda v: np.interp(v, e, np.cumsum(fe))).statistic
        print(f'  {name}: ' + ' | '.join(f'm={c[1]}: medido {mv:.3f} formula {pv:.3f}' for c, mv, pv in zip(chans, meas, Ps)) + f' || excentricidade <e> medido {q.ecc.mean():.3f} formula {np.sum(fe*e):.3f} KS {ks:.3f}')
        errs += list(np.abs(Ps - meas)[[1]] if len(chans) == 2 else np.abs(Ps - meas))
    print('erro medio nas 5 fracoes de escape: %.2f pontos' % (np.mean(errs) * 100))
    m = pd.read_csv('ff_111.csv'); m = m[(m.status == 1) & (m.nscram >= 5)]
    W = BASE * A(X, Ee, 1, 1, 1, P); fe = W.sum(0); fe /= fe.sum(); fx = W.sum(1); fx /= fx.sum()
    print('massas iguais (dentro da grade): <e> medido %.3f formula %.3f KS_e %.3f KS_E %.3f' % (m.ecc.mean(), np.sum(fe * e), stats.kstest(m.ecc, lambda v: np.interp(v, e, np.cumsum(fe))).statistic, stats.kstest(m.EBf, lambda v: np.interp(v, x, np.cumsum(fx))).statistic))
