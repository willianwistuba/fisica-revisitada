"""Problema de tres corpos planar newtoniano (G=1), sem softening.
Integrador DOP853 (coeficientes do scipy) reimplementado em numba.
Registra a cada passo aceito: t, energias de par E_p (p = par oposto ao corpo p),
R_k (distancia do corpo k ao CM do par oposto) e E_k (energia de k relativa a esse CM).
"""
import numpy as np
import numba as nb
from scipy.integrate._ivp import dop853_coefficients as dc

A = np.ascontiguousarray(dc.A[:12, :12]); B = dc.B.copy(); C = dc.C[:12].copy()
E3 = dc.E3.copy(); E5 = dc.E5.copy()
PAIRS = np.array([[1, 2], [0, 2], [0, 1]])  # par p = par que exclui o corpo p


@nb.njit(cache=True, error_model="numpy")
def rhs(y, m, out):
    # y = [x0,y0,x1,y1,x2,y2, vx0,vy0,...]
    for i in range(6):
        out[i] = y[6 + i]
    for i in range(6, 12):
        out[i] = 0.0
    for i in range(3):
        for j in range(i + 1, 3):
            dx = y[2 * j] - y[2 * i]; dy = y[2 * j + 1] - y[2 * i + 1]
            r2 = dx * dx + dy * dy
            ir3 = 1.0 / (r2 * np.sqrt(r2))
            out[6 + 2 * i] += m[j] * dx * ir3; out[7 + 2 * i] += m[j] * dy * ir3
            out[6 + 2 * j] -= m[i] * dx * ir3; out[7 + 2 * j] -= m[i] * dy * ir3


@nb.njit(cache=True, error_model="numpy")
def energy(y, m):
    K = 0.0
    for i in range(3):
        K += 0.5 * m[i] * (y[6 + 2 * i] ** 2 + y[7 + 2 * i] ** 2)
    W = 0.0
    for i in range(3):
        for j in range(i + 1, 3):
            W -= m[i] * m[j] / np.hypot(y[2 * j] - y[2 * i], y[2 * j + 1] - y[2 * i + 1])
    return K + W


@nb.njit(cache=True, error_model="numpy")
def diag(y, m, pairs, Ep, Rk, Ek, RVk, ak):
    """Energias de par, distancia e energia do terceiro corpo."""
    for p in range(3):
        i = pairs[p, 0]; j = pairs[p, 1]; k = p
        mi = m[i]; mj = m[j]; mk = m[k]; M = mi + mj
        rx = y[2 * j] - y[2 * i]; ry = y[2 * j + 1] - y[2 * i + 1]
        vx = y[6 + 2 * j] - y[6 + 2 * i]; vy = y[7 + 2 * j] - y[7 + 2 * i]
        r = np.hypot(rx, ry); mu = mi * mj / M
        E = 0.5 * mu * (vx * vx + vy * vy) - mi * mj / r
        Ep[p] = E
        ak[p] = -mi * mj / (2 * E) if E < 0 else np.inf
        cx = (mi * y[2 * i] + mj * y[2 * j]) / M; cy = (mi * y[2 * i + 1] + mj * y[2 * j + 1]) / M
        cvx = (mi * y[6 + 2 * i] + mj * y[6 + 2 * j]) / M; cvy = (mi * y[7 + 2 * i] + mj * y[7 + 2 * j]) / M
        Rx = y[2 * k] - cx; Ry = y[2 * k + 1] - cy
        Vx = y[6 + 2 * k] - cvx; Vy = y[7 + 2 * k] - cvy
        R = np.hypot(Rx, Ry); muk = mk * M / (mk + M)
        Rk[p] = R
        Ek[p] = 0.5 * muk * (Vx * Vx + Vy * Vy) - mk * M / R
        RVk[p] = Rx * Vx + Ry * Vy


