"""Formula completa da absortividade (B1 + B2) e teste ponta a ponta nas chances de escape."""
import numpy as np, pandas as pd
def P_exch(ma, mb, ms):
    mh = max(ma, mb); return 1 / (1 + (0.52 * mh / ms) ** 1.9)
def P_bound_fly(x, ma, mb, ms):
    z = 0.11 - 1.92 * np.log(x) + 0.59 * np.log(ms / (ma + mb)); return 1 / (1 + np.exp(-z))
def P_bound_exch(x, ma, mb, ms, out):     # out: membro que sai (massa)
    keep = mb if out == ma else ma
    D0 = np.log(ms * keep / (ma * mb)); z = -0.13 - 1.50 * np.log(x) - 1.26 * D0; return 1 / (1 + np.exp(-z))
def A_formula(x, ma, mb, ms, chaos=0.0):
    pe = P_exch(ma, mb, ms)
    pb = 0.5 * (P_bound_exch(x, ma, mb, ms, ma) + P_bound_exch(x, ma, mb, ms, mb))
    return np.clip(chaos + (1 - chaos) * (pe * pb + (1 - pe) * P_bound_fly(x, ma, mb, ms)), 0, 1)
if __name__ == '__main__':
    import glob
    rows = []
    for f in sorted(glob.glob('abs4_r20_*.csv')):
        ma, mb, ms = [float(v) for v in f[9:-4].split(',')]
        a = pd.read_csv(f); a = a[a.ok == 1]
        g = a.groupby('x').nS.apply(lambda v: (v >= 2).mean())
        for x, A in g.items(): rows.append(dict(ch=f[9:-4], x=x, A=A, Af=A_formula(x, ma, mb, ms)))
    r = pd.DataFrame(rows)
    print('Absortividade total (media em e) medida contra formula B1+B2, 77 pontos (7 canais x 11 x):')
    print('  R2 = %.2f, erro medio = %.3f, correlacao = %.3f' % (1 - ((r.A - r.Af) ** 2).mean() / r.A.var(), (r.A - r.Af).abs().mean(), np.corrcoef(r.A, r.Af)[0, 1]))
    print(r.pivot(index='x', columns='ch', values='A').round(2).to_string()); print(r.pivot(index='x', columns='ch', values='Af').round(2).to_string())
    # ponta a ponta: chances de escape com fluxo x formula
    x = np.exp(np.linspace(0, np.log(1e3), 4000)); dx = np.gradient(x)
    SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)], '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
    ff = pd.read_csv('ffrand.csv'); ff = ff[(ff.status == 1) & (ff.nscram >= 5)]
    print('\nChances de escape: medido (5+ embaralhamentos) | fluxo x formula B1+B2 | fluxo puro')
    for name, chans in SETS.items():
        P = np.array([mult * (ma * mb) ** 3 / (ma + mb) * (x ** -2 * A_formula(x, ma, mb, ms) * dx).sum() for (ma, mb, ms), msc, mult in chans]); P /= P.sum()
        P0 = np.array([mult * (ma * mb) ** 3 / (ma + mb) for (ma, mb, ms), msc, mult in chans]); P0 /= P0.sum()
        q = ff[ff.set == name]; meas = [(q.mesc == c[1]).mean() for c in chans]
        print(f'  {name}: ' + ' | '.join(f'm={c[1]}: {mv:.3f} {pv:.3f} {p0:.3f}' for c, mv, pv, p0 in zip(chans, meas, P, P0)))
