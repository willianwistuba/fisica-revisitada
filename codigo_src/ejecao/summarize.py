"""Le runs.csv e gera summary.csv + texto com as tabelas."""
import sys
import numpy as np
import pandas as pd
from scipy import stats

f = sys.argv[1] if len(sys.argv) > 1 else 'runs.csv'
d = pd.read_csv(f)
FR = [0.25, 0.5, 0.75, 0.9]; DL = [1, 3, 10, 30]
order = ['1-1-1', '10-10-10', '10-10-10ind', '1-1-3', '1-1-10', '3-3-1', '10-10-1']
rows = []
for name in order:
    for ens in ['frio', 'virial']:
        g = d[(d.mass_set == name) & (d.ensemble == ens)]
        m = np.array([g.m0.iloc[0], g.m1.iloc[0], g.m2.iloc[0]])
        good = g[(g.discard == 0)]
        ejall = good[good.status == 1]
        ej = ejall[ejall.prompt == 0]   # estatisticas de precursor: sem escapes diretos
        unres = good[good.status == 0]
        r = dict(mass_set=name, ensemble=ens, runs=len(g), discarded=int(g.discard.sum()),
                 unresolved=len(unres), ejections=len(ejall), n_prompt=int(ejall.prompt.sum()))
        mesc_all = m[ejall.esc.astype(int).values]
        mesc = m[ej.esc.astype(int).values]
        if len(set(m)) > 1:
            light = mesc_all == m.min()
            r['n_light_ej'] = int(light.sum()); r['frac_light_ej'] = light.mean()
            p3 = m ** -3.0; p3 = p3 / p3.sum(); r['pred_m-3_light'] = p3[m == m.min()].sum()
        else:
            r['n_light_ej'] = np.nan; r['frac_light_ej'] = np.nan; r['pred_m-3_light'] = np.nan
        # por corpo
        for b in range(3):
            r[f'n_esc_body{b}'] = int((ejall.esc == b).sum())
        r['med_t_ej'] = ej.t_ej.median(); r['med_t_ej_tcr'] = ej.t_ej_tcr.median()
        r['t_cr_med'] = g.t_cr.median()
        r['med_lead'] = ej.lead.median(); r['med_lead_tcr'] = ej.lead_tcr.median()
        r['med_lead_frac'] = ej.lead_frac.median(); r['mean_lead_frac'] = ej.lead_frac.mean()
        r['q75_lead_frac'] = ej.lead_frac.quantile(0.75)
        r['frac_lead_gt_0.5'] = (ej.lead_frac > 0.5).mean()
        r['n_locked_from_start'] = int(ej.locked_from_start.sum()); r['n_nolock'] = int(ej.nolock.sum())
        r['med_leadB_tcr'] = ej.leadB_tcr.median(); r['frac_leadB_pos'] = (ej.leadB_tcr > 0).mean()
        r['med_leadB_frac'] = ej.leadB_frac.median()
        r['med_tdet_minus_tej_tcr'] = ej.t_det_minus_tej_tcr.median()
        r['mean_time_frac_mb'] = ej.time_frac_mb.mean()
        for fr in FR:
            r[f'acc_mb_f{fr}'] = ej[f'acc_f{fr}'].mean()
        for D in DL:
            c = ej[f'acc_d{D}'].dropna(); r[f'acc_mb_d{D}'] = c.mean(); r[f'n_d{D}'] = len(c)
        # preditor ingenuo: par final = dois mais pesados (empate dividido igualmente)
        srt = np.sort(m)
        if srt[0] == srt[1] == srt[2]:
            naive = np.full(len(ej), 1 / 3)
        elif srt[0] == srt[1]:   # dois leves iguais: par = pesado + um leve ao acaso
            naive = np.where(mesc == srt[0], 0.5, 0.0)
        else:                    # leve unico
            naive = (mesc == srt[0]).astype(float)
        r['acc_naive'] = naive.mean(); r['chance'] = 1 / 3
        r['mean_attempts'] = ej.attempts.mean(); r['med_attempts'] = ej.attempts.median()
        r['frac_zero_attempts'] = (ej.attempts == 0).mean()
        tr = ej.n_trans.sum(); up = ej.n_trans_up.sum()
        r['frac_trans_binding_up'] = up / tr if tr > 0 else np.nan; r['n_trans'] = int(tr)
        r['med_B_first_over_final'] = ej.B_first_over_final.median()
        r['med_B_last_over_final'] = ej.B_last_over_final.median()
        r['med_within_var'] = ej.within_var_med.median(); r['med_jump'] = ej.jump_med.median()
        e = ejall.ecc.dropna().clip(0, 1)
        r['mean_e'] = e.mean(); r['med_e'] = e.median(); r['frac_e_gt_0.9'] = (e > 0.9).mean()
        r['ks_p_planar'] = stats.kstest(e, lambda x: 1 - np.sqrt(1 - np.clip(x, 0, 1) ** 2)).pvalue
        r['ks_p_thermal'] = stats.kstest(e, lambda x: np.clip(x, 0, 1) ** 2).pvalue
        r['max_dE_kept'] = good.dE.max()
        rows.append(r)
