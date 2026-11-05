"""E17: absortividade por canal com massas gerais. Corpos 0,1 = binario (ma, mb); corpo 2 = o que chega (ms). L total = 0, E0 = -1."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim import integrate_ar, PAIRS
E0 = -1.0
def kep(Mm, e):
    E = Mm + e * np.sin(Mm)
    for _ in range(60): E = E - (E - e * np.sin(E) - Mm) / (1 - e * np.cos(E))
    return E
def state(x, e, m, rng):
    ma, mb, ms = m; mB = ma + mb; M = mB + ms
    EB = x * E0; Es = E0 - EB
    aB = ma * mb / (2 * abs(EB)); muB = ma * mb / mB
    lB = muB * np.sqrt(mB * aB * (1 - e * e))
    mus = ms * mB / M; k = ms * mB; a_s = k / (2 * Es); ls = -lB
    es = np.sqrt(1 + ls * ls / (mus * mus * M * a_s)); q = a_s * (es - 1)
    r0 = 20 * aB
    if q >= r0: return None
    Mm = rng.uniform(0, 2 * np.pi); Ek = kep(Mm, e); w = rng.uniform(0, 2 * np.pi)
    xb = aB * (np.cos(Ek) - e); yb = aB * np.sqrt(1 - e * e) * np.sin(Ek)
    n = np.sqrt(mB / aB ** 3); Ed = n / (1 - e * np.cos(Ek))
    vxb = -aB * np.sin(Ek) * Ed; vyb = aB * np.sqrt(1 - e * e) * np.cos(Ek) * Ed
    c, s = np.cos(w), np.sin(w); rb = np.array([c * xb - s * yb, s * xb + c * yb]); vb = np.array([c * vxb - s * vyb, s * vxb + c * vyb])
    cosf = (a_s * (es * es - 1) / r0 - 1) / es; f = -np.arccos(np.clip(cosf, -1, 1)); p = a_s * (es * es - 1)
    rr = np.array([r0 * np.cos(f), -r0 * np.sin(f)])
    vr = np.sqrt(k / mus / p) * np.array([-np.sin(f), -(es + np.cos(f))])
    X = np.zeros((3, 2)); V = np.zeros((3, 2))
    X[0] = -mb / mB * rb; X[1] = ma / mB * rb; V[0] = -mb / mB * vb; V[1] = ma / mB * vb
    X[2] = rr; V[2] = vr
    cx = (np.array([ma, mb, ms])[:, None] * X).sum(0) / M; cv = (np.array([ma, mb, ms])[:, None] * V).sum(0) / M
    X -= cx; V -= cv
    mm = np.array([ma, mb, ms]); L = (mm * (X[:, 0] * V[:, 1] - X[:, 1] * V[:, 0])).sum()
    return np.r_[X.ravel(), V.ravel()], L
def task(a):
    x, e, rep, m = a; mm = np.array(m, float)
    rng = np.random.default_rng(20_000_000 + int(x * 1000) * 10000 + int(e * 1000) * 10 + rep * 7919 + int(sum(v * 10 ** i for i, v in enumerate(m))))
    st = state(x, e, m, rng)
    if st is None: return dict(x=x, e=e, rep=rep, ok=0)
    y0, L = st; M = mm.sum(); tcr = M ** 2.5 / (2 * abs(E0)) ** 1.5
    out = integrate_ar(y0, mm, 300 * tcr, 0.01 * tcr, 1e-12, PAIRS, 200_000, 40_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    Ep = rec[:, 1:4]; Rk = rec[:, 4:7]
    prod = np.array([mm[PAIRS[p, 0]] * mm[PAIRS[p, 1]] for p in range(3)])
    with np.errstate(divide='ignore', invalid='ignore'):
        ap = np.where(Ep < 0, -prod / (2 * Ep), np.inf)
    binex = ((Ep < 0) & (Rk > 2 * ap)).any(1)
    nscram = int(((~binex[1:]) & binex[:-1]).sum())
    return dict(x=x, e=e, rep=rep, ok=1, L=L, status=int(status), esc=int(esc), T=(t_ej if status == 1 else t_end) / tcr, nscram=nscram, dE=dE)
if __name__ == '__main__':
    N = int(sys.argv[1]); m = tuple(float(v) for v in sys.argv[2].split(',')); outf = sys.argv[3]
    XS = [1.05, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0]; ES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92, 0.97, 0.995]
    tasks = [(x, e, r, m) for x in XS for e in ES for r in range(N)]
    np.random.default_rng(2).shuffle(tasks)
    task((2.0, 0.5, 0, m)); rows = []; t0 = time.time()
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=8)): rows.append(r)
    keys = ['x', 'e', 'rep', 'ok', 'L', 'status', 'esc', 'T', 'nscram', 'dE']
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    print(outf, 'ok', round(time.time() - t0), flush=True)
