"""Que combinacao fisica explica a absortividade? Testa empurrao (impulso de mare) e velocidade (adiabaticidade)."""
import glob, numpy as np, pandas as pd
rows = []
for f in sorted(glob.glob('abs4_r20_*.csv')):
    ma, mb, ms = [float(v) for v in f[9:-4].split(',')]
    a = pd.read_csv(f); a = a[a.ok == 1]
    g = a.groupby(['x', 'e']).agg(Af=('nSf', lambda v: (v >= 2).mean()), At=('nS', lambda v: (v >= 2).mean()), n=('nS', 'size')).reset_index()
    mB = ma + mb; M = mB + ms; E0 = -1.0
    EB = g.x * E0; Es = E0 - EB; aB = ma * mb / (2 * abs(EB)); mus = ms * mB / M
    vinf = np.sqrt(2 * Es / mus); vorb = np.sqrt(mB / aB)
    for lab, dd in (('a', aB), ('apo', aB * (1 + g.e)), ('peri', aB * (1 - g.e) + 1e-9)):
        vp = np.sqrt(vinf ** 2 + 2 * M / dd)
        g['K_' + lab] = ms / (np.sqrt(mB / dd) * dd * vp)          # empurrao: kick relativo ~ G m_s/(d v_p) / v_orb(d)
        g['S_' + lab] = vp / np.sqrt(mB / dd)                      # velocidade relativa / velocidade orbital (adiabaticidade)
    g['sig'] = vinf / vorb; g['ch'] = f[9:-4]; g['mrat'] = ms / mB
    rows.append(g)
d = pd.concat(rows, ignore_index=True)
def r2(y, cols, df=d):
    X = np.c_[np.ones(len(df))] if not cols else np.c_[np.ones(len(df)), np.column_stack([df[c] for c in cols])]
    b = np.linalg.lstsq(X, y, rcond=None)[0]; r = y - X @ b; return 1 - r.var() / y.var()
for A in ('Af', 'At'):
    y = d[A].values; noise = np.mean(y * (1 - y) / d.n); ceil = 1 - noise / y.var()
    print(f'\n=== absortividade {A} ({"ate a 1a excursao" if A=="Af" else "contagem total"}); teto pelo ruido R2={ceil:.2f} ===')
    for c in ('K_a', 'K_apo', 'K_peri', 'S_a', 'S_apo', 'sig'):
        d['l' + c] = np.log(d[c])
    tests = {
        'so energia x e excentricidade e (sem massas)': ['lx', 'e', 'lx2', 'e2', 'lxe'],
        'empurrao K (a)': ['lK_a', 'lK_a2'],
        'empurrao K (apoastro)': ['lK_apo', 'lK_apo2'],
        'velocidade S (a)': ['lS_a', 'lS_a2'],
        'velocidade sigma (infinito)': ['lsig', 'lsig2'],
        'empurrao + velocidade (a)': ['lK_a', 'lS_a', 'lK_a2', 'lS_a2', 'lKS'],
        'empurrao x velocidade (a), um numero': ['lKxS', 'lKxS2'],
        'empurrao + velocidade (apoastro)': ['lK_apo', 'lS_apo', 'lK_apo2', 'lS_apo2', 'lKSapo'],
        'empurrao + velocidade (apo) + e': ['lK_apo', 'lS_apo', 'lK_apo2', 'lS_apo2', 'lKSapo', 'e', 'e2'],
    }
    d['lx'] = np.log(d.x); d['lx2'] = d.lx ** 2; d['e2'] = d.e ** 2; d['lxe'] = d.lx * d.e
    for c in ('lK_a', 'lK_apo', 'lS_a', 'lsig', 'lS_apo'): d[c + '2'] = d[c] ** 2
    d['lKS'] = d.lK_a * d.lS_a; d['lKSapo'] = d.lK_apo * d.lS_apo; d['lKxS'] = d.lK_a + d.lS_a; d['lKxS2'] = d.lKxS ** 2
    for lab, cols in tests.items():
        print(f'  {lab:42s} R2={r2(y, cols):.2f}')
    # teste de universalidade: ajusta num conjunto de canais, preve nos outros
    tr = d.ch.isin(['1,3,1', '3,3,1', '2,3,1', '1,2,3']); te = ~tr
    for lab in ('empurrao + velocidade (apo) + e', 'so energia x e excentricidade e (sem massas)'):
        cols = tests[lab]
        X = lambda df: np.c_[np.ones(len(df)), np.column_stack([df[c] for c in cols])]
        b = np.linalg.lstsq(X(d[tr]), y[tr], rcond=None)[0]; p = X(d[te]) @ b
        yt = y[te]; print(f'  universalidade ({lab}): R2 em canais nao usados no ajuste = {1-((yt-p)**2).mean()/yt.var():.2f}')

print('\n=== com razao de massas (quem chega / dupla) ===')
d['lm'] = np.log(d.mrat); d['lm2'] = d.lm ** 2
for A in ('Af', 'At'):
    y = d[A].values
    for lab, cols in (('velocidade + massas + e', ['lS_apo', 'lS_apo2', 'lm', 'lm2', 'e', 'e2', 'lS_apo_m']),
                      ('empurrao + velocidade + massas + e', ['lK_apo', 'lS_apo', 'lK_apo2', 'lS_apo2', 'lKSapo', 'lm', 'e', 'e2'])):
        d['lS_apo_m'] = d.lS_apo * d.lm
        X = lambda df: np.c_[np.ones(len(df)), np.column_stack([df[c] for c in cols])]
        b = np.linalg.lstsq(X(d), y, rcond=None)[0]; p = X(d) @ b
        # deixa um canal de fora por vez
        errs = []
        for ch in d.ch.unique():
            tr = d.ch != ch; te = ~tr
            bb = np.linalg.lstsq(X(d[tr]), y[tr], rcond=None)[0]; pp = X(d[te]) @ bb; errs.append(np.sqrt(((y[te] - pp) ** 2).mean()))
        print(f'  {A} {lab:38s} R2={1-((y-p)**2).mean()/y.var():.2f}  erro tipico deixando um canal de fora={np.mean(errs):.3f} (desvio da absortividade={y.std():.3f})')
