"""Executa os ensembles e grava runs.csv (uma linha por simulacao)."""
import sys, time, csv
import numpy as np
from multiprocessing import Pool
from sim import run_one_ar

MASS_SETS = {'1-1-1': (1, 1, 1), '10-10-10': (10, 10, 10), '1-1-3': (1, 1, 3),
             '1-1-10': (1, 1, 10), '3-3-1': (3, 3, 1), '10-10-1': (10, 10, 1),
             '10-10-10ind': (10, 10, 10)}  # 10-10-10ind: sementes independentes
SEED_OFFSET = {'10-10-10ind': 500_000}
ENSEMBLES = ['frio', 'virial']
FRACS = [0.25, 0.5, 0.75, 0.9]
DELTAS = [1, 3, 10, 30]  # antecedencia absoluta em t_cr
TCAP = 2000.0
TOL = 1e-13


def analyse(o, m, tcr):
    row = {}
    k = int(o['esc'])
    rec = o['rec']; t = rec[:, 0]; Ep = rec[:, 1:4]; Rk = rec[:, 4:7]; Ek = rec[:, 7:10]
    tej = o['t_ej']
    nej = int(np.searchsorted(t, tej, 'right') - 1)
    nej = max(nej, 0)
    mb = np.argmin(Ep, axis=1)
    # (1) travamento
    if mb[nej] != k:
        tlock = tej; nolock = 1
    else:
        nolock = 0
        bad = np.nonzero(mb[:nej + 1] != k)[0]
        tlock = 0.0 if len(bad) == 0 else t[bad[-1] + 1]
    lead = tej - tlock
    row.update(t_lock=tlock, lead=lead, lead_frac=lead / tej if tej > 0 else np.nan,
               lead_tcr=lead / tcr, nolock=nolock, locked_from_start=int(nolock == 0 and tlock == 0.0))
    # variante B: travamento avaliado ate a deteccao (t_det); antecedencia pode ser negativa
    badB = np.nonzero(mb != k)[0]
    tlockB = 0.0 if len(badB) == 0 else t[badB[-1] + 1]
    row.update(t_lockB=tlockB, leadB_tcr=(tej - tlockB) / tcr,
               leadB_frac=(tej - tlockB) / tej if tej > 0 else np.nan,
               t_det_minus_tej_tcr=(t[-1] - tej) / tcr)
    # fracao do tempo (ponderada) em que o par final e o mais ligado
    if nej > 0:
        dt = np.diff(t[:nej + 1]); row['time_frac_mb'] = float((dt * (mb[:nej] == k)).sum() / dt.sum())
    else:
        row['time_frac_mb'] = np.nan
    # (2) preditor em fracoes de t_ej e a antecedencias absolutas
    for f in FRACS:
        n = int(np.searchsorted(t, f * tej, 'right') - 1)
        row[f'acc_f{f}'] = int(mb[max(n, 0)] == k)
    for D in DELTAS:
        tt = tej - D * tcr
        if tt < 0:
            row[f'acc_d{D}'] = np.nan
        else:
            n = int(np.searchsorted(t, tt, 'right') - 1)
            row[f'acc_d{D}'] = int(mb[max(n, 0)] == k)
    # (3) tentativas de ejecao
    af = o['a']
    above = Rk[:nej + 1, k] > 5 * af
    att = 0; Bseq = []; wvar = []
    n = 0; N = len(above)
    while n < N:
        if above[n]:
            s = n
            while n < N and above[n]:
                n += 1
            e = n  # segmento [s, e)
            if s > 0 and e < N:  # comecou depois de t=0 e voltou antes de t_ej
                seg = slice(s, e)
                napo = s + int(np.argmax(Rk[seg, k]))
                if Ek[napo, k] < 0 and Ep[napo, k] < 0:
                    att += 1
                    Bseq.append(-Ep[napo, k])
                    ee = Ep[seg, k]
                    wvar.append((ee.max() - ee.min()) / abs(ee.mean()))
        else:
            n += 1
    Bf = -Ep[-1, k]
    Bseq.append(Bf)
    Bseq = np.array(Bseq)
    row['attempts'] = att
    if att > 0:
        d = np.diff(Bseq)
        row['n_trans'] = len(d); row['n_trans_up'] = int((d > 0).sum())
        row['B_first_over_final'] = Bseq[0] / Bf
        row['B_last_over_final'] = Bseq[-2] / Bf
        row['jump_med'] = float(np.median(np.abs(d) / Bseq[1:]))
        row['within_var_med'] = float(np.median(wvar))
    else:
        for c in ['n_trans', 'n_trans_up']:
            row[c] = 0
        for c in ['B_first_over_final', 'B_last_over_final', 'jump_med', 'within_var_med']:
            row[c] = np.nan
    return row


def task(args):
    name, ens, i = args
    m = np.array(MASS_SETS[name], float)
    seed = (i if ens == 'frio' else 1_000_000 + i) + SEED_OFFSET.get(name, 0)
    t0 = time.time()
    o, E, tcr = run_one_ar(m, ens, seed, tcap=TCAP, tol=TOL)
    row = dict(mass_set=name, ensemble=ens, run=i, seed=seed, m0=m[0], m1=m[1], m2=m[2],
               E0=E, t_cr=tcr, status=int(o['status']), esc=int(o['esc']), t_end=o['t_end'],
               t_ej=o['t_ej'], t_ej_tcr=o['t_ej'] / tcr if o['status'] == 1 else np.nan,
               dE=o['dE'], ecc=o['ecc'], a_fin=o['a'], nsteps=int(o['nsteps']), stride=int(o['stride']))
    row['discard'] = int(o['dE'] > 1e-4 or o['status'] in (2, 3))
    row['prompt'] = int(o['status'] == 1 and o['t_ej'] == 0.0)  # sem pericentro: escape direto
    if o['status'] == 1 and not row['discard'] and not row['prompt']:
        row.update(analyse(o, m, tcr))
    row['cpu_s'] = time.time() - t0
    return row


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    out = sys.argv[2] if len(sys.argv) > 2 else 'runs.csv'
    tasks = [(name, ens, i) for name in MASS_SETS for ens in ENSEMBLES for i in range(N)]
    run_one_ar((1, 1, 1), 'frio', 0, tcap=1)  # compila
    rows = []; t0 = time.time()
    with Pool(2) as p:
        for j, r in enumerate(p.imap_unordered(task, tasks, chunksize=4)):
            rows.append(r)
            if (j + 1) % 200 == 0:
                print(j + 1, len(tasks), round(time.time() - t0), flush=True)
    keys = []
    for r in rows:
        for kk in r:
            if kk not in keys:
                keys.append(kk)
    rows.sort(key=lambda r: (r['mass_set'], r['ensemble'], r['run']))
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader()
        for r in rows:
            w.writerow(r)
    print('ok', round(time.time() - t0))
