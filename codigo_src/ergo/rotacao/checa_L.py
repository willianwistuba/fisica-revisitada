import numpy as np, rot
from sim2 import initial_conditions
Lz = lambda y, m: (m * (y[:6].reshape(3, 2)[:, 0] * y[6:].reshape(3, 2)[:, 1] - y[:6].reshape(3, 2)[:, 1] * y[6:].reshape(3, 2)[:, 0])).sum()
XS = [1.01, 1.03, 1.05, 1.1, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]; ES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92, 0.97, 0.995]
for conj, canais in (('1-1-3', [(1., 3., 1.), (1., 1., 3.)]), ('1-2-3', [(2., 3., 1.), (1., 3., 2.), (1., 2., 3.)])):
    m = [float(v) for v in conj.split('-')]; L0 = np.sqrt(rot.kB_principal(m) / 2)
    for lam in (0.3, 0.7):
        L = lam * L0; err = 0; sem = {}
        for ch in canais:
            for s in (1, -1):
                n0 = 0
                for x in XS:
                    for e in ES:
                        st = rot.state(x, e, ch, np.random.default_rng(1), 20.0, L, s)
                        if st is None: n0 += 1
                        else: err = max(err, abs(Lz(st, np.array(ch)) - L))
                sem[f'{ch} s={s:+d}'] = n0
        print(conj, f'lam={lam}', f'L0={L0:.3f}', f'erro max de L = {err:.1e}', 'celulas sem alcance (de 132):', sem)
    for lam in (0.3, 0.7):
        rng = np.random.default_rng(5); mm = np.array(m); fail = 0; Ls = []
        for i in range(2000):
            x, v = initial_conditions(rng, mm, 'frio'); b = rot.build_rot(x, mm, lam)
            if b is None: fail += 1
            else: Ls.append(b[3] / np.sqrt(rot.kB_principal(m) / (-2 * b[1])))
        print(f'   queda livre lam={lam}: posicoes sem solucao {fail}/2000; L/L0 obtido {np.min(Ls):.6f} a {np.max(Ls):.6f}')