@nb.njit(cache=True, error_model="numpy")
def integrate(y0, m, tmax, rtol, atol, A, B, C, E3, E5, pairs, maxrec, maxsteps):
    n = 12
    y = y0.copy(); t = 0.0
    K = np.zeros((13, n)); f = np.zeros(n); tmp = np.zeros(n); ynew = np.zeros(n)
    rhs(y, m, f)
    E0 = energy(y, m)
    h = 1e-4
    rec = np.zeros((maxrec, 10)); nrec = 0; stride = 1; cnt = 0
    Ep = np.zeros(3); Rk = np.zeros(3); Ek = np.zeros(3); RV = np.zeros(3); ak = np.zeros(3)
    Rm1 = np.full(3, -1.0); Rm2 = np.full(3, -1.0); tm1 = 0.0
    lastmin = np.zeros(3)
    esc = -1; nsteps = 0; status = 0
    diag(y, m, pairs, Ep, Rk, Ek, RV, ak)
    rec[0, 0] = 0.0; rec[0, 1:4] = Ep; rec[0, 4:7] = Rk; rec[0, 7:10] = Ek; nrec = 1
    Rm1[:] = Rk
    while t < tmax:
        if nsteps >= maxsteps:
            status = 2; break
        if t + h > tmax:
            h = tmax - t
        # passo DOP853
        K[0, :] = f
        for s in range(1, 12):
            for q in range(n):
                acc = 0.0
                for r in range(s):
                    acc += A[s, r] * K[r, q]
                tmp[q] = y[q] + h * acc
            rhs(tmp, m, K[s])
        for q in range(n):
            acc = 0.0
            for r in range(12):
                acc += B[r] * K[r, q]
            ynew[q] = y[q] + h * acc
        rhs(ynew, m, K[12])
        e5 = 0.0; e3 = 0.0
        for q in range(n):
            sc = atol + max(abs(y[q]), abs(ynew[q])) * rtol
            a5 = 0.0; a3 = 0.0
            for r in range(13):
                a5 += E5[r] * K[r, q]; a3 += E3[r] * K[r, q]
            e5 += (a5 / sc) ** 2; e3 += (a3 / sc) ** 2
        if e5 == 0.0 and e3 == 0.0:
            en = 0.0
        else:
            en = abs(h) * e5 / np.sqrt((e5 + 0.01 * e3) * n)
        if en < 1.0:
            t += h; y[:] = ynew; f[:] = K[12]; nsteps += 1
            fac = 10.0 if en == 0 else min(10.0, 0.9 * en ** (-1.0 / 8))
            h *= fac
            diag(y, m, pairs, Ep, Rk, Ek, RV, ak)
            # minimos locais de R_k (ultimo pericentro) de forma exata no passo
            for p in range(3):
                if Rm2[p] >= 0 and Rm1[p] < Rm2[p] and Rm1[p] <= Rk[p]:
                    lastmin[p] = tm1
                Rm2[p] = Rm1[p]; Rm1[p] = Rk[p]
            tm1 = t
            cnt += 1
            if cnt >= stride:
                cnt = 0
                if nrec >= maxrec:  # dizima por 2
                    half = nrec // 2
                    for q in range(half):
                        rec[q, :] = rec[2 * q, :]
                    nrec = half; stride *= 2
                rec[nrec, 0] = t; rec[nrec, 1:4] = Ep; rec[nrec, 4:7] = Rk; rec[nrec, 7:10] = Ek
                nrec += 1
            # criterio de ejecao
            for p in range(3):
                if Ep[p] < 0 and Ek[p] > 0 and RV[p] > 0 and Rk[p] > 20.0 * ak[p]:
                    esc = p
            if esc >= 0:
                status = 1
                if cnt != 0:  # garante ultimo ponto registrado
                    if nrec >= maxrec:
                        nrec -= 1
                    rec[nrec, 0] = t; rec[nrec, 1:4] = Ep; rec[nrec, 4:7] = Rk; rec[nrec, 7:10] = Ek
                    nrec += 1
                break
        else:
            h *= max(0.2, 0.9 * en ** (-1.0 / 8))
        if h < 1e-16 * max(1.0, t):
            status = 3; break
    E1 = energy(y, m)
    # excentricidade do par final
    ecc = np.nan; a = np.nan
    if esc >= 0:
        i = pairs[esc, 0]; j = pairs[esc, 1]; M = m[i] + m[j]
        rx = y[2 * j] - y[2 * i]; ry = y[2 * j + 1] - y[2 * i + 1]
        vx = y[6 + 2 * j] - y[6 + 2 * i]; vy = y[7 + 2 * j] - y[7 + 2 * i]
        r = np.hypot(rx, ry); eps = 0.5 * (vx * vx + vy * vy) - M / r
        hh = rx * vy - ry * vx
        ecc = np.sqrt(max(0.0, 1.0 + 2.0 * eps * hh * hh / (M * M)))
        a = -M / (2 * eps)
    tej = lastmin[esc] if esc >= 0 else np.nan
    return status, esc, t, tej, abs((E1 - E0) / E0), ecc, a, nsteps, stride, rec[:nrec].copy()


