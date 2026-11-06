"""Analise da E61 (PREREGISTRO_DANDEKAR.md). Uso: python analise_dandekar.py <pasta_dados> [reamostragens=500]. Gera resultado_dandekar.json.
Familia 1: nossas quedas livres (fracao prograda, teste exato com mistura bootstrap; escapes, qui2). Familia 2: numeros publicados
por Dandekar et al. 2026 (Tabelas B.1 e B.3). Exploratorio: KS do formato e previsao cega a emissividade."""
import sys, json, numpy as np, pandas as pd
from scipy import stats
from multiprocessing import Pool
import analise_rot as A
B = A.B
CONJ = {'10-15-20': (1.0567, [((15., 20., 10.), 10., 1), ((10., 20., 15.), 15., 1), ((10., 15., 20.), 20., 1)]),
        '5-15-25': (1.0263, [((15., 25., 5.), 5., 1), ((5., 25., 15.), 15., 1), ((5., 15., 25.), 25., 1)])}
# Dandekar et al. 2026: razao prograda/retrograda (Tab. B.3), fracao do corte ergodico (Tab. B.1), P do mais leve com erro-padrao (Tab. B.1)
DK = {'10-15-20': dict(razao=2.08, frac_es=0.13, p_leve=0.7827, se_leve=0.0011),
      '5-15-25': dict(razao=144.0, frac_es=0.06, p_leve=0.9749, se_leve=0.0006)}
def teste(arg):
    nome, k = arg; lam, chans = CONJ[nome]; rng = np.random.default_rng(61_000 + 10 * k + len(nome))
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
    cnt = np.array([(q.mbody == c[1]).sum() for c in chans]); chi = stats.chisquare(cnt, Pesc * n)
    dk = DK[nome]; fD = dk['razao'] / (1 + dk['razao']); ND = dk['frac_es'] * 1e6
    zf = (fpro - fD) / np.sqrt(fb.var() + fD * (1 - fD) / ND)
    zl = (Pesc[0] - dk['p_leve']) / np.sqrt(Pb[:, 0].var() + dk['se_leve'] ** 2)
    kb = np.array([(ma * mb) ** 3 / (ma + mb) for (ma, mb, ms), _, _ in chans]); cego = kb / kb.sum()
    return dict(conjunto=nome, lam=lam, k=k, n=n, retrogrados=r,
                fracao_prograda_medida=1 - r / n, fracao_prograda_prevista=float(fpro), fracao_prograda_ic95=[float(v) for v in np.quantile(fb, [.025, .975])],
                razao_medida=(n - r) / max(r, 1), razao_prevista=float(fpro / (1 - fpro)), p_prograda=p_pro,
                escapes_medidos=(cnt / n).tolist(), escapes_previstos=Pesc.tolist(), escapes_cegos=cego.tolist(), p_escapes=float(chi.pvalue),
                dk_fracao_prograda=fD, p_dk_prograda=float(2 * stats.norm.sf(abs(zf))), dk_p_leve=dk['p_leve'], p_dk_leve=float(2 * stats.norm.sf(abs(zl))),
                p_leve_previsto=float(Pesc[0]), p_leve_ic95=[float(v) for v in np.quantile(Pb[:, 0], [.025, .975])],
                KS=float(ks), KS_critico95=float(np.quantile(null, .95)), p_KS=float((1 + (null >= ks).sum()) / (B + 1)),
                e_medido=float(obs.mean()), e_previsto=float((np.diff(np.r_[0, c_all]) * A.e).sum()), corridas=int(d.run.nunique()))
if __name__ == '__main__':
    with Pool(2) as pl: res = pl.map(teste, [(n, k) for n in CONJ for k in (3, 4)])
    f1 = [(r, 'p_prograda') for r in res] + [(r, 'p_escapes') for r in res]
    f2 = [(r, 'p_dk_prograda') for r in res] + [(r, 'p_dk_leve') for r in res]
    for fam, nomef in ((f1, 'familia1'), (f2, 'familia2')):
        ok = A.holm(np.array([r[key] for r, key in fam]))
        for (r, key), v in zip(fam, ok): r[f'{key}_passa_holm_{nomef}'] = bool(v)
    json.dump(dict(reamostragens=B, testes=res), open(f'{A.D}/resultado_dandekar.json', 'w'), indent=1, ensure_ascii=False)
    for r in res:
        print(f"{r['conjunto']} k={r['k']} n={r['n']}: prograda {r['fracao_prograda_medida']:.4f}/{r['fracao_prograda_prevista']:.4f} "
              f"(razao {r['razao_medida']:.1f}/{r['razao_prevista']:.1f}) p={r['p_prograda']:.3f} {'ok' if r['p_prograda_passa_holm_familia1'] else 'REPROVA'} | "
              f"escapes {np.round(r['escapes_medidos'], 4).tolist()}/{np.round(r['escapes_previstos'], 4).tolist()} (cego {np.round(r['escapes_cegos'], 4).tolist()}) p={r['p_escapes']:.3f} "
              f"{'ok' if r['p_escapes_passa_holm_familia1'] else 'REPROVA'} | DK prograda {r['dk_fracao_prograda']:.4f} p={r['p_dk_prograda']:.3f} {'ok' if r['p_dk_prograda_passa_holm_familia2'] else 'REPROVA'} | "
              f"DK leve {r['dk_p_leve']:.4f}/{r['p_leve_previsto']:.4f} p={r['p_dk_leve']:.3f} {'ok' if r['p_dk_leve_passa_holm_familia2'] else 'REPROVA'} | "
              f"KS {r['KS']:.3f}/{r['KS_critico95']:.3f} e {r['e_medido']:.3f}/{r['e_previsto']:.3f}")
