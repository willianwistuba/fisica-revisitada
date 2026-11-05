import numpy as np, pandas as pd
exec(open('analyse18.py').read().split("SETS =")[0].split("pre = sys.argv")[0])
SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)], '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
f = pd.read_csv('ffrand3.csv'); f = f[f.status == 1]
rows = []
for name, chans in SETS.items():
    P = {}
    for k in (2, 3):
        v = np.array([mult * (ma * mb) ** 3 / (ma + mb) * (BASE * grid(f'abs4_r20_{ma},{mb},{ms}.csv', 'nS', k)[0]).sum() for (ma, mb, ms), msc, mult in chans]); P[k] = v / v.sum()
    g = f[f.set == name]
    subs = {'nS>=2': g[g.nS >= 2], 'nS>=5': g[g.nS >= 5], 'nS>=2,T<=10': g[(g.nS >= 2) & (g['T'] <= 10)], 'nS>=2,T>30': g[(g.nS >= 2) & (g['T'] > 30)],
            'nS>=2,sem exc': g[(g.nS >= 2) & (g.nexc == 0)], 'nS>=2,com exc': g[(g.nS >= 2) & (g.nexc > 0)], 'nSl>=2': g[g.nSl >= 2]}
    for i, c in enumerate(chans):
        vals = {kk: (q.mesc == c[1]).mean() for kk, q in subs.items()}
        rows.append(dict(set=name, m=c[1], pred2=P[2][i], pred3=P[3][i], meas=vals['nS>=5'], lo=min(vals.values()), hi=max(vals.values()), **{kk: round(v, 3) for kk, v in vals.items()}))
r = pd.DataFrame(rows)
if not (r.m == 1).all(): pass
print(r.round(3).to_string())
r['heavy_or_all'] = True
sel = r[~((r.set != '1-2-3') & (r.m == 1))]
print('erro medio vs nS>=5: k2 %.2f  k3 %.2f pontos' % ((sel.pred2 - sel.meas).abs().mean() * 100, (sel.pred3 - sel.meas).abs().mean() * 100))
print('previsao dentro do envelope medido:', ((sel.pred2 >= sel.lo) & (sel.pred2 <= sel.hi)).tolist(), ((sel.pred3 >= sel.lo) & (sel.pred3 <= sel.hi)).tolist())
print('largura media do envelope: %.2f pontos' % ((sel.hi - sel.lo).mean() * 100))