def initial_conditions(rng, m, ensemble):
    while True:
        r = np.sqrt(rng.random(3)); th = 2 * np.pi * rng.random(3)
        x = np.c_[r * np.cos(th), r * np.sin(th)]
        d = [np.linalg.norm(x[i] - x[j]) for i, j in ((0, 1), (0, 2), (1, 2))]
        if min(d) >= 0.1:
            break
    v = rng.normal(size=(3, 2))  # sempre sorteado, para manter a sequencia aleatoria comum
    return x, v


def build_state(x, v, m, ensemble):
    x = x - (m[:, None] * x).sum(0) / m.sum()
    W = -sum(m[i] * m[j] / np.linalg.norm(x[i] - x[j]) for i, j in ((0, 1), (0, 2), (1, 2)))
    if ensemble == 'frio':
        v = np.zeros((3, 2))
    else:
        v = v - (m[:, None] * v).sum(0) / m.sum()
        Kin = 0.5 * (m * (v ** 2).sum(1)).sum()
        v = v * np.sqrt(0.5 * abs(W) / Kin)  # Q = K/|W| = 0.5
    y0 = np.r_[np.c_[x[:, 0], x[:, 1]].ravel(), np.c_[v[:, 0], v[:, 1]].ravel()]
    E = W + 0.5 * (m * (v ** 2).sum(1)).sum()
    tcr = m.sum() ** 2.5 / (2 * abs(E)) ** 1.5
    return y0, E, tcr


def run_one(m, ensemble, seed, tcap=2000.0, rtol=1e-11, atol=1e-12, maxrec=1_000_000, maxsteps=50_000_000):
    m = np.asarray(m, float)
    rng = np.random.default_rng(seed)
    x, v = initial_conditions(rng, m, ensemble)
    y0, E, tcr = build_state(x, v, m, ensemble)
    out = integrate(y0, m, tcap * tcr, rtol, atol, A, B, C, E3, E5, PAIRS, maxrec, maxsteps)
    return dict(zip(['status', 'esc', 't_end', 't_ej', 'dE', 'ecc', 'a', 'nsteps', 'stride', 'rec'], out)), E, tcr


# ---------------------------------------------------------------------------
# Integrador regularizado em coordenadas de cadeia (chain, Mikkola & Aarseth 1993)
# com leapfrog logH (Mikkola & Tanikawa 1999; Preto & Tremaine 1999)
# + extrapolacao de Gragg-Bulirsch-Stoer.
# Estado z = [X1(2), X2(2), W1(2), W2(2), t]; ordem da cadeia perm=(a,b,c):
# X1 = x_b - x_a, X2 = x_c - x_b. O par (a,c) e sempre o mais distante.
# ---------------------------------------------------------------------------


@nb.njit(cache=False, error_model="numpy")
def pd3(R, pairs):
    o = np.zeros(3)
    for p in range(3):
        o[p] = np.hypot(R[pairs[p, 0], pairs[p, 1], 0], R[pairs[p, 0], pairs[p, 1], 1])
    return o

JIT = dict(cache=False, error_model="numpy")


@nb.njit(**JIT)
def chain_rel(z, perm, off, R):
    """R[i,j,:] = vetor x_j - x_i (posicoes se off=0, velocidades se off=4)."""
    a = perm[0]; b = perm[1]; c = perm[2]
    for d in range(2):
        X1 = z[off + d]; X2 = z[off + 2 + d]
        R[a, b, d] = X1; R[b, a, d] = -X1
        R[b, c, d] = X2; R[c, b, d] = -X2
        R[a, c, d] = X1 + X2; R[c, a, d] = -(X1 + X2)
        R[a, a, d] = 0.0; R[b, b, d] = 0.0; R[c, c, d] = 0.0


