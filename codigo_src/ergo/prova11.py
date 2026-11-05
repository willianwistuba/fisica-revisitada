"""Prova formal de 95% da formula v10 da absortividade (serie Fisica Revisitada, problema dos tres corpos).

O que faz:
  1. Reajusta a formula nos dados de treino originais (replica 0) e confere se bate com a formula de referencia.
  2. Gera B replicas "bootstrap parametrico": cada celula de treino tem suas absorcoes sorteadas de novo
     (binomial com a fracao medida) e a formula e reajustada. Isso mede quanto a formula oscila por causa
     do numero finito de simulacoes.
  3. Com essas replicas, calcula o valor critico de 95% dos testes de queda livre (formato da dupla final, KS,
     e chances de escape, qui-quadrado), incluindo a incerteza da propria formula, e aplica a correcao de Holm.

Uso (no Prompt de Comando, dentro da pasta do pacote):
  python prova95.py              -> roda tudo (padrao: 40 replicas)
  python prova95.py --replicas 20
  python prova95.py --teste      -> verificacao rapida (so a replica 0, sem o teste final)
O progresso fica salvo na pasta "replicas"; se o programa parar, rode de novo e ele continua de onde parou.
Resultado final: arquivo "resultado_prova95.json" (e o que deve ser enviado de volta).

Requisitos: Python 3.10 ou mais novo, com numpy, scipy e pandas.
"""
import os, sys, json, time, glob, argparse
import numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
from scipy import stats

E0 = -1.0
HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------- variaveis fisicas
def canon(ma, mb, ms):
    hi = np.maximum(ma, mb); lo = np.minimum(ma, mb); return np.ones_like(hi), lo / hi, ms / hi

def peri(x, e, ma, mb, ms):
    """periastro do corpo que chega, em semieixos do par (momento angular total nulo: l_s = -l_B)."""
    mB = ma + mb; M = mB + ms; EB = x * E0; Es = E0 - EB
    aB = ma * mb / (2 * np.abs(EB)); muB = ma * mb / mB
    lB = muB * np.sqrt(mB * aB * (1 - e * e)); mus = ms * mB / M; k = ms * mB
    p = lB ** 2 / (mus ** 2 * M)
    es = np.sqrt(1 + 2 * Es * p / k)
    return (p / (1 + es)) / aB

def feats(x, e, ma, mb, ms):
    x = np.asarray(x, float); e = np.asarray(e, float)
    a, b, c = canon(np.asarray(ma, float), np.asarray(mb, float), np.asarray(ms, float))
    mu = a * b / (a + b); r = c / mu; q = b / a
    Q = peri(x, np.minimum(e, 0.9995), a, b, c)
    return dict(lx=np.log(x), lr=np.log(r), lq=np.log(q), e=e, r=r, x=x, Q=np.minimum(Q, 5.0))

# ----------------------------------------------------------------- formula v10
TL = ['1', 'lx', 'lx2', 'lr', 'lr2', 'lq', 'e', 'L1', 'lx*e', 'lx*lr', 'lq*lr', 'sQ', 'Q', 'Q*lr', 'sQ*lx', 'Q2', 'Q*lq', 'E0', 'E0*lr', 'E0*lq']
VARIANTES_H = {
 'cheia': ['1', 'lx', 'lx2', 'lr', 'lr2', 'lr3', 'lq', 'lq2', 'lq*lr', 'lq*lr2', 'e', 'e2', 'L1', 'lr*e', 'lr2*e', 'lq*e', 'lx*e', 'lx*lr',
           'lr*L1', 'lq*L1', 'E1', 'E1*lr', 'E1*lq', 'E0', 'E0*lr', 'E0*lq'],
 'media': ['1', 'lx', 'lx2', 'lr', 'lr2', 'lq', 'e', 'e2', 'L1', 'lr*e', 'lq*e', 'lx*e', 'lx*lr', 'E1', 'E0', 'E0*lr'],
 'enxuta': ['1', 'lx', 'lr', 'lq', 'e', 'e2', 'L1', 'lr*e', 'lx*e', 'E1', 'E0']}
