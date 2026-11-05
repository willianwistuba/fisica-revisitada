"""E30b: formula v3 com limiar de massa mais nitido (termos cubicos em ln(m_s/m_max) e cruzados com e).
Ajuste so na grade de massas; testes fora da grade iguais aos da v2."""
import numpy as np, pandas as pd, json, glob
from sklearn.linear_model import LogisticRegression
from scipy import stats
import formula_v2 as F2
import warnings; warnings.filterwarnings('ignore')

def feats(x, e, ma, mb, ms, D0=None):
    F = F2.feats(x, e, ma, mb, ms, D0)
    l = F['lmh'] * np.ones_like(np.asarray(x, float)); ee = F['e']
    F.update(lmh_e=l * ee, lmh2=l ** 2, lmh3=l ** 3, lmh_e2=l * ee ** 2, lmh2_e=l ** 2 * ee, lms2=F['lms'] ** 2 * np.ones_like(ee), lms2_e=F['lms'] ** 2 * ee,
             lmhp=np.maximum(l, 0), lmhn=np.minimum(l, 0), lmhn_e=np.minimum(l, 0) * ee, lmhn_e2=np.minimum(l, 0) * ee ** 2, lmhn2=np.minimum(l, 0) ** 2)
    return F

SETS = {
 'v2':  (F2.C_B1, F2.C_FLY, F2.C_EXC),
 'v4a': (F2.C_B1 + ['lmhn', 'lmhn_e'], F2.C_FLY, F2.C_EXC),
 'v4b': (F2.C_B1 + ['lmhn', 'lmhn_e'], F2.C_FLY + ['lmhn', 'lmhn_e'], F2.C_EXC),
 'v4c': (F2.C_B1 + ['lmhn', 'lmhn_e', 'lmhn_e2'], F2.C_FLY + ['lmhn', 'lmhn_e', 'lmhn_e2'], F2.C_EXC),
 'v4d': (F2.C_B1 + ['lmhn', 'lmhn2', 'lmhn_e'], F2.C_FLY + ['lmhn', 'lmhn2', 'lmhn_e'], F2.C_EXC),
}

def load_grid():
    d = pd.read_csv('b2_rows.csv'); mg = pd.read_csv('massgrid.csv'); grid = set(zip(mg.mb.round(3), mg.ms.round(3)))
    d['ingrid'] = [(ma == 1.0) and ((round(mb, 3), round(ms, 3)) in grid) for ma, mb, ms in zip(d.ma, d.mb, d.ms)]
    X = pd.DataFrame([feats(r.x, r.e, r.ma, r.mb, r.ms, r.D0) for r in d.itertuples()], index=d.index).astype(float)
    return d, X

def fit(d, X, cols):
    g = d.ingrid
    c1, c2, c3 = cols
    m1 = LogisticRegression(C=10, max_iter=8000).fit(X.loc[g, c1], (d.branch[g] == 'troca').astype(int))
    f = g & (d.branch == 'passagem'); m2 = LogisticRegression(C=10, max_iter=8000).fit(X.loc[f, c2], d.bound[f])
    t = g & (d.branch == 'troca'); m3 = LogisticRegression(C=10, max_iter=8000).fit(X.loc[t, c3], d.bound[t])
    return {k: dict(const=float(m.intercept_[0]), **{c: float(v) for c, v in zip(cc, m.coef_[0])}) for k, m, cc in (('B1_troca', m1, c1), ('B2_passagem', m2, c2), ('B2_troca', m3, c3))}

def A(x, e, ma, mb, ms, P):
    Fe = feats(x, e, ma, mb, ms)
    pe = F2.lg(P['B1_troca'], Fe); pf = F2.lg(P['B2_passagem'], Fe); pb = 0
    for out, keep in ((ma, mb), (mb, ma)):
        pb = pb + 0.5 * F2.lg(P['B2_troca'], feats(x, e, ma, mb, ms, np.log(ms * keep / (ma * mb))))
    return pe * pb + (1 - pe) * pf

