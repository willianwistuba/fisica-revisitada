"""Absortividade v3: grade em x refinada perto do limiar, distancia de lancamento configuravel e contagem de embaralhamentos ate a primeira excursao."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim2 import integrate_ar, PAIRS
import run_absorb2 as R2
from segs2 import counts_all
E0 = -1.0
def task(a):
    x, e, rep, m, rf = a; mm = np.array(m, float)
    rng = np.random.default_rng(30_000_000 + int(x * 1000) * 10000 + int(e * 1000) * 10 + rep * 7919 + int(sum(v * 10 ** i for i, v in enumerate(m))) + int(rf))
    old = R2.state.__code__
    st = state(x, e, m, rng, rf)
    if st is None: return dict(x=x, e=e, rep=rep, ok=0)
    y0 = st; M = mm.sum(); tcr = M ** 2.5 / (2 * abs(E0)) ** 1.5
    out = integrate_ar(y0, mm, 300 * tcr, 0.01 * tcr, 1e-12, PAIRS, 200_000, 40_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    nD, nDf, nDl, nx, nS, nSf, nSl = counts_all(rec, mm, E0)
    return dict(x=x, e=e, rep=rep, ok=1, status=int(status), esc=int(esc), T=(t_ej if status == 1 else t_end) / tcr, nD=nD, nDf=nDf, nexc=nx, nS=nS, nSf=nSf, dE=dE)
def state(x, e, m, rng, rf):
    ma, mb, ms = m; mB = ma + mb; M = mB + ms
    EB = x * E0; Es = E0 - EB
    aB = ma * mb / (2 * abs(EB)); muB = ma * mb / mB
    lB = muB * np.sqrt(mB * aB * (1 - e * e))
    mus = ms * mB / M; k = ms * mB; a_s = k / (2 * Es); ls = -lB
    es = np.sqrt(1 + ls * ls / (mus * mus * M * a_s)); q = a_s * (es - 1)
    r0 = rf * aB
    if q >= r0: return None
    Mm = rng.uniform(0, 2 * np.pi); Ek = R2.kep(Mm, e); w = rng.uniform(0, 2 * np.pi)
    xb = aB * (np.cos(Ek) - e); yb = aB * np.sqrt(1 - e * e) * np.sin(Ek)
    n = np.sqrt(mB / aB ** 3); Ed = n / (1 - e * np.cos(Ek))
    vxb = -aB * np.sin(Ek) * Ed; vyb = aB * np.sqrt(1 - e * e) * np.cos(Ek) * Ed
    c, s = np.cos(w), np.sin(w); rb = np.array([c * xb - s * yb, s * xb + c * yb]); vb = np.array([c * vxb - s * vyb, s * vxb + c * vyb])
    cosf = (a_s * (es * es - 1) / r0 - 1) / es; f = -np.arccos(np.clip(cosf, -1, 1)); p = a_s * (es * es - 1)
    rr = np.array([r0 * np.cos(f), -r0 * np.sin(f)]); vr = np.sqrt(k / mus / p) * np.array([-np.sin(f), -(es + np.cos(f))])
    X = np.zeros((3, 2)); V = np.zeros((3, 2))
    X[0] = -mb / mB * rb; X[1] = ma / mB * rb; V[0] = -mb / mB * vb; V[1] = ma / mB * vb; X[2] = rr; V[2] = vr
    w8 = np.array([ma, mb, ms])[:, None]; X -= (w8 * X).sum(0) / M; V -= (w8 * V).sum(0) / M
    return np.r_[X.ravel(), V.ravel()]
if __name__ == '__main__':
    N = int(sys.argv[1]); m = tuple(float(v) for v in sys.argv[2].split(',')); rf = float(sys.argv[3]); outf = sys.argv[4]
    XS = [1.01, 1.03, 1.05, 1.1, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]; ES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92, 0.97, 0.995]
    tasks = [(x, e, r, m, rf) for x in XS for e in ES for r in range(N)]
    np.random.default_rng(2).shuffle(tasks)
    task((2.0, 0.5, 0, m, rf)); rows = []; t0 = time.time()
    with Pool(2) as p:
        for r in p.imap_unordered(task, tasks, chunksize=8): rows.append(r)
    keys = ['x', 'e', 'rep', 'ok', 'status', 'esc', 'T', 'nD', 'nDf', 'nexc', 'nS', 'nSf', 'dE']
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    print(outf, 'ok', round(time.time() - t0), flush=True)
