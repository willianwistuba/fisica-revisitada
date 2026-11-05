from sim2 import *
from sim2 import nb, JIT, np

@nb.njit(**JIT)
def integrate_stop(y0, m, tmax, dtmax, tol, pairs, maxrec, maxsteps):
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
    chain_rel(z, perm, 0, R); chain_rel(z, perm, 4, V)
    Mt = m[0] + m[1] + m[2]; y = np.zeros(12)
    for a_ in range(3):
        for d in range(2):
            sx = 0.0; sv = 0.0
            for b_ in range(3):
                sx += m[b_] * R[a_, b_, d]; sv += m[b_] * V[a_, b_, d]
            y[2 * a_ + d] = -sx / Mt; y[6 + 2 * a_ + d] = -sv / Mt
    return status, esc, z[8], tej, abs((E1 - E0) / E0), ecc, aa, nsteps, stride, rec[:nrec].copy(), y