@nb.njit(**JIT)
def chain_T(z, perm, m):
    a = perm[0]; b = perm[1]; c = perm[2]; M = m[0] + m[1] + m[2]
    T = 0.0
    for d in range(2):
        W1 = z[4 + d]; W2 = z[6 + d]
        va = -(m[b] * W1 + m[c] * (W1 + W2)) / M
        vb = va + W1; vc = vb + W2
        T += 0.5 * (m[a] * va * va + m[b] * vb * vb + m[c] * vc * vc)
    return T


@nb.njit(**JIT)
def chain_acc(z, perm, m, dW):
    """Retorna U e derivadas dW1, dW2."""
    a = perm[0]; b = perm[1]; c = perm[2]
    X1x = z[0]; X1y = z[1]; X2x = z[2]; X2y = z[3]
    Yx = X1x + X2x; Yy = X1y + X2y
    r1 = np.hypot(X1x, X1y); r2 = np.hypot(X2x, X2y); r3 = np.hypot(Yx, Yy)
    U = m[a] * m[b] / r1 + m[b] * m[c] / r2 + m[a] * m[c] / r3
    # forcas por unidade de massa: f_ab = X1/r1^3 etc. (direcao a->b)
    g1 = 1.0 / (r1 * r1 * r1); g2 = 1.0 / (r2 * r2 * r2); g3 = 1.0 / (r3 * r3 * r3)
    # acc_a = m_b X1 g1 + m_c Y g3 ; acc_b = -m_a X1 g1 + m_c X2 g2 ; acc_c = -m_a Y g3 - m_b X2 g2
    for d in range(2):
        X1 = z[d]; X2 = z[2 + d]; Y = X1 + X2
        aa = m[b] * X1 * g1 + m[c] * Y * g3
        ab = -m[a] * X1 * g1 + m[c] * X2 * g2
        ac = -m[a] * Y * g3 - m[b] * X2 * g2
        dW[d] = ab - aa; dW[2 + d] = ac - ab
    return U


@nb.njit(**JIT)
def leapfrog_c(z, perm, m, Bc, H, n, out, dW):
    hs = H / n
    for q in range(9):
        out[q] = z[q]
    dt = 0.5 * hs / (chain_T(out, perm, m) + Bc)
    for q in range(4):
        out[q] += dt * out[4 + q]
    out[8] += dt
    for s in range(n):
        U = chain_acc(out, perm, m, dW)
        dt = hs / U
        for q in range(4):
            out[4 + q] += dt * dW[q]
        fac = 0.5 if s == n - 1 else 1.0
        dt = fac * hs / (chain_T(out, perm, m) + Bc)
        for q in range(4):
            out[q] += dt * out[4 + q]
        out[8] += dt


@nb.njit(**JIT)
def gbs_c(z, perm, m, Bc, H, tol, T, dW, tmp):
    KMAX = 8
    for k in range(KMAX):
        nk = 2 * (k + 1)
        leapfrog_c(z, perm, m, Bc, H, nk, tmp, dW)
        for q in range(9):
            T[k, 0, q] = tmp[q]
        for j in range(1, k + 1):
            nkj = 2 * (k - j + 1)
            r = (nk / nkj) ** 2 - 1.0
            for q in range(9):
                T[k, j, q] = T[k, j - 1, q] + (T[k, j - 1, q] - T[k - 1, j - 1, q]) / r
        if k >= 2:
            err = 0.0
            for v in range(4):  # cada vetor de cadeia escalado pela propria norma
                o = 2 * v
                nrm = np.hypot(T[k, k, o], T[k, k, o + 1]) + 1e-300
                for d in range(2):
                    e = abs(T[k, k, o + d] - T[k, k - 1, o + d]) / nrm
                    if e > err:
                        err = e
            e = abs(T[k, k, 8] - T[k, k - 1, 8]) / max(abs(T[k, k, 8] - z[8]), 1e-300)
            if e > err:
                err = e
            if err < tol:
                return True, k
    return False, KMAX - 1


