import numpy as np, pandas as pd, sys
exec(open('analyse18.py').read().split("SETS =")[0].split("pre = sys.argv")[0])
ff = pd.read_csv('ffrand.csv'); ff = ff[ff.status == 1]
def pred(chans, files, col, k):
    P = np.array([mult * (ma * mb) ** 3 / (ma + mb) * (BASE * grid(fn, col, k)[0]).sum() for ((ma, mb, ms), msc, mult), fn in zip(chans, files)]); return P / P.sum()
SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)], '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}
sets = sys.argv[1].split(',') if len(sys.argv) > 1 else list(SETS)
for name in sets:
    chans = SETS[name]
    g = ff[ff.set == name]
    for lo in (2, 5):
        q = g[g.nscram >= lo]; meas = [(q.mesc == c[1]).mean() for c in chans]
        print(f'{name} medido nscram>={lo} (n={len(q)}): ' + ' '.join(f'{v:.3f}' for v in meas))
    for lab, files, col in (('antigo r=20 (grade 7x)', [f'abs_{a},{b},{c}.csv' for (a, b, c), _, _ in chans], 'nscram'),
                            ('r=20 grade fina', [f'abs4_r20_{a},{b},{c}.csv' for (a, b, c), _, _ in chans], 'nS'),
                            ('r=40 grade fina', [f'abs4_r40_{a},{b},{c}.csv' for (a, b, c), _, _ in chans], 'nS')):
        try:
            for k in (2, 3):
                print(f'   {lab:24s} k={k}: ' + ' '.join(f'{v:.3f}' for v in pred(chans, files, col, k)))
        except FileNotFoundError:
            pass