VARIANTE = os.environ.get('VARIANTE_H', 'cheia')
TH = VARIANTES_H[VARIANTE]
EXTRA = ['w0', 'w_lr', 'w_lx', 'w_lrlx', 'w_w', 'w_rc', 'v_depth', 'v_Q', 'v_sig', 'mix_lr', 'mix_w']
NAMES = ['L_' + t for t in TL] + ['H_' + t for t in TH] + EXTRA

def _vars(Fe):
    lx, lr, lq, e, Q = Fe['lx'], Fe['lr'], Fe['lq'], Fe['e'], Fe['Q']
    v = dict(lx=lx, lr=lr, lq=lq, e=e, Q=Q, L1=np.log(1 - np.minimum(e, 0.9995) ** 2), lx2=lx ** 2, lr2=lr ** 2, lr3=lr ** 3,
             lq2=lq ** 2, e2=e ** 2, Q2=Q ** 2, sQ=np.sqrt(Q), E0=np.exp(-e / 0.15), E1=np.exp(-(1 - e) / 0.04))
    v['1'] = np.ones_like(lx); return v

def _mat(v, terms):
    return np.stack([v[t] if '*' not in t else v[t.split('*')[0]] * v[t.split('*')[1]] for t in terms], -1)

def basis(Fe):
    v = _vars(Fe); return _mat(v, TL), _mat(v, TH)

def A_model(p, Fe, B=None):
    BL, BH = basis(Fe) if B is None else B
    nL, nH = len(TL), len(TH); cL = p[:nL]; cH = p[nL:nL + nH]; P = dict(zip(EXTRA, p[nL + nH:]))
    s = expit((Fe['lr'] - P['mix_lr']) / (0.05 + np.exp(P['mix_w'])))
    z = (1 - s) * (BL @ cL) + s * (BH @ cH)
    Q, lx = Fe['Q'], Fe['lx']
    lr = Fe['lr']
    estar = 0.95 * expit(P['w0'] + P['w_lr'] * lr + P['w_lx'] * lx + P['w_lrlx'] * lr * lx)   # muro em e: depende de r e x, nao do par
    wall = expit((Fe['e'] - estar) / (0.005 + np.exp(P['w_w'])))
    g = expit((P['w_rc'] - lr) / 0.05)                                   # o muro so existe para intruso leve (r < r_c)
    wall = 1 - g * (1 - wall)
    vQ = 0.2 + 0.5 * expit(P['v_Q'])
    vale = 1 - expit(P['v_depth']) * np.exp(-0.5 * ((Q - vQ) / (0.05 + np.exp(P['v_sig']))) ** 2)
    return np.clip(expit(z) * wall * vale, 1e-9, 1 - 1e-9)

def flux_w(x, e):
    w = x ** -2.0 * e / np.sqrt(1 - np.minimum(e, 0.9995) ** 2); return w / w.mean()

def fit(C, K, p0, starts):
    Fe = feats(C.x.values, C.e.values, C.ma.values, C.mb.values, C.ms.values); B = basis(Fe)
    N = C.N.values; W = flux_w(C.x.values, C.e.values)
    def nll(p):
        A = A_model(p, Fe, B); return -(W * (K * np.log(A) + (N - K) * np.log(1 - A))).sum()
    best = None
    for s in range(starts):
        x0 = p0 + (0 if s == 0 else np.random.default_rng(s).normal(0, 0.1, len(p0)))
        r = minimize(nll, x0, method='L-BFGS-B', options=dict(maxiter=40000, maxfun=400000))
        if best is None or r.fun < best.fun: best = r
    return best.x, float(best.fun)

