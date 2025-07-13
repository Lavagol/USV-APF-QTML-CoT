import numpy as np
import matplotlib.pyplot as plt

# ——————————————————— PARAMETROS ———————————————————
Escala = 10.0                               # 1 unidad interna = 0.1 m

# ——————————————————— TRAYECTORIA ———————————————————
tray = np.load("trayectoria.npy", allow_pickle=True)
xs, ys = tray[:, 0] * Escala, tray[:, 1] * Escala       # mismo signo interno

# ——————————————————— OBSTÁCULOS ———————————————————
obs = np.load("obstaculos.npy", allow_pickle=True)

# ① Si el archivo es 1-D (array de objetos), lo expandimos a (N,3)
if obs.ndim == 1:
    # Cada entrada debería ser (x, y, tipo).  Filtramos nulos por si acaso
    obs = np.array([o for o in obs if o is not None], dtype=object)
    if obs.size:                            # evita vstack([]) si está vacío
        obs = np.vstack(obs)

# ② Si aún así no tenemos forma (N,3) → lo tratamos como vacío
if obs.ndim != 2 or obs.shape[1] < 2:
    ox = oy = ot = np.empty(0)
else:
    ox = obs[:, 0].astype(float) * Escala
    oy = obs[:, 1].astype(float) * Escala
    # Si existe tercera columna la usamos como tipo
    ot = obs[:, 2] if obs.shape[1] >= 3 else np.array(['desconocido'] * len(ox))

# ——————————————————— ESTILOS ———————————————————
estilos = {
    'piedra'    : dict(marker='o', s=150, facecolor='lightgray', edgecolor='black'),
    'barco'     : dict(marker='s', s=150, facecolor='skyblue',   edgecolor='black'),
    'boya'      : dict(marker='^', s=150, facecolor='orange',    edgecolor='black'),
    'desconocido': dict(marker='o', s=150, facecolor='none',     edgecolor='black'),
}

# ——————————————————— PLOT ———————————————————
fig, ax = plt.subplots(figsize=(8, 8))

# Trayectoria
ax.plot(xs, ys, 'b.-', lw=1, ms=4, label="Trayectoria")
ax.scatter(xs[0],  ys[0],  c='red',   s=120, label="Inicio", zorder=4)
ax.scatter(xs[-1], ys[-1], c='green', s=120, label="Meta",   zorder=4)

# Fondo de influencia (círculos grises)
for x0, y0 in zip(ox, oy):
    ax.add_patch(plt.Circle((x0, y0), 10 * Escala, color='gray', alpha=0.20, zorder=1))

# Obstáculos con su estilo
vistos = set()
for x0, y0, tipo in zip(ox, oy, ot):
    cfg   = estilos.get(tipo, estilos['desconocido'])
    label = tipo.capitalize() if tipo not in vistos else None
    ax.scatter(x0, y0,
               marker     = cfg['marker'],
               s          = cfg['s'],
               facecolors = cfg['facecolor'],
               edgecolors = cfg['edgecolor'],
               label      = label,
               zorder     = 3)
    vistos.add(tipo)

# Ajustes de gráfico
ax.set_title("Trayectoria USV (orientación interna)")
ax.set_xlabel("X (m)");  ax.set_ylabel("Y (m)")
ax.set_aspect('equal', 'box')
ax.set_xlim(xs.min() - 20, xs.max() + 20)
ax.set_ylim(ys.min() - 20, ys.max() + 20)
ax.grid(alpha=0.3)
ax.legend(loc='best', fontsize=9)
plt.tight_layout()
plt.show()
