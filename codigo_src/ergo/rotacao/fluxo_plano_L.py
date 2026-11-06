"""Peso do fluxo plano com rotacao total L (Kol 2021; Dandekar et al. 2026, eq. 10).
Medida do fluxo: dphi_F dE_F dL_F * dphi_B dE_B dL_B T(E_B) * delta(E_B+E_F-E) delta(L_B+L_F-L).
Integrando E_F, L_F e os angulos sobra (2pi)^3 dL_s dL_B, com L_s = sqrt(k_B/(-2E_B)) e |L_B| <= L_s.
Em (x = E_B/E, e, s = sentido de L_B em relacao a L): dL_s dL_B = (L0^2/2) x^-2 e/sqrt(1-e^2) dx de, para cada s.
O peso nao depende de L: a rotacao so entra por L_F = L - s L_s sqrt(1-e^2), isto e, pela absortividade A(x, e, s; L).
Este script confere a troca de variaveis por Monte Carlo e o total (2pi)^3 L0^2."""
import numpy as np
rng = np.random.default_rng(1)
L0 = 1.0; n = 4_000_000
# sorteio uniforme na regiao |L_B| <= L_s <= L0 do plano (L_s, L_B): densidade constante = medida do fluxo
Ls = L0 * np.sqrt(rng.uniform(0, 1, n)); LB = Ls * rng.uniform(-1, 1, n)       # area total = L0^2
x = (L0 / Ls) ** 2; e = np.sqrt(1 - (LB / Ls) ** 2); s = np.sign(LB)
area = L0 ** 2
xe = np.exp(np.linspace(0, np.log(50), 26)); ee = np.linspace(0, 1, 21)
for sg in (1, -1):
    H, _, _ = np.histogram2d(x[s == sg], e[s == sg], bins=[xe, ee])
    dens_mc = H / n * area / np.diff(xe)[:, None] / np.diff(ee)[None, :]
    # previsao analitica integrada na celula, dividida pela area da celula
    Fx = lambda v: -1 / v; Fe = lambda v: -np.sqrt(1 - v ** 2)
    ana = 0.5 * L0 ** 2 * np.diff(Fx(xe))[:, None] * np.diff(Fe(ee))[None, :] / np.diff(xe)[:, None] / np.diff(ee)[None, :]
    exp = ana * np.diff(xe)[:, None] * np.diff(ee)[None, :] / area * n; ok = exp > 20
    chi = ((H - exp) ** 2 / exp)[ok].sum(); from scipy import stats
    print(f'sentido {sg:+d}: qui2/gl = {chi / ok.sum():.3f} em {ok.sum()} celulas, p = {stats.chi2.sf(chi, ok.sum()):.2f}')
print('total analitico 2 sentidos x (L0^2/2) x int x^-2 dx (1..inf) x int e/sqrt(1-e^2) de (0..1) =', 2 * 0.5 * 1 * 1, '(= L0^2)')
print('reducao a L = 0: peso por (x, e) somando os sentidos = L0^2 x^-2 e/sqrt(1-e^2), o BASE de analise_v2.py')
