import sys, numpy as np, pandas as pd
from scipy import ndimage
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
files = sys.argv[1:]
fig, axs = plt.subplots(1, len(files), figsize=(4.2 * len(files), 4.4))
axs = np.atleast_1d(axs)
for ax, f in zip(axs, files):
    d = pd.read_csv(f); N = d.i.max() + 1
    G = np.full((N, N), -1)
    cls = np.where(d.ok == 0, -1, np.where(d.nSf >= 2, 0, np.where(d.status != 1, 3, np.where(d.esc == 2, 1, 2))))
    G[d.i, d.j] = cls
    ch = (G == 0)
    A = ch.mean(); At = (d.nS >= 2).mean()
    fr = {k: (G == v).mean() for k, v in (('caos', 0), ('passagem', 1), ('troca', 2), ('excursao', 3))}
    eps, fs = [], []
    for k in (1, 2, 4, 8, 16):
        dif = np.concatenate([(ch != np.roll(ch, k, 0)).ravel(), (ch != np.roll(ch, k, 1)).ravel()]).mean()
        eps.append(k / N); fs.append(dif)
    alpha = np.polyfit(np.log(eps[:4]), np.log(fs[:4]), 1)[0]
    reg = ~ch
    lab, n = ndimage.label(reg); sizes = ndimage.sum(reg, lab, range(1, n + 1))
    big = sizes[sizes >= 0.002 * N * N]
    print(f'{f}: A(1a exc)={A:.3f} A(total)={At:.3f} | ' + ' '.join(f'{k}={v:.3f}' for k, v in fr.items()) +
          f' | vizinhos diferentes {fs[0]:.3f}..{fs[-1]:.3f}, expoente de incerteza {alpha:.2f} | ilhas regulares: {n} ({len(big)} grandes, com {big.sum()/max(reg.sum(),1):.0%} da area regular)')
    ax.imshow(G.T, origin='lower', extent=[0, 360, 0, 360], cmap=ListedColormap(['#d9d9d9', '#111318', '#1D3FD8', '#E8480C', '#7a7a7a']), vmin=-1, vmax=3, interpolation='nearest')
    ax.set_title(f.replace('ph_', '').replace('.csv', ''), fontsize=9); ax.set_xlabel('fase do binario (graus)'); ax.set_ylabel('orientacao (graus)')
plt.tight_layout(); plt.savefig('phase_maps.png', dpi=110)