P0 = np.zeros(len(NAMES)); P0[0] = -2; P0[1] = -1.5; P0[len(TL)] = -3; P0[len(TL) + 1] = -1.5
P0[len(TL) + len(TH):] = [-2.3, -3.0, 0.0, 0.0, np.log(0.03), np.log(0.95), 2.4, -0.3, np.log(0.25), np.log(1.4), np.log(0.15)]

# ----------------------------------------------------------------- previsao das quedas livres (fluxo x absortividade)
xg = np.exp(np.linspace(0, np.log(1e3), 900)); ug = (np.arange(700) + .5) / 700; eg = 1 - (1 - ug) ** 2
XG, EG = np.meshgrid(xg, eg, indexing='ij')
BASE = XG ** -2.0 * EG / np.sqrt(1 - EG ** 2) * np.gradient(xg)[:, None] * np.gradient(eg)[None, :]
SETS = {'1-1-3': [((1, 3, 1), 1, 2), ((1, 1, 3), 3, 1)], '3-3-1': [((3, 3, 1), 1, 1), ((3, 1, 3), 3, 2)],
        '1-2-3': [((2, 3, 1), 1, 1), ((1, 3, 2), 2, 1), ((1, 2, 3), 3, 1)]}

def predict(p):
    out = {}
    for name, chans in SETS.items():
        Ws = []
        for (ma, mb, ms), msc, mult in chans:
            Fe = feats(XG, EG, np.full_like(XG, ma), np.full_like(XG, mb), np.full_like(XG, ms))
            Ws.append(mult * (ma * mb) ** 3 / (ma + mb) * BASE * A_model(p, Fe))
        Ps = np.array([W.sum() for W in Ws]); Ps /= Ps.sum(); fe = sum(Ws).sum(0); fe /= fe.sum()
        out[name] = dict(Ps=Ps.tolist(), cdf=np.cumsum(fe).tolist())
    return out

# ----------------------------------------------------------------- tarefas
def run_replica(b):
    fn = os.path.join(HERE, 'replicas', f'rep_{b:03d}.json')
    if os.path.exists(fn): return b, 'ja existia'
    C = pd.read_csv(os.path.join(HERE, 'treino_celulas.csv'))
    t0 = time.time()
    if b == 0:
        K = C.K.values.astype(float); p, f = fit(C, K, P0, 4)
    else:
        ref = json.load(open(os.path.join(HERE, 'replicas', 'rep_000.json')))
        rng = np.random.default_rng(1000 + b)
        K = rng.binomial(C.N.values, C.K.values / C.N.values).astype(float)
        p, f = fit(C, K, np.array(ref['params']), 1)
    res = dict(replica=b, params=p.tolist(), nll=f, segundos=round(time.time() - t0, 1), pred=predict(p))
    json.dump(res, open(fn, 'w'))
    return b, f'{res["segundos"]} s'

