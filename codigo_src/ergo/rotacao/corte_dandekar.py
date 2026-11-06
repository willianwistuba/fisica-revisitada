"""Exploratorio (E62): sensibilidade da fracao do corpo leve e da fracao prograda ao criterio de selecao, na condicao inicial de Dandekar et al.
Compara cortes por tempo (tau_D >= 80 anos, tau_gap >= 10 anos; tau_D pelo ultimo encontro T ou pela deteccao da fuga) com k >= 3 e 4 embaralhamentos.
Uso: python corte_dandekar.py <pasta com ci_*.csv> [deteccao]"""
import pandas as pd, numpy as np, sys
DK={'5-15-25':(0.9749,0.9931,(-1559.40,45.)), '10-15-20':(0.7827,2.08/3.08,(-1322.53,45.))}
for nome in ('5-15-25','10-15-20'):
    d=pd.read_csv(f'{sys.argv[1]}/ci_{nome}.csv'); E=d.E.iloc[0]; M=45.; tcr=M**2.5/(2*abs(E))**1.5
    last=d.sort_values('idx').groupby('run').tail(1); last=last[(last.exit=='esc')&(last.status==1)].copy()
    if len(sys.argv) > 2 and sys.argv[2] == 'deteccao': last['tau']=(last['t0']+last['dur'])*tcr/(2*np.pi); last['gap']=last['dur']*tcr/(2*np.pi)
    else: last['tau']=last['T']*tcr/(2*np.pi); last['gap']=(last['T']-last['t0'])*tcr/(2*np.pi)
    # escala: nossa E difere da deles; converter tempo pela razao de unidades (mesmas massas e geometria: a=5, d=100)
    m=min(float(v) for v in nome.split('-')); ok=last[(last.tau>=80)&(last.gap>=10)]
    np_=last[last.tau>=30]
    for lab,q in (('nao-prompt',np_),('corte ergodico deles',ok),('k>=3',last[last.nS>=3]),('k>=4',last[last.nS>=4])):
        print(f"{nome} {lab}: n={len(q)} ({100*len(q)/d.run.nunique():.1f}%) leve {(q.mbody==m).mean():.4f} prograda {(q.sentido>0).mean():.4f}")
    print('   publicado: leve %.4f prograda %.4f; tcr deles %.2f anos'%(DK[nome][0],DK[nome][1], 4*np.pi**2*45**2.5/(2*abs(DK[nome][2][0]))**1.5))
    print('   duracao da queda inicial (mediana do 1o episodio, anos): %.1f'%(d[d.idx==0].dur.median()*tcr/(2*np.pi)))
