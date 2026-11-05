"""E16: absortividade caotica (Kol 2021), versao planar, massas iguais.
Estado de saida invertido no tempo: binario (x=E_B/E0, e_B) e terceiro corpo chegando em hiperbole com L_s=-l_B
(L total = 0), a partir de r0 = 20 a_B; fase do binario e orientacao sorteadas. Mede-se a fracao que entra em regime caotico."""
import sys, os, time, csv
import numpy as np
from multiprocessing import Pool
from sim import integrate_ar, PAIRS
m = np.ones(3); E0 = -1.0; M = 3.0
def kepler_E(Mm, e):
    E = Mm.copy() if hasattr(Mm, 'copy') else Mm
    E = Mm + e * np.sin(Mm)
    for _ in range(60): E = E - (E - e * np.sin(E) - Mm) / (1 - e * np.cos(E))
    return E
def state(x, e, rng):
    EB = x * E0; Es = E0 - EB
    aB = 1.0 / (2 * abs(EB)); muB = 0.5; mB = 2.0
    lB = muB * np.sqrt(mB * aB * (1 - e * e))
    mus = 2.0 / 3.0; k = 2.0; a_s = k / (2 * Es); ls = -lB
    es = np.sqrt(1 + ls * ls / (mus * mus * M * a_s)); q = a_s * (es - 1)
    r0 = 20 * aB
    if q >= r0: return None
    # binario: anomalia media uniforme, periastro em angulo w
    Mm = rng.uniform(0, 2 * np.pi); Ek = kepler_E(Mm, e); w = rng.uniform(0, 2 * np.pi)
    xb = aB * (np.cos(Ek) - e); yb = aB * np.sqrt(1 - e * e) * np.sin(Ek)
    n = np.sqrt(mB / aB ** 3); Edot = n / (1 - e * np.cos(Ek))
    vxb = -aB * np.sin(Ek) * Edot; vyb = aB * np.sqrt(1 - e * e) * np.cos(Ek) * Edot   # sentido anti-horario: l>0
    c, s = np.cos(w), np.sin(w); rb = np.array([c * xb - s * yb, s * xb + c * yb]); vb = np.array([c * vxb - s * vyb, s * vxb + c * vyb])
    # terceiro corpo: hiperbole horaria (l<0), ramo de chegada, periastro no eixo x
    cosf = (a_s * (es * es - 1) / r0 - 1) / es; f = -np.arccos(np.clip(cosf, -1, 1))
    p = a_s * (es * es - 1); h = abs(ls) / mus
    # orbita horaria: inverte o sinal de f (espelho em y)
    rr = np.array([r0 * np.cos(f), -r0 * np.sin(f)])
    vr = np.sqrt(k / mus / p) * np.array([-np.sin(f), es + np.cos(f)])
    vr = np.array([vr[0], -vr[1]])
    # posicoes absolutas no CM
    xa = -0.5 * rb; xbb = 0.5 * rb; va = -0.5 * vb; vbb = 0.5 * vb
    X = np.array([xa, xbb, np.zeros(2)]); V = np.array([va, vbb, np.zeros(2)])
    X[2] = rr; V[2] = vr
    X[:2] -= rr / 3 * 1; X[2] -= rr / 3; V[:2] -= vr / 3; V[2] -= vr / 3
    # confere L e E
    L = (X[:, 0] * V[:, 1] - X[:, 1] * V[:, 0]).sum()
    y0 = np.r_[X.ravel(), V.ravel()]
    return y0, L, r0
def task(a):
    x, e, rep = a
    rng = np.random.default_rng(10_000_000 + int(x * 1000) * 10000 + int(e * 1000) * 10 + rep * 7919)
    st = state(x, e, rng)
    if st is None: return dict(x=x, e=e, rep=rep, ok=0)
    y0, L, r0 = st
    tcr = M ** 2.5 / (2 * abs(E0)) ** 1.5
    out = integrate_ar(y0, m, 300 * tcr, 0.01 * tcr, 1e-12, PAIRS, 200_000, 40_000_000)
    status, esc, t_end, t_ej, dE, ecc, a_b, nsteps, stride, rec = out
    Ep = rec[:, 1:4]; Rk = rec[:, 4:7]
    with np.errstate(divide='ignore', invalid='ignore'):
        ap = np.where(Ep < 0, -1.0 / (2 * Ep), np.inf)
    binex = ((Ep < 0) & (Rk > 2 * ap)).any(1)
    nscram = int(((~binex[1:]) & binex[:-1]).sum())
    return dict(x=x, e=e, rep=rep, ok=1, L=L, status=int(status), esc=int(esc), T=(t_ej if status == 1 else t_end) / tcr,
                nscram=nscram, ecc_out=ecc, EBf_out=(-0.5 / a_b) / E0 if status == 1 else np.nan, dE=dE)
if __name__ == '__main__':
    N = int(sys.argv[1]); outf = sys.argv[2]
    XS = [1.05, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0]; ES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92, 0.97, 0.995]
    tasks = [(x, e, r) for x in XS for e in ES for r in range(N)]
    np.random.default_rng(2).shuffle(tasks)
    task((2.0, 0.5, 0)); rows = []; t0 = time.time()
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=8)):
            rows.append(r)
            if (j + 1) % 2000 == 0: print(j + 1, len(tasks), round(time.time() - t0), flush=True)
    keys = sorted({k for r in rows for k in r}, key=lambda k: list(rows[-1].keys()).index(k) if k in rows[-1] else 99)
    with open(outf, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    print('ok', round(time.time() - t0), flush=True)
