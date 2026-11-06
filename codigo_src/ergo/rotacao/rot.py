"""Estudo de rotacao no plano (0 < L <= L0): absortividade com sentido do par e queda livre com rotacao rigida.
Com L = 0 e s = +1, as duas tarefas reproduzem exatamente run_absorb4.task e escada/run_age.task (mesmas sementes).
L e dado como lam = L / L0, com L0 = sqrt(k_B / (-2E)) do par principal (o mais pesado), k_B = mu_B (m_a m_b)^2, G = 1."""
import os, sys, numpy as np
_aqui = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [os.path.join(_aqui, '..'), os.path.join(_aqui, '..', 'escada')]
from sim2 import integrate_ar, PAIRS, initial_conditions
import run_absorb2 as R2
import run_episodes as RE
from segs2 import counts_all
import run_age as ER
import sim2r
E0 = -1.0
def kB(ma, mb): return ma * mb / (ma + mb) * (ma * mb) ** 2
def kB_principal(m):
    m = sorted(m); return kB(m[1], m[2])
# ---------------- absortividade: par (ma, mb) com sentido s, corpo ms chegando de rf * aB, L total = lam * L0
def state(x, e, m, rng, rf, Ltot, s):
    ma, mb, ms = m; mB = ma + mb; M = mB + ms
    EB = x * E0; Es = E0 - EB
    aB = ma * mb / (2 * abs(EB)); muB = ma * mb / mB
    lB = muB * np.sqrt(mB * aB * (1 - e * e))
    mus = ms * mB / M; k = ms * mB; a_s = k / (2 * Es); ls = Ltot - s * lB          # L_F = L - L_B
    es = np.sqrt(1 + ls * ls / (mus * mus * M * a_s)); q = a_s * (es - 1)
    r0 = rf * aB
    if q >= r0: return None                                                       # chegada sem alcance: A = 0
    Mm = rng.uniform(0, 2 * np.pi); Ek = R2.kep(Mm, e); w = rng.uniform(0, 2 * np.pi)
    xb = aB * (np.cos(Ek) - e); yb = aB * np.sqrt(1 - e * e) * np.sin(Ek)
    n = np.sqrt(mB / aB ** 3); Ed = n / (1 - e * np.cos(Ek))
    vxb = -aB * np.sin(Ek) * Ed; vyb = aB * np.sqrt(1 - e * e) * np.cos(Ek) * Ed
    if s < 0: yb, vyb = -yb, -vyb                                                 # par girando no sentido oposto
    c, sn = np.cos(w), np.sin(w); rb = np.array([c * xb - sn * yb, sn * xb + c * yb]); vb = np.array([c * vxb - sn * vyb, sn * vxb + c * vyb])
    cosf = (a_s * (es * es - 1) / r0 - 1) / es; f = -np.arccos(np.clip(cosf, -1, 1)); p = a_s * (es * es - 1)
    rr = np.array([r0 * np.cos(f), -r0 * np.sin(f)]); vr = np.sqrt(k / mus / p) * np.array([-np.sin(f), -(es + np.cos(f))])   # L_F < 0
    if ls > 0: rr[1], vr[1] = -rr[1], -vr[1]                                      # espelha a chegada para L_F > 0
    X = np.zeros((3, 2)); V = np.zeros((3, 2))
    X[0] = -mb / mB * rb; X[1] = ma / mB * rb; V[0] = -mb / mB * vb; V[1] = ma / mB * vb; X[2] = rr; V[2] = vr
    w8 = np.array([ma, mb, ms])[:, None]; X -= (w8 * X).sum(0) / M; V -= (w8 * V).sum(0) / M
    return np.r_[X.ravel(), V.ravel()]
def task_abs(a):
    """a = (x, e, rep, m, rf, Ltot, s, semente_extra). Ltot absoluto (E0 = -1)."""
    x, e, rep, m, rf, Ltot, s, extra = a; mm = np.array(m, float)
    seed = 30_000_000 + int(x * 1000) * 10000 + int(e * 1000) * 10 + rep * 7919 + int(sum(v * 10 ** i for i, v in enumerate(m))) + int(rf) + extra
    rng = np.random.default_rng(seed)
    st = state(x, e, m, rng, rf, Ltot, s)
    if st is None: return dict(x=x, e=e, s=s, rep=rep, ok=0, alcance=0)
    M = mm.sum(); tcr = M ** 2.5 / (2 * abs(E0)) ** 1.5
    out = integrate_ar(st, mm, 300 * tcr, 0.01 * tcr, 1e-12, PAIRS, 200_000, 40_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    nD, nDf, nDl, nx, nS, nSf, nSl = counts_all(rec, mm, E0)
    return dict(x=x, e=e, s=s, rep=rep, ok=1, alcance=1, status=int(status), esc=int(esc), T=(t_ej if status == 1 else t_end) / tcr,
                nD=nD, nDf=nDf, nexc=nx, nS=nS, nSf=nSf, dE=dE)
# ---------------- queda livre com rotacao rigida: mesmas posicoes do ensemble frio, v = omega z x r
def build_rot(x, m, lam):
    x = x - (m[:, None] * x).sum(0) / m.sum()
    W = -sum(m[i] * m[j] / np.linalg.norm(x[i] - x[j]) for i, j in ((0, 1), (0, 2), (1, 2)))
    I = (m * (x ** 2).sum(1)).sum(); k = kB_principal(m)
    disc = W * W - lam * lam * k / I
    if disc < 0: return None
    y = abs(W) - np.sqrt(disc)                                    # y = omega^2 I; resolve L = lam * L0(E) com E = W + y/2
    om = np.sqrt(y / I); v = om * np.c_[-x[:, 1], x[:, 0]]
    E = W + 0.5 * (m * (v ** 2).sum(1)).sum(); L = (m * (x[:, 0] * v[:, 1] - x[:, 1] * v[:, 0])).sum()
    y0 = np.r_[x.ravel(), v.ravel()]; tcr = m.sum() ** 2.5 / (2 * abs(E)) ** 1.5
    return y0, E, tcr, L
def task_age(a):
    mset, i, lam, base = a; mm = np.array(mset, float)
    rng = np.random.default_rng(base + i)
    while True:                                                   # sorteio como no ensemble frio; repete so se lam for inalcancavel
        x, v = initial_conditions(rng, mm, 'frio'); b = build_rot(x, mm, lam)
        if b is not None: break
    y0, E, tcr, L = b
    out = sim2r.integrate_ar(y0, mm, 1000 * tcr, 0.01 * tcr, 1e-12, PAIRS, 400_000, 80_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    sent = int(np.sign(ecc)) if status == 1 else 0; ecc = abs(ecc)
    rows = RE.episodes(rec, mm, E, status, esc, t_end, tcr); ee = ER.exc_ecc(rec, mm, E)
    s = '-'.join('%g' % v for v in mset); T = (t_ej if status == 1 else t_end) / tcr
    q = 0
    for r in rows:
        if r['exit'] == 'exc': r['e_exit'] = ee[q] if q < len(ee) else np.nan; q += 1
        else: r['e_exit'] = ecc if status == 1 else np.nan
        r.update(set=s, run=i, lam=lam, sentido=sent if r['exit'] == 'esc' else 0, L=L, E=E, T=T, n_epis=len(rows), status=int(status), stride=int(stride), dE=dE)
    return rows
