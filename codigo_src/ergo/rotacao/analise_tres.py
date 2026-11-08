"""Analise da E63 (PREREGISTRO_TRES.md): 8-21-21, 10-20-20 e 15-15-15. Uso: python analise_tres.py <pasta saida_E63> [reamostragens=500]. Gera resultado_tres.json.
Familia 1: nossas quedas livres (fracao prograda, teste exato com mistura bootstrap; escapes, qui2). Familia 2: numeros publicados
por Dandekar et al. 2026 (Tabelas B.1 e B.3). Exploratorio: KS do formato e previsao cega a emissividade."""
import sys, json, numpy as np, pandas as pd
from scipy import stats
from multiprocessing import Pool
import analise_rot as A
B = A.B
CONJ = {'8-21-21': (1.0374, [((21., 21., 8.), 8., 1), ((8., 21., 21.), 21., 2)]),
        '10-20-20': (1.0488, [((20., 20., 10.), 10., 1), ((10., 20., 20.), 20., 2)]),
        '15-15-15': (1.0955, [((15., 15., 15.), 15., 3)])}
# Dandekar et al. 2026: razao prograda/retrograda (Tab. B.3), fracao do corte ergodico (Tab. B.1), P do mais leve com erro-padrao (Tab. B.1)
DK = {'8-21-21': dict(razao=12.35, frac_es=0.09, p_leve=0.9428, se_leve=0.0008),
      '10-20-20': dict(razao=3.85, frac_es=0.13, p_leve=0.8735, se_leve=0.0009),
      '15-15-15': dict(razao=0.90, frac_es=0.12, p_leve=None, se_leve=None)}
def teste(arg):
    nome, k = arg; lam, chans = CONJ[nome]; rng = np.random.default_rng(63_000 + 10 * k + len(nome))
    d = pd.read_csv(f'{A.D}/age_{nome}_lam{lam}.csv'); fin = d[(d.exit == 'esc') & (d.status == 1)]
    q = fin[fin.nS >= k]; n = len(q); obs = q.e_exit.values
    tabs = [[A.table(A.load(m, lam), k, s) for s in (1, -1)] for m, _, _ in chans]
    W0 = A.weights(chans, tabs, [[K / N for _, _, K, N in tc] for tc in tabs])
    tot = np.array([[w.sum() for w in ww] for ww in W0]); Pesc = tot.sum(1) / tot.sum(); fpro = tot[:, 0].sum() / tot.sum()
    c_all = A.cdf_of(W0); ks = stats.kstest(obs, lambda v: np.interp(v, A.e, c_all)).statistic
    fb, Pb, null = [], [], []
    for _ in range(B):
        Wb = A.weights(chans, tabs, [[rng.binomial(N.astype(int), K / N) / N for _, _, K, N in tc] for tc in tabs])
        tb = np.array([[w.sum() for w in ww] for ww in Wb]); fb.append(tb[:, 0].sum() / tb.sum()); Pb.append(tb.sum(1) / tb.sum())
        cb = A.cdf_of(Wb); null.append(stats.kstest(np.interp(rng.uniform(0, 1, n), cb, A.e), lambda v: np.interp(v, A.e, c_all)).statistic)
    fb, Pb, null = np.array(fb), np.array(Pb), np.array(null)
    r = int((q.sentido < 0).sum()); pr = 1 - fb                                    # retrogrados contados e previstos
    lo = np.mean(stats.binom.cdf(r, n, pr)); hi = np.mean(stats.binom.sf(r - 1, n, pr)); p_pro = float(min(1.0, 2 * min(lo, hi)))
    cnt = np.array([(q.mbody == c[1]).sum() for c in chans]); p_esc = float(stats.chisquare(cnt, Pesc * n).pvalue) if len(chans) > 1 else None
    dk = DK[nome]; fD = dk['razao'] / (1 + dk['razao']); ND = dk['frac_es'] * 1e6
    zf = (fpro - fD) / np.sqrt(fb.var() + fD * (1 - fD) / ND)
    p_dk_leve = float(2 * stats.norm.sf(abs((Pesc[0] - dk['p_leve']) / np.sqrt(Pb[:, 0].var() + dk['se_leve'] ** 2)))) if dk['p_leve'] else None
    kb = np.array([(ma * mb) ** 3 / (ma + mb) for (ma, mb, ms), _, _ in chans]); cego = kb / kb.sum()
    return dict(conjunto=nome, lam=lam, k=k, n=n, retrogrados=r,
                fracao_prograda_medida=1 - r / n, fracao_prograda_prevista=float(fpro), fracao_prograda_ic95=[float(v) for v in np.quantile(fb, [.025, .975])],
                razao_medida=(n - r) / max(r, 1), razao_prevista=float(fpro / (1 - fpro)), p_prograda=p_pro,
                escapes_medidos=(cnt / n).tolist(), escapes_previstos=Pesc.tolist(), escapes_cegos=cego.tolist(), p_escapes=p_esc,
                dk_fracao_prograda=fD, p_dk_prograda=float(2 * stats.norm.sf(abs(zf))), dk_p_leve=dk['p_leve'], p_dk_leve=p_dk_leve,
                p_leve_previsto=float(Pesc[0]), p_leve_ic95=[float(v) for v in np.quantile(Pb[:, 0], [.025, .975])],
                KS=float(ks), KS_critico95=float(np.quantile(null, .95)), p_KS=float((1 + (null >= ks).sum()) / (B + 1)),
                e_medido=float(obs.mean()), e_previsto=float((np.diff(np.r_[0, c_all]) * A.e).sum()), corridas=int(d.run.nunique()))
