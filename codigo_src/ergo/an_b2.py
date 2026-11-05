import numpy as np, pandas as pd
from scipy import stats
a = pd.read_csv('onepass.csv'); a = a[a.ok == 1].copy()
m = a.ch.str.split(',', expand=True).astype(float); a['ma'], a['mb'], a['ms'] = m[0], m[1], m[2]; a['body'] = a.body.astype(int)
b = pd.read_csv('massgrid.csv'); b = b[b.ok == 1].copy(); b['ma'] = 1.0; b['body'] = b['first'].astype(int)
d = pd.concat([a[['ma', 'mb', 'ms', 'x', 'e', 'body', 'xnew', 'nS1']], b[['ma', 'mb', 'ms', 'x', 'e', 'body', 'xnew', 'nS1']]], ignore_index=True)
d = d[d.nS1 <= 1].copy()                       # primeira passagem regular
mm = d[['ma', 'mb', 'ms']].values
d['m_out'] = mm[np.arange(len(d)), d.body]
keep = np.array([[j for j in range(3) if j != k] for k in d.body])
d['m1'] = mm[np.arange(len(d)), keep[:, 0]]; d['m2'] = mm[np.arange(len(d)), keep[:, 1]]
d['branch'] = np.where(d.body == 2, 'passagem', 'troca')
d['D'] = np.log(d.xnew / d.x); d['bound'] = d.xnew < 1
# estimativa geometrica para trocas: novo par com o mesmo semieixo do antigo
d['D0'] = np.log(d.m1 * d.m2 / (d.ma * d.mb))
d.to_csv('b2_rows.csv', index=False)
print('linhas', len(d), d.branch.value_counts().to_dict())
for br, g in d.groupby('branch'):
    print(f'\n== {br} ==  P(fica ligado) media {g.bound.mean():.3f}')
    c = g.groupby(['ma', 'mb', 'ms', 'x', 'e', 'body']).agg(n=('D', 'size'), med=('D', 'median'), q1=('D', lambda v: v.quantile(.25)), q3=('D', lambda v: v.quantile(.75)), D0=('D0', 'first'), P=('bound', 'mean')).reset_index()
    c = c[c.n >= 15]
    print(f'  celulas {len(c)}; mediana de D: media {c.med.mean():+.3f} desvio {c.med.std():.3f}; largura (IQR/1,35) media {((c.q3-c.q1)/1.349).mean():.3f}')
    for var in ('x', 'e'):
        print('  mediana de D por', var, c.groupby(var).med.mean().round(3).to_dict())
    if br == 'troca':
        print('  correlacao mediana de D com a estimativa geometrica D0: %.3f; inclinacao %.2f' % (np.corrcoef(c.med, c.D0)[0, 1], np.polyfit(c.D0, c.med, 1)[0]))
