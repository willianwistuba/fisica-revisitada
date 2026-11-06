"""Analise da E60 (PREREGISTRO_CONF.md). Usa teste() de analise_rot.py nos dados novos.
Familia principal: fracao prograda, 2 conjuntos x lam 0,3 e 0,7 x k 3 e 4 (Holm sobre 8).
Familia secundaria: formato do 1-1-3 com lam 0,7, k 3 e 4 (Holm sobre 2). Resto exploratorio (inclui lam 0,1).
Uso: python analise_conf.py <pasta_dados> [reamostragens=500]. Gera resultado_conf.json."""
import sys, json, numpy as np
from multiprocessing import Pool
import analise_rot as A
if __name__ == '__main__':
    args = [(n, l, k) for n in A.CONJ for l in (0.3, 0.7, 0.1) for k in (3, 4)]
    with Pool(2) as pl: res = pl.map(A.teste, args)
    fam1 = [r for r in res if r['lam'] in (0.3, 0.7)]
    for r, v in zip(fam1, A.holm(np.array([r['p_prograda'] for r in fam1]))): r['principal_prograda_passa_holm'] = bool(v)
    fam2 = [r for r in res if r['conjunto'] == '1-1-3' and r['lam'] == 0.7]
    for r, v in zip(fam2, A.holm(np.array([r['p_KS'] for r in fam2]))): r['secundario_formato_passa_holm'] = bool(v)
    json.dump(dict(reamostragens=A.B, testes=res), open(f'{A.D}/resultado_conf.json', 'w'), indent=1, ensure_ascii=False)
    for r in res:
        tag = ''
        if 'principal_prograda_passa_holm' in r: tag += ' | PRINCIPAL ' + ('passa' if r['principal_prograda_passa_holm'] else 'REPROVA')
        if 'secundario_formato_passa_holm' in r: tag += ' | SECUNDARIO formato ' + ('passa' if r['secundario_formato_passa_holm'] else 'REPROVA')
        print(f"{r['conjunto']} lam={r['lam']} k={r['k']} n={r['n']}: prograda {r['fracao_prograda_medida']:.3f}/{r['fracao_prograda_prevista']:.3f} "
              f"(razao {r['razao_pro_ret_medida']:.2f}/{r['razao_pro_ret_prevista']:.2f}) p={r['p_prograda']:.3f} | KS {r['KS']:.3f}/{r['KS_critico95']:.3f} p={r['p_KS']:.3f} | "
              f"e {r['e_medido']:.3f}/{r['e_previsto']:.3f} | escapes p={r['p_escapes']:.3f}{tag}")