if __name__ == '__main__':
    with Pool(2) as pl: res = pl.map(teste, [(n, k) for n in CONJ for k in (3, 4)])
    f1 = [(r, 'p_prograda') for r in res] + [(r, 'p_escapes') for r in res if r['p_escapes'] is not None]
    f2 = [(r, 'p_dk_prograda') for r in res] + [(r, 'p_dk_leve') for r in res if r['p_dk_leve'] is not None]
    for fam, nomef in ((f1, 'familia1'), (f2, 'familia2')):
        ok = A.holm(np.array([r[key] for r, key in fam]))
        for (r, key), v in zip(fam, ok): r[f'{key}_passa_holm_{nomef}'] = bool(v)
    json.dump(dict(reamostragens=B, testes=res), open(f'{A.D}/resultado_tres.json', 'w'), indent=1, ensure_ascii=False)
    for r in res:
        for kk in ('p_escapes', 'p_dk_leve', 'dk_p_leve'):
            r.setdefault(kk, None)
        print(json.dumps({k: r.get(k) for k in ('conjunto', 'k', 'n', 'fracao_prograda_medida', 'fracao_prograda_prevista', 'razao_medida', 'razao_prevista', 'p_prograda',
              'p_prograda_passa_holm_familia1', 'escapes_medidos', 'escapes_previstos', 'p_escapes', 'p_escapes_passa_holm_familia1', 'dk_fracao_prograda', 'p_dk_prograda',
              'p_dk_prograda_passa_holm_familia2', 'dk_p_leve', 'p_leve_previsto', 'p_dk_leve', 'p_dk_leve_passa_holm_familia2', 'KS', 'KS_critico95', 'e_medido', 'e_previsto')}, ensure_ascii=False))
        continue
        print(f"{r['conjunto']} k={r['k']} n={r['n']}: prograda {r['fracao_prograda_medida']:.4f}/{r['fracao_prograda_prevista']:.4f} "
              f"(razao {r['razao_medida']:.1f}/{r['razao_prevista']:.1f}) p={r['p_prograda']:.3f} {'ok' if r['p_prograda_passa_holm_familia1'] else 'REPROVA'} | "
              f"escapes {np.round(r['escapes_medidos'], 4).tolist()}/{np.round(r['escapes_previstos'], 4).tolist()} (cego {np.round(r['escapes_cegos'], 4).tolist()}) p={r['p_escapes']:.3f} "
              f"{'ok' if r['p_escapes_passa_holm_familia1'] else 'REPROVA'} | DK prograda {r['dk_fracao_prograda']:.4f} p={r['p_dk_prograda']:.3f} {'ok' if r['p_dk_prograda_passa_holm_familia2'] else 'REPROVA'} | "
              f"DK leve {r['dk_p_leve']:.4f}/{r['p_leve_previsto']:.4f} p={r['p_dk_leve']:.3f} {'ok' if r['p_dk_leve_passa_holm_familia2'] else 'REPROVA'} | "
              f"KS {r['KS']:.3f}/{r['KS_critico95']:.3f} e {r['e_medido']:.3f}/{r['e_previsto']:.3f}")
