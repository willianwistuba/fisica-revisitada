import sys, json, numpy as np, pandas as pd
from scipy import optimize, stats
sys.argv = ['x', '/home/claude/estudo/conf_dados']; sys.path.insert(0, '/home/claude/fisica-revisitada/codigo_src/ergo/rotacao')
import analise_rot as A, rot
R1, R2, L0D = '/home/claude/estudo/rot_dados', '/home/claude/estudo/conf_dados', '/home/claude/estudo/dados/pacote_v2'
CH = {(1., 3., 1.): '1-1-3', (1., 1., 3.): '1-1-3', (2., 3., 1.): '1-2-3', (1., 3., 2.): '1-2-3', (1., 2., 3.): '1-2-3'}
fmt = lambda m: ','.join('%g' % v for v in m)
def cells(df):
    df = df[(df.ok == 1) | (df.get('alcance', 1) == 0)].copy(); df['h'] = (df.ok == 1) & (df.nSf >= 3)
    return df.groupby([c for c in ('x', 'e', 's') if c in df]).h.agg(K='sum', N='size').reset_index()
def rho(x, e, s, m, lam):
    ma, mb, ms = m; aB = ma * mb / (2 * x); lB = ma * mb / (ma + mb) * np.sqrt((ma + mb) * aB * (1 - e * e))
    L = lam * np.sqrt(rot.kB_principal([float(v) for v in CH[m].split('-')]) / 2); return (L - s * lB) / (s * lB)
lg = lambda p: np.log(p / (1 - p)); ex = lambda z: 1 / (1 + np.exp(-z))
def dev(K, N, p):
    p = np.clip(p, 1e-6, 1 - 1e-6); a = np.where(K > 0, K * np.log(np.maximum(K, 1e-12) / (N * p)), 0); b = np.where(N - K > 0, (N - K) * np.log(np.maximum(N - K, 1e-12) / (N * (1 - p))), 0)
    return float(2 * (a + b).sum())
out = {}; modelos = {}
for m in CH:
    a0 = cells(pd.concat([pd.read_csv(f'{L0D}/{t}_{fmt(m)}.csv') for t in ('abs4_r20', 'abs5_cauda')]))
    a0['p0'] = (a0.K + 0.5) / (a0.N + 1); a0 = a0[['x', 'e', 'p0']]; a0['e'] = a0.e.round(6)
    def lado(D, lam):
        c = cells(pd.concat([pd.read_csv(f'{D}/{t}_{fmt(m)}_lam{lam}.csv') for t in ('abs4_r20', 'abs5_cauda')])); c['e'] = c.e.round(6)
        c = c.merge(a0, on=['x', 'e']); c['rho'] = rho(c.x.values, c.e.values, c.s.values, m, lam); c['lam'] = lam; return c
    tr = pd.concat([lado(R1, l) for l in (0.3, 0.7)])
    nos = np.r_[np.quantile(tr.rho, np.linspace(0, 1, 8)), -1.0]; nos = np.unique(np.round(nos, 6))
    def g(par, r): return np.interp(r, nos, par)
    i1 = np.argmin(abs(nos + 1))
    def nll(q):
        par = np.insert(q, i1, 0.0); p = ex(lg(tr.p0.values) + g(par, tr.rho.values)); p = np.clip(p, 1e-9, 1 - 1e-9)
        return -(tr.K * np.log(p) + (tr.N - tr.K) * np.log(1 - p)).sum()
    res = optimize.minimize(nll, np.zeros(len(nos) - 1), method='L-BFGS-B'); par = np.insert(res.x, i1, 0.0)
    modelos[m] = (nos, par, a0)
    r = {}
    for lam in (0.1, 0.3, 0.7):
        te = lado(R2, lam); pm = ex(lg(te.p0.values) + g(par, te.rho.values))
        r[lam] = dict(dev_modelo=dev(te.K.values, te.N.values, pm), dev_sem_rotacao=dev(te.K.values, te.N.values, te.p0.values), celulas=len(te))
        if lam in (0.3, 0.7):
            raw = lado(R1, lam)[['x', 'e', 's', 'K', 'N']].rename(columns={'K': 'K1', 'N': 'N1'}); tt = te.merge(raw, on=['x', 'e', 's'])
            r[lam]['dev_tabela_r1'] = dev(tt.K.values, tt.N.values, ((tt.K1 + 0.5) / (tt.N1 + 1)).values)
    out[fmt(m)] = dict(nos=nos.round(3).tolist(), g=par.round(3).tolist(), testes=r)
    print(fmt(m), {l: {k: round(v, 1) for k, v in d.items()} for l, d in r.items()}, flush=True)
# C2: fracao prograda prevista em lam = 0,1 contra a medida
conf = json.load(open(f'{R2}/resultado_conf.json'))['testes']; c2 = []
for nome, chans in A.CONJ.items():
    tabs, Ps = [], []
    for mm, _, _ in chans:
        nos, par, a0 = modelos[mm]; tc, pc = [], []
        for s in (1, -1):
            xs, js, K, N = A.table(A.load(mm, 0.1), 3, s)
            X, J = np.meshgrid(xs, js, indexing='ij'); E = np.sqrt(1 - J ** 2).round(6)
            p0 = pd.DataFrame(dict(x=X.ravel(), e=E.ravel())).merge(a0, on=['x', 'e'], how='left').p0.values.reshape(X.shape)
            tc.append((xs, js, K, N)); pc.append(ex(lg(p0) + np.interp(rho(X, E, s, mm, 0.1), nos, par)))
        tabs.append(tc); Ps.append(pc)
    W = A.weights(chans, tabs, Ps); tot = np.array([[w.sum() for w in ww] for ww in W]); fp = tot[:, 0].sum() / tot.sum()
    t = [x for x in conf if x['conjunto'] == nome and x['lam'] == 0.1 and x['k'] == 3][0]; n = t['n']; k = round(t['fracao_prograda_medida'] * n)
    p = stats.binomtest(k, n, fp).pvalue; c2.append(p)
    print(nome, 'lam 0,1: prograda medida %.3f, modelo %.3f, tabela medida %.3f, p = %.3f' % (k / n, fp, t['fracao_prograda_prevista'], p))
out['C2_p'] = c2; out['C2_holm_passa'] = A.holm(np.array(c2)).tolist()
json.dump(out, open('resultado_colapso.json', 'w'), indent=1)
print('C2 Holm:', out['C2_holm_passa'])