@nb.njit(**JIT)
def rechain(z, perm, R, V):
    """Garante que o par fora da cadeia seja o mais distante."""
    chain_rel(z, perm, 0, R); chain_rel(z, perm, 4, V)
    d01 = R[0, 1, 0] ** 2 + R[0, 1, 1] ** 2
    d02 = R[0, 2, 0] ** 2 + R[0, 2, 1] ** 2
    d12 = R[1, 2, 0] ** 2 + R[1, 2, 1] ** 2
    if d01 >= d02 and d01 >= d12:
        a, b, c = 0, 2, 1
    elif d02 >= d01 and d02 >= d12:
        a, b, c = 0, 1, 2
    else:
        a, b, c = 1, 0, 2
    if a == perm[0] and b == perm[1] and c == perm[2]:
        return False
    perm[0] = a; perm[1] = b; perm[2] = c
    for d in range(2):
        z[d] = R[a, b, d]; z[2 + d] = R[b, c, d]
        z[4 + d] = V[a, b, d]; z[6 + d] = V[b, c, d]
    return True


@nb.njit(**JIT)
def diag_c(z, perm, m, pairs, R, V, Ep, Rk, Ek, RVk, ak):
    chain_rel(z, perm, 0, R); chain_rel(z, perm, 4, V)
    for p in range(3):
        i = pairs[p, 0]; j = pairs[p, 1]; k = p
        mi = m[i]; mj = m[j]; mk = m[k]; M = mi + mj
        rx = R[i, j, 0]; ry = R[i, j, 1]; vx = V[i, j, 0]; vy = V[i, j, 1]
        r = np.hypot(rx, ry); mu = mi * mj / M
        E = 0.5 * mu * (vx * vx + vy * vy) - mi * mj / r
        Ep[p] = E
        ak[p] = -mi * mj / (2 * E) if E < 0 else np.inf
        # vetor do CM do par ate k
        Rx = (mi * R[i, k, 0] + mj * R[j, k, 0]) / M; Ry = (mi * R[i, k, 1] + mj * R[j, k, 1]) / M
        Vx = (mi * V[i, k, 0] + mj * V[j, k, 0]) / M; Vy = (mi * V[i, k, 1] + mj * V[j, k, 1]) / M
        Rr = np.hypot(Rx, Ry); muk = mk * M / (mk + M)
        Rk[p] = Rr
        Ek[p] = 0.5 * muk * (Vx * Vx + Vy * Vy) - mk * M / Rr
        RVk[p] = Rx * Vx + Ry * Vy


@nb.njit(**JIT)
def chain_E(z, perm, m, dW):
    return chain_T(z, perm, m) - chain_acc(z, perm, m, dW)


