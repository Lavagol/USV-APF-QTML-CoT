import numpy as np
import matplotlib.pyplot as plt

# Factor de escala
Escala = 0.2

# ————— CARGO TRAYECTORIA —————
tray = np.load("trayectoria.npy", allow_pickle=True)
xs = tray[:,0] * Escala
ys = tray[:,1] * Escala

# ————— CARGO OBSTÁCULOS (x, y, tipo) —————
obs = np.load("obstaculos.npy", allow_pickle=True)
if obs.ndim == 2 and obs.shape[1] == 3:
    ox = obs[:,0].astype(float) * Escala
    oy = obs[:,1].astype(float) * Escala
    ot = obs[:,2]  # tipos como array de strings
else:
    # sin tipos, los tratamos como "desconocido"
    ox = obs[:,0].astype(float) * Escala
    oy = -obs[:,1].astype(float) * Escala
    ot = np.array(['desconocido'] * len(ox))

# ————— ESTILOS POR TIPO —————
estilos = {
    'piedra'    : dict(marker='o', s=150, facecolor='lightgray', edgecolor='black'),
    'barco'     : dict(marker='s', s=150, facecolor='skyblue',   edgecolor='black'),
    'boya'      : dict(marker='^', s=150, facecolor='orange',    edgecolor='black'),
    'desconocido': dict(marker='o', s=150, facecolor='none',      edgecolor='black'),
    #costa o accidente geográfico
}

# ————— PLOTEO —————
fig, ax = plt.subplots(figsize=(8,8))
ax.plot(xs, ys, 'b.-', lw=1, ms=4, label="Trayectoria")
ax.scatter(xs[0], ys[0], c='red',   s=120, label="Inicio", zorder=4)
ax.scatter(xs[-1],ys[-1],c='green', s=120, label="Meta",   zorder=4)

# Fondo de influencia
for x0, y0 in zip(ox, oy):
    c = plt.Circle((x0,y0), 10*Escala, color='gray', alpha=0.2, zorder=1)
    ax.add_patch(c)

# Obstáculos con su estilo
vistos = set()
for x0, y0, tipo in zip(ox, oy, ot):
    cfg = estilos.get(tipo, estilos['desconocido'])
    label = tipo.capitalize() if tipo not in vistos else None
    ax.scatter(
        x0, y0,
        marker    = cfg['marker'],
        s         = cfg['s'],
        facecolors= cfg['facecolor'],
        edgecolors= cfg['edgecolor'],
        label     = label,
        zorder    = 3
    )
    vistos.add(tipo)

ax.set_title("Trayectoria USV (Y invertido: norte arriba)")
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.legend(loc='best', fontsize=10)
ax.set_aspect('equal', 'box')
ax.set_xlim(xs.min()-20, xs.max()+20)
ax.set_ylim(ys.min()-20, ys.max()+20)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()
