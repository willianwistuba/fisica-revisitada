"""Simulado interno: validacao cruzada por grupos de massas (regime pesado), so com dados de treino."""
import os, sys, json, time, numpy as np, pandas as pd
from multiprocessing import Pool
VARS = ['cheia', 'media', 'enxuta']; NF = 8
def job(a):
    var, k = a; os.environ['VARIANTE_H'] = var
    import importlib, prova11 as P; importlib.reload(P)
    C = pd.read_csv('treino_celulas.csv'); A, B, Cc = P.canon(C.ma.values, C.mb.values, C.ms.values)
    r = Cc / (A * B / (A + B)); g = pd.Series(list(zip(np.round(B, 3), np.round(Cc, 3))))
    heavy = sorted(set(g[r >= 1.5])); rng = np.random.default_rng(5); rng.shuffle(heavy)
    out = set(heavy[k::NF]); te = g.isin(out).values
    tr = C[~te].reset_index(drop=True); ts = C[te].reset_index(drop=True)
    p0 = P.P0.copy(); t0 = time.time()
    p, _ = P.fit(tr, tr.K.values.astype(float), p0, 2)
    Fe = P.feats(ts.x.values, ts.e.values, ts.ma.values, ts.ms.values * 0 + ts.mb.values, ts.ms.values)
    Am = P.A_model(p, Fe); W = P.flux_w(ts.x.values, ts.e.values)
    nll = float(-(W * (ts.K * np.log(Am) + (ts.N - ts.K) * np.log(1 - Am))).sum())
    nll0 = float(-(W * (ts.K * np.log(ts.K.clip(0.5) / ts.N) + (ts.N - ts.K) * np.log(1 - ts.K.clip(0.5) / ts.N).clip(-50))).sum())
    return var, k, nll, nll0, round(time.time() - t0)
if __name__ == '__main__':
    tasks = [(v, k) for v in VARS for k in range(NF)]; res = []
    with Pool(2) as pool:
        for r in pool.imap_unordered(job, tasks):
            res.append(r); print(r, flush=True)
    R = pd.DataFrame(res, columns=['var', 'fold', 'nll', 'nll_sat', 's'])
    tot = R.groupby('var')[['nll', 'nll_sat']].sum(); tot['excesso'] = tot.nll - tot.nll_sat
    print(tot.round(1).to_string())
    best = tot.excesso.idxmin(); print('MELHOR', best)
    json.dump(dict(tabela=tot.round(2).reset_index().to_dict('records'), melhor=best), open('cv_resultado.json', 'w'), indent=1)
