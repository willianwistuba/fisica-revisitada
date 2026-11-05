"""Diagnostico (dados de teste, so para localizar o erro): absortividade medida x v11 por canal, ponderada pelo fluxo."""
import json, numpy as np, pandas as pd, prova11 as P
d11 = json.load(open('formula_v11_referencia.json')); p = np.array([d11[n] for n in P.NAMES])
for ch in ['1,3,1', '1,1,3', '3,3,1', '3,1,3', '2,3,1', '1,3,2', '1,2,3']:
    d = pd.read_csv(f'abs4_r20_{ch}.csv'); ma, mb, ms = map(float, ch.split(','))
    d['A'] = (d.nSf >= 2).astype(int); c = d.groupby(['x', 'e']).agg(K=('A', 'sum'), N=('A', 'size')).reset_index()
    n = len(c); Fe = P.feats(c.x.values, c.e.values, np.full(n, ma), np.full(n, mb), np.full(n, ms))
    W = P.flux_w(c.x.values, c.e.values); med = c.K / c.N; prev = P.A_model(p, Fe)
    lo = c.e < 0.5
    print(f'({ch}) r={Fe["r"][0]:.2f} | media ponderada: medida {np.average(med, weights=W):.3f} v11 {np.average(prev, weights=W):.3f}'
          f' | e<0,5: {np.average(med[lo], weights=W[lo]):.3f} vs {np.average(prev[lo], weights=W[lo]):.3f}'
          f' | e>=0,5: {np.average(med[~lo], weights=W[~lo]):.3f} vs {np.average(prev[~lo], weights=W[~lo]):.3f} | corridas {int(c.N.sum())}')