@nb.njit(**JIT)
def integrate_ar(y0, m, tmax, dtmax, tol, pairs, maxrec, maxsteps):
    R = np.zeros((3, 3, 2)); V = np.zeros((3, 3, 2)); dW = np.zeros(4)
    # monta cadeia a partir das coordenadas absolutas
    z = np.zeros(9); perm = np.array([0, 1, 2])
    for d in range(2):
        z[d] = y0[2 + d] - y0[d]; z[2 + d] = y0[4 + d] - y0[2 + d]
        z[4 + d] = y0[8 + d] - y0[6 + d]; z[6 + d] = y0[10 + d] - y0[8 + d]
    rechain(z, perm, R, V)
    E0 = chain_E(z, perm, m, dW); Bc = -E0
    tmp = np.zeros(9); T = np.zeros((8, 8, 9))
    H = 1e-3 * (-E0)
    rec = np.zeros((maxrec, 10)); nrec = 0; stride = 1; cnt = 0
    Ep = np.zeros(3); Rk = np.zeros(3); Ek = np.zeros(3); RV = np.zeros(3); ak = np.zeros(3)
    Rm1 = np.full(3, -1.0); Rm2 = np.full(3, -1.0); tm1 = 0.0; tm2 = 0.0
    lastmin = np.zeros(3)
    esc = -1; nsteps = 0; status = 0; nrechain = 0
    diag_c(z, perm, m, pairs, R, V, Ep, Rk, Ek, RV, ak)
    rec[0, 0] = 0.0; rec[0, 1:4] = Ep; rec[0, 4:7] = Rk; rec[0, 7:10] = pd3(R, pairs); nrec = 1
    Rm1[:] = Rk
    while z[8] < tmax:
        if nsteps >= maxsteps:
            status = 2; break
        ok, k = gbs_c(z, perm, m, Bc, H, tol, T, dW, tmp)
        if not ok:
            H *= 0.5
            if H < 1e-300:
                status = 3; break
            continue
        dtstep = T[k, k, 8] - z[8]
        if dtstep > dtmax:
            H *= 0.7 * dtmax / dtstep
            continue
        for q in range(9):
            z[q] = T[k, k, q]
        nsteps += 1
        if k <= 3:
            H *= 1.6
        elif k >= 6:
            H *= 0.7
        if rechain(z, perm, R, V):
            nrechain += 1
        t = z[8]
        diag_c(z, perm, m, pairs, R, V, Ep, Rk, Ek, RV, ak)
        for p in range(3):
            if Rm2[p] >= 0 and Rm1[p] < Rm2[p] and Rm1[p] <= Rk[p]:
                x1 = tm2; x2 = tm1; x3 = t; f1 = Rm2[p]; f2 = Rm1[p]; f3 = Rk[p]
                den = (x1 - x2) * (x1 - x3) * (x2 - x3)
                tv = x2
                if den != 0:
                    A2 = (x3 * (f2 - f1) + x2 * (f1 - f3) + x1 * (f3 - f2)) / den
                    B2 = (x3 * x3 * (f1 - f2) + x2 * x2 * (f3 - f1) + x1 * x1 * (f2 - f3)) / den
                    if A2 > 0:
                        tv = -B2 / (2 * A2)
                if not (tv >= x1 and tv <= x3):
                    tv = x2
                lastmin[p] = tv
            Rm2[p] = Rm1[p]; Rm1[p] = Rk[p]
        tm2 = tm1; tm1 = t
        cnt += 1
        if cnt >= stride:
            cnt = 0
            if nrec >= maxrec:
                half = nrec // 2
                for q in range(half):
                    rec[q, :] = rec[2 * q, :]
                nrec = half; stride *= 2
            rec[nrec, 0] = t; rec[nrec, 1:4] = Ep; rec[nrec, 4:7] = Rk; rec[nrec, 7:10] = pd3(R, pairs)
            nrec += 1
        for p in range(3):
            if Ep[p] < 0 and Ek[p] > 0 and RV[p] > 0 and Rk[p] > 20.0 * ak[p]:
                esc = p
        if esc >= 0:
            status = 1
            if cnt != 0:
                if nrec >= maxrec:
                    nrec -= 1
                rec[nrec, 0] = t; rec[nrec, 1:4] = Ep; rec[nrec, 4:7] = Rk; rec[nrec, 7:10] = pd3(R, pairs)
                nrec += 1
            break
    E1 = chain_E(z, perm, m, dW)
    ecc = np.nan; aa = np.nan
    if esc >= 0:
        chain_rel(z, perm, 0, R); chain_rel(z, perm, 4, V)
        i = pairs[esc, 0]; j = pairs[esc, 1]; M = m[i] + m[j]
        rx = R[i, j, 0]; ry = R[i, j, 1]; vx = V[i, j, 0]; vy = V[i, j, 1]
        r = np.hypot(rx, ry); eps = 0.5 * (vx * vx + vy * vy) - M / r
        hh = rx * vy - ry * vx
        ecc = np.sqrt(max(0.0, 1.0 + 2.0 * eps * hh * hh / (M * M)))
        aa = -M / (2 * eps)
    tej = lastmin[esc] if esc >= 0 else np.nan
    return status, esc, z[8], tej, abs((E1 - E0) / E0), ecc, aa, nsteps, stride, rec[:nrec].copy()


def run_one_ar(m, ensemble, seed, tcap=2000.0, tol=1e-12, dtmax_tcr=0.01, maxrec=1_000_000, maxsteps=20_000_000):
    m = np.asarray(m, float)
    rng = np.random.default_rng(seed)
    x, v = initial_conditions(rng, m, ensemble)
    y0, E, tcr = build_state(x, v, m, ensemble)
    out = integrate_ar(y0, m, tcap * tcr, dtmax_tcr * tcr, tol, PAIRS, maxrec, maxsteps)
    return dict(zip(['status', 'esc', 't_end', 't_ej', 'dE', 'ecc', 'a', 'nsteps', 'stride', 'rec'], out)), E, tcr
