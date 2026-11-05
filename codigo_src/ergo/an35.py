"""E35: formula v2 e v3 no teste coerente k=2 (ultimo episodio com nS>=2 na queda livre; tabela da v3 refeita com nSf>=2)."""
import numpy as np, pandas as pd, json
from scipy import stats
from scipy.interpolate import RegularGridInterpolator
from statsmodels.stats.multitest import multipletests
import formula_v2 as F2, an33 as A
P = json.load(open('formula_v2.json'))
w = pd.read_csv('wall2.csv'); w = w[w.ok == 1]
for crit in ('nS', 'nSf'):
    w['a_' + crit] = (w[crit] >= 2).astype(int)
def build(crit):
    t = w[(w.ma == 1) & (w.mb == 1) & (~np.isclose(w.ms, 1 / 3, atol=1e-3))].groupby(['ms', 'x', 'e'])['a_' + crit].mean().reset_index(); t['r'] = t.ms / 0.5
    RS = np.sort(t.r.unique()); XS = np.sort(t.x.unique()); ES = np.sort(t.e.unique())
    T = t.pivot_table(index=['r', 'x'], columns='e', values='a_' + crit).values.reshape(len(RS), len(XS), len(ES))
    return RegularGridInterpolator((RS, np.log(XS), ES), T, bounds_error=False, fill_value=None), RS, XS, ES
def make_A3(crit):
    f, RS, XS, ES = build(crit)
    def A3(X, E, ma, mb, ms):
        r = ms / (ma * mb / (ma + mb)); a2 = F2.A(X, E, ma, mb, ms, P)
        if r >= 1.4: return a2
        lx = np.clip(np.log(X), np.log(XS[0]), np.log(XS[-1])); ee = np.clip(E, ES[0], ES[-1])
        at = np.clip(f(np.stack(np.broadcast_arrays(np.full_like(lx, min(max(r, RS[0]), RS[-1])), lx, ee), -1)), 0, 1)
        big = X > XS[-1]
        ref = F2.A(np.full_like(X, XS[-1]), E, ma, mb, ms, P)
        with np.errstate(divide='ignore', invalid='ignore'): fac = np.where(ref > 0, a2 / ref, 0)
        at = np.where(big, at * np.clip(fac, 0, 1), at); wgt = np.clip((r - 1.0) / 0.4, 0, 1)
        return (1 - wgt) * at + wgt * a2
    return A3
d = pd.read_csv('age.csv'); fin = d[(d.exit == 'esc') & (d.status == 1) & (d.nS >= 2)]
models = {'v2': lambda X, E, ma, mb, ms: F2.A(X, E, ma, mb, ms, P), 'v3 (tabela nS)': make_A3('nS'), 'v3 (tabela nSf)': make_A3('nSf')}
rows = []
for lab, fA in models.items():
    for name, chans in A.SETS.items():
        Ws = [mult * (ma * mb) ** 3 / (ma + mb) * A.BASE * fA(A.X, A.E, ma, mb, ms) for (ma, mb, ms), msc, mult in chans]
        Ps = np.array([W.sum() for W in Ws]); Ps /= Ps.sum(); fe = sum(Ws).sum(0); fe /= fe.sum(); cdf = np.cumsum(fe)
        q = fin[fin.set == name]; n = len(q)
        ks = stats.kstest(q.e_exit, lambda v: np.interp(v, A.e, cdf))
        obs = np.array([(q.mbody == c[1]).sum() for c in chans]); chi = stats.chisquare(obs, Ps * n)
        rows.append((lab, name, n, ks.statistic, ks.pvalue, q.e_exit.mean(), float(np.sum(fe * A.e)), np.round(obs / n, 3), np.round(Ps, 3), np.abs(obs / n - Ps).max() * 100, chi.pvalue))
R = pd.DataFrame(rows, columns=['modelo', 'conjunto', 'n', 'KS', 'p_e', 'e_med', 'e_prev', 'esc_med', 'esc_prev', 'maior_erro_pp', 'p_esc'])
for lab in models:
    m = R.modelo == lab
    R.loc[m, 'e_ok'] = ~multipletests(R.loc[m, 'p_e'], .05, 'holm')[0]; R.loc[m, 'esc_ok'] = ~multipletests(R.loc[m, 'p_esc'], .05, 'holm')[0]
pd.set_option('display.width', 250); print(R.round(4).to_string(index=False))
