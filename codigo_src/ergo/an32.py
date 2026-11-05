"""E32: formula v3 = v2 fora do regime leve + absortividade tabelada em r = ms/mu (massa de quem chega / massa reduzida do par).
Treino da tabela: so o par (1,1) do mapa wall2, SEM a razao q=1/3 (que equivale ao canal 3,3,1 do teste).
Testes fora do treino: (T1) par (1,2) do mapa wall2; (T2) canal (3,3,1) medido em abs4 (200 por celula);
(T3) queda livre 3-3-1 e (T4) queda livre 1-2-3 e 1-1-3: fracoes de escape e distribuicao de e (KS, valor critico 1,36/sqrt(n))."""
import numpy as np, pandas as pd, json
from scipy import stats
from scipy.interpolate import RegularGridInterpolator
import formula_v2 as F2
P = json.load(open('formula_v2.json'))
g = pd.read_csv('wall2_cells.csv')
tr = g[(g.ma == 1) & (g.mb == 1) & (~np.isclose(g.ms, 1 / 3, atol=1e-3))].copy()
tr['r'] = tr.ms / 0.5
RS = np.sort(tr.r.unique()); XS = np.sort(tr.x.unique()); ES = np.sort(tr.e.unique())
T = np.full((len(RS), len(XS), len(ES)), np.nan)
for i, r in enumerate(RS):
    for j, x in enumerate(XS):
        s = tr[np.isclose(tr.r, r) & np.isclose(tr.x, x)].sort_values('e'); T[i, j] = s.p.values
interp = RegularGridInterpolator((RS, np.log(XS), ES), T, bounds_error=False, fill_value=None)
R_LO, R_HI = 1.0, 1.4          # acima de R_HI usa so a v2; entre R_LO e R_HI mistura linear

def A_table(x, e, r):
    x = np.asarray(x, float); e = np.asarray(e, float)
    lx = np.clip(np.log(x), np.log(XS[0]), np.log(XS[-1])); ee = np.clip(e, ES[0], ES[-1]); rr = np.clip(r, RS[0], RS[-1])
    pts = np.stack(np.broadcast_arrays(np.full_like(lx, rr), lx, ee), -1)
    return np.clip(interp(pts), 0, 1)

def A3(x, e, ma, mb, ms):
    x = np.asarray(x, float); e = np.asarray(e, float); r = ms / (ma * mb / (ma + mb))
    a2 = F2.A(x, e, ma, mb, ms, P)
    if r >= R_HI: return a2
    at = A_table(x, e, r)
    # para x alem da tabela (x>3), escala pela queda da v2 em x, mantendo a forma em e da tabela
    big = x > XS[-1]
    if np.any(big):
        ref = F2.A(np.full_like(x, XS[-1]), e, ma, mb, ms, P)
        with np.errstate(divide='ignore', invalid='ignore'):
            fac = np.where(ref > 0, a2 / ref, 0)
        at = np.where(big, at * np.clip(fac, 0, 1), at)
    w = np.clip((r - R_LO) / (R_HI - R_LO), 0, 1)
    return (1 - w) * at + w * a2

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h

print('T1) par (1,2) previsto pela tabela do par (1,1) via r = ms/mu (fora do treino)')
te = g[(g.ma == 1) & (g.mb == 2)].copy(); te['r'] = te.ms / (2 / 3)
te = te[te.r < R_HI]
te['pred'] = [float(A_table(np.array([x]), np.array([e]), r)[0]) for x, e, r in zip(te.x, te.e, te.r)]
te['pv2'] = [float(F2.A(np.array([x]), np.array([e]), 1, 2, ms, P)[0]) for x, e, ms in zip(te.x, te.e, te.ms)]
ci = [wilson(k, n) for k, n in zip(te['sum'], te['size'])]; te['inci'] = [lo <= p <= hi for (lo, hi), p in zip(ci, te.pred)]
for lab, c in (('tabela v3', 'pred'), ('formula v2', 'pv2')):
    R2 = 1 - ((te.p - te[c]) ** 2).sum() / ((te.p - te.p.mean()) ** 2).sum()
    print(f'   {lab:10s}: celulas {len(te)}, erro medio {np.abs(te.p - te[c]).mean():.3f}, R2 {R2:.2f}')
print(f'   celulas em que a previsao da v3 cai dentro do IC95 da medida: {te.inci.mean():.2f}')
z = te[te['sum'] == 0]; print(f'   celulas com zero absorcoes medidas: {len(z)}; previsao media nelas: v3 {z.pred.mean():.3f}, v2 {z.pv2.mean():.3f}')

print('\nT2) canal (3,3,1), absortividade medida em abs4 (200 por celula), fora do treino')
a = pd.read_csv('abs4_r20_3,3,1.csv'); a = a[a.ok == 1]
c2 = a.groupby(['x', 'e']).nS.agg(k=lambda v: (v >= 2).sum(), n='size').reset_index(); c2['p'] = c2.k / c2.n
c2['v3'] = A3(c2.x.values, c2.e.values, 3, 3, 1); c2['v2'] = F2.A(c2.x.values, c2.e.values, 3, 3, 1, P)
for c in ('v3', 'v2'):
    R2 = 1 - ((c2.p - c2[c]) ** 2).sum() / ((c2.p - c2.p.mean()) ** 2).sum()
    print(f'   {c}: erro medio {np.abs(c2.p - c2[c]).mean():.3f}, R2 por celula {R2:.2f}')

print('\nT3/T4) quedas livres: fracoes de escape e excentricidade final')
x = np.exp(np.linspace(0, np.log(1e3), 900)); u = (np.arange(700) + .5) / 700; e = 1 - (1 - u) ** 2
X, E = np.meshgrid(x, e, indexing='ij'); BASE = X ** -2.0 * E / np.sqrt(1 - E ** 2) * np.gradient(x)[:, None] * np.gradient(e)[None, :]
SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)], '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
ff = pd.read_csv('ffrand.csv'); ff = ff[(ff.status == 1) & (ff.nscram >= 5)]
for lab, fA in (('v2', lambda X, E, ma, mb, ms: F2.A(X, E, ma, mb, ms, P)), ('v3', A3)):
    errs = []; out = []
    for name, chans in SETS.items():
        Ws = [mult * (ma * mb) ** 3 / (ma + mb) * BASE * fA(X, E, ma, mb, ms) for (ma, mb, ms), msc, mult in chans]
        Ps = np.array([W.sum() for W in Ws]); Ps /= Ps.sum()
        q = ff[ff.set == name]; n = len(q); meas = np.array([(q.mesc == c[1]).mean() for c in chans])
        se = np.sqrt(meas * (1 - meas) / n)
        fe = sum(Ws).sum(0); fe /= fe.sum(); ks = stats.kstest(q.ecc, lambda v: np.interp(v, e, np.cumsum(fe))).statistic
        crit = 1.36 / np.sqrt(n)
        dentro = np.all(np.abs(Ps - meas) <= 1.96 * se)
        out.append(f'   {lab} {name}: escapes medido {np.round(meas,3)} (+-{np.round(1.96*se,3)}) formula {np.round(Ps,3)} {"dentro" if dentro else "FORA"} do IC95 | <e> {q.ecc.mean():.3f} x {np.sum(fe*e):.3f} | KS {ks:.3f} (critico {crit:.3f}) {"ok" if ks < crit else "REJEITA"}')
        errs += list(np.abs(Ps - meas)[[1]] if len(chans) == 2 else np.abs(Ps - meas))
    print('\n'.join(out)); print(f'   {lab}: erro medio nas 5 fracoes de escape {np.mean(errs)*100:.2f} pontos')
