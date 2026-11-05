"""Criterios de Manwadkar, Trani e Kol (2024), adaptados ao plano:
configuracao democratica = raio de homologia modificado 3 r_min^2 / sum r_ij^2 sobe acima de 0,33 e volta abaixo;
excursao = par mais ligado com terceiro corpo ligado (E_k = E0 - E_par < 0), alem do raio de mare
R > (2 m_bin m3 / (m1 m2))^(1/3) * 2a, por mais de um periodo mediano do binario."""
import numpy as np
from sim2 import PAIRS
def counts(rec, m, E0, thrH=0.33):
    t = rec[:, 0]; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]; r = rec[:, 7:10]
    RH = 3 * r.min(1) ** 2 / (r ** 2).sum(1)
    up = RH > thrH
    # indices de fim de cada configuracao democratica (descida)
    dem = np.where(up[:-1] & ~up[1:])[0] + 1
    p = np.argmin(Ep, 1); idx = np.arange(len(t))
    i_ = PAIRS[p, 0]; j_ = PAIRS[p, 1]; mi = m[i_]; mj = m[j_]; mk = m[p]
    E = Ep[idx, p]
    with np.errstate(divide='ignore', invalid='ignore'):
        a = np.where(E < 0, -mi * mj / (2 * E), np.inf)
    Rt = (2 * (mi + mj) * mk / (mi * mj)) ** (1 / 3) * 2 * a
    cand = (E < 0) & (E0 - E < 0) & (Rk[idx, p] > Rt)
    exc = []; k = 0; n = len(t)
    while k < n:
        if cand[k]:
            j = k
            while j + 1 < n and cand[j + 1] and p[j + 1] == p[k]: j += 1
            P = 2 * np.pi * np.sqrt(np.median(a[k:j + 1]) ** 3 / (mi[k] + mj[k]))
            if t[j] - t[k] > P: exc.append((k, j))
            k = j + 1
        else: k += 1
    nD = len(dem)
    first = int((dem < exc[0][0]).sum()) if exc else nD
    last = int((dem > exc[-1][1]).sum()) if exc else nD
    return nD, first, last, len(exc)
def counts_all(rec, m, E0, thrH=0.33):
    """(nD, nD_first, nD_last, n_exc, nS, nS_first, nS_last): configuracoes democraticas e embaralhamentos
    (fases sem par com terceiro alem de 2a), no total, antes da primeira excursao e depois da ultima."""
    t = rec[:, 0]; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]; r = rec[:, 7:10]
    RH = 3 * r.min(1) ** 2 / (r ** 2).sum(1); up = RH > thrH
    dem = np.where(up[:-1] & ~up[1:])[0] + 1
    prod = np.array([m[PAIRS[q, 0]] * m[PAIRS[q, 1]] for q in range(3)])
    with np.errstate(divide='ignore', invalid='ignore'):
        apq = np.where(Ep < 0, -prod / (2 * Ep), np.inf)
    binex = ((Ep < 0) & (Rk > 2 * apq)).any(1)
    scr = np.where(binex[:-1] & ~binex[1:])[0] + 1
    if not binex[0]: scr = np.r_[0, scr]
    p = np.argmin(Ep, 1); idx = np.arange(len(t))
    i_ = PAIRS[p, 0]; j_ = PAIRS[p, 1]; mi = m[i_]; mj = m[j_]; mk = m[p]
    E = Ep[idx, p]
    with np.errstate(divide='ignore', invalid='ignore'):
        a = np.where(E < 0, -mi * mj / (2 * E), np.inf)
    Rt = (2 * (mi + mj) * mk / (mi * mj)) ** (1 / 3) * 2 * a
    cand = (E < 0) & (E0 - E < 0) & (Rk[idx, p] > Rt)
    exc = []; k = 0; n = len(t)
    while k < n:
        if cand[k]:
            j = k
            while j + 1 < n and cand[j + 1] and p[j + 1] == p[k]: j += 1
            P = 2 * np.pi * np.sqrt(np.median(a[k:j + 1]) ** 3 / (mi[k] + mj[k]))
            if t[j] - t[k] > P: exc.append((k, j))
            k = j + 1
        else: k += 1
    f = lambda ev: (len(ev), int((ev < exc[0][0]).sum()) if exc else len(ev), int((ev > exc[-1][1]).sum()) if exc else len(ev))
    a1 = f(dem); a2 = f(scr)
    return a1[0], a1[1], a1[2], len(exc), a2[0], a2[1], a2[2]