def offgrid_parts(d, P):
    """B1 e B2 fora da grade: erro medio por celula (combo, x, e)."""
    o = d[~d.ingrid]; out = {}
    rows = []
    for (ma, mb, ms, x, e), s in o.groupby(['ma', 'mb', 'ms', 'x', 'e']):
        F = feats(np.array([x]), np.array([e]), ma, mb, ms)
        rows.append((len(s), (s.branch == 'troca').mean(), F2.lg(P['B1_troca'], F)[0]))
    r = pd.DataFrame(rows, columns=['n', 'm', 'p']); r = r[r.n >= 15]
    out['B1 erro medio'] = (r.m - r.p).abs().mean(); out['B1 R2'] = 1 - ((r.m - r.p) ** 2).mean() / r.m.var()
    return out

if __name__ == '__main__':
    d, X = load_grid()
    x = np.exp(np.linspace(0, np.log(1e3), 900)); u = (np.arange(700) + .5) / 700; e = 1 - (1 - u) ** 2
    XX, EE = np.meshgrid(x, e, indexing='ij'); BASE = XX ** -2.0 * EE / np.sqrt(1 - EE ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
    CH = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)], '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
    ff = pd.read_csv('ffrand.csv'); ff = ff[(ff.status == 1) & (ff.nscram >= 5)]
    m111 = pd.read_csv('ff_111.csv'); m111 = m111[(m111.status == 1) & (m111.nscram >= 5)]
    res = {}
    for name, cols in SETS.items():
        P = fit(d, X, cols)
        json.dump(P, open(f'formula_{name}_e30.json', 'w'), indent=1)
        rows = []
        for fn in sorted(glob.glob('abs4_r20_*.csv')):
            ma, mb, ms = [float(v) for v in fn[9:-4].split(',')]; a = pd.read_csv(fn); a = a[a.ok == 1]
            for (xx, ee), v in a.groupby(['x', 'e']).nS.apply(lambda v: (v >= 2).mean()).items():
                rows.append((fn[9:-4], xx, ee, v, float(A(np.array([xx]), np.array([ee]), ma, mb, ms, P)[0])))
        r = pd.DataFrame(rows, columns=['ch', 'x', 'e', 'A', 'Af'])
        R2 = 1 - ((r.A - r.Af) ** 2).mean() / r.A.var()
        rmean = r.groupby(['ch', 'x']).mean(numeric_only=True); R2e = 1 - ((rmean.A - rmean.Af) ** 2).mean() / rmean.A.var()
        print(f'\n=== {name} ===')
        print(f'absortividade fora da grade: R2 por celula {R2:.2f}; R2 media sobre e {R2e:.2f}; erro medio {np.abs(r.A - r.Af).mean():.3f}')
        print('  B1 fora da grade:', {k: round(v, 3) for k, v in offgrid_parts(d, P).items()})
        errs = []
        for sname, chans in CH.items():
            Ws = [mult * (ma * mb) ** 3 / (ma + mb) * BASE * A(XX, EE, ma, mb, ms, P) for (ma, mb, ms), msc, mult in chans]
            Ps = np.array([W.sum() for W in Ws]); Ps /= Ps.sum()
            q = ff[ff.set == sname]; meas = np.array([(q.mesc == c[1]).mean() for c in chans])
            fe = sum(Ws).sum(0); fe /= fe.sum(); ks = stats.kstest(q.ecc, lambda v: np.interp(v, e, np.cumsum(fe))).statistic
            print(f'  {sname}: escapes medido {np.round(meas,3)} formula {np.round(Ps,3)} | <e> medido {q.ecc.mean():.3f} formula {np.sum(fe*e):.3f} KS {ks:.3f}')
            errs += list(np.abs(Ps - meas)[[1]] if len(chans) == 2 else np.abs(Ps - meas))
        W = BASE * A(XX, EE, 1, 1, 1, P); fe = W.sum(0); fe /= fe.sum()
        ks1 = stats.kstest(m111.ecc, lambda v: np.interp(v, e, np.cumsum(fe))).statistic
        print(f'  1-1-1: <e> medido {m111.ecc.mean():.3f} formula {np.sum(fe*e):.3f} KS {ks1:.3f}')
        print(f'  erro medio nas 5 fracoes de escape: {np.mean(errs)*100:.2f} pontos')
