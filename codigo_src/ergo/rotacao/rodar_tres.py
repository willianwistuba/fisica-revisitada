"""Rodada E63 (PREREGISTRO_TRES.md): 8-21-21, 10-20-20 e 15-15-15 com a rotacao de Dandekar et al. (2026).
Uso:  python rodar_tres.py            (rodada completa; usa todos os nucleos)
      python rodar_tres.py --teste    (confere o ambiente em cerca de 2 min e estima o tempo total)
Saida: pasta saida_E63/ e, no fim, o arquivo resultado_E63.zip para enviar."""
import sys, os, time, csv, zipfile, numpy as np
from multiprocessing import Pool, freeze_support
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [AQUI]
import rot
XS = [1.01, 1.03, 1.05, 1.1, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]
ES = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.92, 0.97, 0.995]
JS = [0.09, 0.07, 0.05, 0.03, 0.02, 0.01, 0.005]
KA = ['x', 'e', 's', 'rep', 'ok', 'alcance', 'status', 'esc', 'T', 'nD', 'nDf', 'nexc', 'nS', 'nSf', 'dE']
KQ = ['set', 'lam', 'run', 'L', 'E', 'T', 'n_epis', 'idx', 't0', 'dur', 'nS', 'nD', 'exit', 'body', 'mbody', 'x', 'exc_dur', 'P_kep', 'e_exit', 'sentido', 'status', 'stride', 'dE']
CONJ = {'8-21-21': (1.0374, [(21., 21., 8.), (8., 21., 21.)]),
        '10-20-20': (1.0488, [(20., 20., 10.), (10., 20., 20.)]),
        '15-15-15': (1.0955, [(15., 15., 15.)])}
fmt = lambda m: ','.join('%g' % v for v in m)
def warm(_):
    rot.task_abs((2.0, 0.5, 0, (1., 3., 1.), 20.0, 0.0, 1, 0)); rot.task_age(((1., 1., 3.), 0, 0.0, 1)); return 0
def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)
def grades():
    return (('abs4_r20', [(x, e, 10_000 * ie + r) for x in XS for ie, e in enumerate(ES) for r in range(200)]),
            ('abs5_cauda', [(x, float(np.sqrt(1 - j * j)), 500_000 + 10_000 * ij + r) for x in XS for ij, j in enumerate(JS) for r in range(200)]))
def teste(pl):
    nome = '8-21-21'; lam, chans = CONJ[nome]; m = (8., 21., 21.); L = lam * np.sqrt(rot.kB_principal(m) / 2)
    ta = [(x, e, r, chans[1], 20.0, L, s, 1) for s in (1, -1) for x in (1.05, 3.0) for e in (0.25, 0.92) for r in range(40)]
    t = time.time(); pl.map(rot.task_abs, ta, chunksize=4); sa = (time.time() - t) / len(ta)
    tq = [(m, i, lam, 1) for i in range(64 * NP // 2)]
    t = time.time(); pl.map(rot.task_age, tq, chunksize=2); sq = (time.time() - t) / len(tq)
    nabs = sum(len(c) for _, c in CONJ.values()) * 2 * (len(XS) * (len(ES) + len(JS)) * 200)
    tot = nabs * sa + 3 * 12_000 * sq
    log(f'ambiente ok: {NP} processos; {sa*1000:.1f} ms por corrida de absortividade, {sq*1000:.1f} ms por queda livre')
    log(f'estimativa da rodada completa: {tot/60:.0f} min ({nabs} corridas de absortividade e 36000 quedas livres)')
if __name__ == '__main__':
    freeze_support()
    NP = os.cpu_count() or 2
    OUT = os.path.join(os.getcwd(), 'saida_E63'); os.makedirs(OUT, exist_ok=True); t0 = time.time()
    with Pool(NP) as pl:
        pl.map(warm, range(NP))
        if '--teste' in sys.argv:
            teste(pl); sys.exit(0)
        for ic, (nome, (lam, _)) in enumerate(CONJ.items()):
            f = os.path.join(OUT, f'age_{nome}_lam{lam}.csv')
            if os.path.exists(f + '.ok'): continue
            mset = tuple(float(v) for v in nome.split('-')); base = 900_000_000 + 1_000_000 * ic
            with open(f, 'w', newline='') as fh:
                w = csv.DictWriter(fh, fieldnames=KQ, extrasaction='ignore'); w.writeheader()
                for rr in pl.imap_unordered(rot.task_age, [(mset, i, lam, base) for i in range(12_000)], chunksize=8):
                    for r in rr: w.writerow(r)
            open(f + '.ok', 'w').close(); log('queda livre', nome, 'ok', round(time.time() - t0), 's')
        for nome, (lam, chans) in CONJ.items():
            Ltot = lam * np.sqrt(rot.kB_principal([float(v) for v in nome.split('-')]) / 2)
            for m in chans:
                for tag, grid in grades():
                    f = os.path.join(OUT, f'{tag}_{fmt(m)}_lam{lam}.csv')
                    if os.path.exists(f + '.ok'): continue
                    tasks = [(x, e, rep, m, 20.0, Ltot, s, 700_000_000_000 + (500_000 if s < 0 else 0)) for x, e, rep in grid for s in (1, -1)]
                    with open(f, 'w', newline='') as fh:
                        w = csv.DictWriter(fh, fieldnames=KA, extrasaction='ignore'); w.writeheader()
                        for r in pl.imap_unordered(rot.task_abs, tasks, chunksize=32): w.writerow(r)
                    open(f + '.ok', 'w').close(); log(tag, fmt(m), 'ok', round(time.time() - t0), 's')
    z = os.path.join(os.getcwd(), 'resultado_E63.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for n in sorted(os.listdir(OUT)):
            if n.endswith('.csv'): zf.write(os.path.join(OUT, n), n)
    log('fim:', round((time.time() - t0) / 60, 1), 'min; envie o arquivo', z)
