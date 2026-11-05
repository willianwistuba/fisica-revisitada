"""E24: modelo de uma passagem. A excursao acontece quando a energia do par logo apos a 1a passagem fica abaixo do limiar: x_novo < 1.
Testa se a distribuicao de D = ln(x_novo/x) tem centro e largura dados por leis simples do encontro."""
import numpy as np, pandas as pd
from scipy import stats
d = pd.read_csv('onepass.csv'); d = d[d.ok == 1].copy()
d['reg'] = d.nS1 <= 1; d['D'] = np.log(d.xnew / d.x)
rows = []
for (ch, x, e), g in d.groupby(['ch', 'x', 'e']):
    ma, mb, ms = [float(v) for v in ch.split(',')]; mB = ma + mb; M = mB + ms
    r = g[g.reg]; D = r.D.values
    mu = np.median(D); sg = (np.percentile(D, 75) - np.percentile(D, 25)) / 1.349
    EB = -x; Es = -1 - EB; aB = ma * mb / (2 * x); mus = ms * mB / M
    vinf = np.sqrt(2 * Es / mus); vorb = np.sqrt(mB / aB); vp = np.sqrt(vinf ** 2 + 2 * M / aB)
    rows.append(dict(ch=ch, x=x, e=e, n=len(g), nreg=len(r), Pexc=(g.reg & (g.xnew < 1)).mean(), Pch=(~g.reg).mean(),
                     Pexc_reg=(D < -np.log(x)).mean(), mu=mu, sg=sg, lS=np.log(vp / vorb), lm=np.log(ms / mB), q=min(ma, mb) / max(ma, mb), lx=np.log(x)))
c = pd.DataFrame(rows)
# 1) dado mu e sigma da propria celula, uma gaussiana preve P(excursao)?
c['Pg'] = stats.norm.cdf((-c.lx - c.mu) / c.sg)
print('Gaussiana com centro e largura da propria celula: erro medio em P(exc|regular) = %.3f (P media %.3f)' % ((c.Pg - c.Pexc_reg).abs().mean(), c.Pexc_reg.mean()))
for lab in ('mu', 'sg'):
    print(f'  {lab}: media {c[lab].mean():.3f}, desvio {c[lab].std():.3f}')
# 2) leis para mu e sigma
F = {'velocidade, e, massas': ['lS', 'e', 'e2', 'lm', 'q', 'lSe'], 'energia, e, massas': ['lx', 'e', 'e2', 'lm', 'q', 'lxe']}
c['e2'] = c.e ** 2; c['lSe'] = c.lS * c.e; c['lxe'] = c.lx * c.e
def fit(df, y, cols):
    X = np.c_[np.ones(len(df)), df[cols].values]; b = np.linalg.lstsq(X, df[y].values, rcond=None)[0]; return b
def pred(df, b, cols): return np.c_[np.ones(len(df)), df[cols].values] @ b
for lab, cols in F.items():
    out = {}
    for y in ('mu', 'sg'):
        b = fit(c, y, cols); p = pred(c, b, cols); out[y] = 1 - ((c[y] - p) ** 2).mean() / c[y].var()
    # previsao de P(exc) com mu, sigma das leis, deixando um canal de fora
    P = np.zeros(len(c))
    for ch in c.ch.unique():
        tr = c.ch != ch; te = ~tr
        bm = fit(c[tr], 'mu', cols); bs = fit(c[tr], 'sg', cols)
        mu = pred(c[te], bm, cols); sg = np.maximum(pred(c[te], bs, cols), 0.05)
        P[te.values] = stats.norm.cdf((-c[te].lx.values - mu) / sg)
    # P(excursao) total = P(regular) * P(exc|regular); para comparar, usa P(regular) medido
    Pe = P * (1 - c.Pch)
    r2 = 1 - ((c.Pexc - Pe) ** 2).mean() / c.Pexc.var()
    print(f'{lab}: R2 centro {out["mu"]:.2f}, largura {out["sg"]:.2f} | P(excursao) prevista em canais deixados de fora: R2={r2:.2f}, erro medio {np.abs(c.Pexc-Pe).mean():.3f} (desvio de P {c.Pexc.std():.3f})')
c.to_csv('onepass_cells.csv', index=False)