S = pd.DataFrame(rows)
S.to_csv('summary.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 100)
print(S.T.to_string())

# verificacao de escala 1-1-1 x 10-10-10 (mesmas CIs, mesmas sementes)
print('\n== Escala de massa ==')
for ens in ['frio', 'virial']:
    a = d[(d.mass_set == '1-1-1') & (d.ensemble == ens)].set_index('run')
    b = d[(d.mass_set == '10-10-10') & (d.ensemble == ens)].set_index('run')
    print(ens, 't_cr ratio', (b.t_cr / a.t_cr).median(), (b.t_cr / a.t_cr).std())
    both = a[(a.status == 1) & (a.discard == 0)].index.intersection(b[(b.status == 1) & (b.discard == 0)].index)
    same = (a.loc[both, 'esc'] == b.loc[both, 'esc'])
    ratio = (b.loc[both, 't_ej'] / a.loc[both, 't_ej'])
    close = (np.abs(ratio / 10 ** -0.5 - 1) < 1e-3)
    c = d[(d.mass_set == '10-10-10ind') & (d.ensemble == ens)]
    pr = lambda u, v, col: stats.ks_2samp(u[col].dropna(), v[col].dropna()).pvalue
    print(' independente: KS t_ej/t_cr p=%.3f lead_frac p=%.3f e p=%.3f attempts p=%.3f' % (
        pr(a, c, 't_ej_tcr'), pr(a, c, 'lead_frac'), pr(a, c, 'ecc'), pr(a, c, 'attempts')))
    print(' t_ej_tcr mediana 1-1-1 %.2f | 10-10-10 %.2f | 10-10-10ind %.2f' % (a.t_ej_tcr.median(), b.t_ej_tcr.median(), c.t_ej_tcr.median()))
    print(' t_ej absoluto mediana 1-1-1 %.3f | 10-10-10ind %.3f razao %.3f' % (a.t_ej.median(), c.t_ej.median(), c.t_ej.median() / a.t_ej.median()))
    print(' runs ambos ejetaram', len(both), 'mesmo corpo', int(same.sum()), 'razao t_ej = 10^-1/2 (1e-3)', int(close.sum()))
    x = a.loc[a.status == 1, 't_ej_tcr'].dropna(); y = b.loc[b.status == 1, 't_ej_tcr'].dropna()
    print(' KS t_ej/t_cr p =', stats.ks_2samp(x, y).pvalue, ' KS lead_frac p =',
          stats.ks_2samp(a.lead_frac.dropna(), b.lead_frac.dropna()).pvalue,
          ' KS e p =', stats.ks_2samp(a.ecc.dropna(), b.ecc.dropna()).pvalue)
    # ate onde as trajetorias coincidem: fracao com t_ej identico em funcao de t_ej
    for lim in [1, 10, 100]:
        sel = a.loc[both, 't_ej_tcr'] < lim
        print(f'  t_ej<{lim} t_cr: {int(sel.sum())} runs, identicas {int((close & sel).sum())}')