def final_test(B):
    ff = pd.read_csv(os.path.join(HERE, 'quedas_livres.csv'))
    reps = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(HERE, 'replicas', 'rep_*.json')))]
    r0 = [r for r in reps if r['replica'] == 0][0]; boot = [r for r in reps if r['replica'] > 0]
    rng = np.random.default_rng(7); rows = []
    for name, chans in SETS.items():
        q = ff[ff.set == name]; n = len(q); obs_e = q.e_exit.values
        cdf0 = np.array(r0['pred'][name]['cdf']); P0s = np.array(r0['pred'][name]['Ps'])
        ks_obs = stats.kstest(obs_e, lambda v: np.interp(v, eg, cdf0)).statistic
        obs = np.array([(q.mbody == c[1]).sum() for c in chans]); chi_obs = (((obs - n * P0s) ** 2) / (n * P0s)).sum()
        ks_null, chi_null = [], []
        for r in boot:
            cdfb = np.array(r['pred'][name]['cdf']); Pb = np.array(r['pred'][name]['Ps'])
            for _ in range(5):
                smp = np.interp(rng.uniform(0, 1, n), cdfb, eg)
                ks_null.append(stats.kstest(smp, lambda v: np.interp(v, eg, cdf0)).statistic)
                cnt = rng.multinomial(n, Pb); chi_null.append((((cnt - n * P0s) ** 2) / (n * P0s)).sum())
        ks_null = np.array(ks_null); chi_null = np.array(chi_null)
        rows.append(dict(conjunto=name, n=n, KS=ks_obs, KS_critico95=float(np.quantile(ks_null, .95)), p_KS=float((ks_null >= ks_obs).mean()),
                         escapes_medidos=(obs / n).tolist(), escapes_formula=P0s.tolist(), chi2=chi_obs,
                         chi2_critico95=float(np.quantile(chi_null, .95)), p_escapes=float((chi_null >= chi_obs).mean())))
    def holm(ps):
        o = np.argsort(ps); m = len(ps); ok = np.ones(m, bool)
        for k, i in enumerate(o):
            if ps[i] <= 0.05 / (m - k): ok[i] = False
            else: break
        return ok
    pk = holm(np.array([r['p_KS'] for r in rows])); pe = holm(np.array([r['p_escapes'] for r in rows]))
    for r, a, b_ in zip(rows, pk, pe): r['formato_passa_holm'] = bool(a); r['escapes_passa_holm'] = bool(b_)
    ref = np.array(list(json.load(open(os.path.join(HERE, 'formula_v11_referencia.json'))).values()))
    out = dict(replicas_bootstrap=len(boot), conferencia_replica0=dict(nll=r0['nll'], diferenca_max_parametros=float(np.abs(np.array(r0['params']) - ref).max())),
               testes=rows, maquina=dict(cpus=os.cpu_count(), python=sys.version.split()[0]))
    json.dump(out, open(os.path.join(HERE, 'resultado_prova95.json'), 'w'), indent=1)
    print('\n================ RESULTADO ================')
    for r in rows:
        print(f"{r['conjunto']}: formato KS {r['KS']:.3f} (critico {r['KS_critico95']:.3f}, p={r['p_KS']:.3f}) -> {'PASSA' if r['formato_passa_holm'] else 'reprovado'} | "
              f"escapes p={r['p_escapes']:.3f} -> {'PASSA' if r['escapes_passa_holm'] else 'reprovado'}")
    print('Arquivo gerado: resultado_prova95.json (envie este arquivo).')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--replicas', type=int, default=40); ap.add_argument('--teste', action='store_true')
    ap.add_argument('--processos', type=int, default=max(1, (os.cpu_count() or 2) // 2))
    a = ap.parse_args(); os.makedirs(os.path.join(HERE, 'replicas'), exist_ok=True)
    print(f'Maquina: {os.cpu_count()} processadores logicos; usando {a.processos} processos em paralelo.')
    t0 = time.time()
    print('Passo 1: ajuste nos dados originais (replica 0)...', flush=True); print('   ', run_replica(0)[1])
    r0 = json.load(open(os.path.join(HERE, 'replicas', 'rep_000.json')))
    ref = np.array(list(json.load(open(os.path.join(HERE, 'formula_v11_referencia.json'))).values()))
    print(f'   conferencia: maior diferenca para a formula de referencia = {np.abs(np.array(r0["params"]) - ref).max():.4f}')
    if a.teste: print('Teste rapido concluido.'); sys.exit(0)
    from multiprocessing import Pool
    todo = list(range(1, a.replicas + 1))
    print(f'Passo 2: {len(todo)} replicas bootstrap...', flush=True)
    with Pool(a.processos) as pool:
        for k, (b, msg) in enumerate(pool.imap_unordered(run_replica, todo), 1):
            print(f'   replica {b:3d} pronta ({msg}) | {k}/{len(todo)} | {round((time.time()-t0)/60,1)} min', flush=True)
    print('Passo 3: teste final com 95% e correcao de Holm...', flush=True)
    final_test(a.replicas)
    print(f'Tempo total: {round((time.time()-t0)/60,1)} min')
