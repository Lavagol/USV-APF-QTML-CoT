import numpy as np
import matplotlib.pyplot as plt

Escala = 0.2
trayectoria = np.load("trayectoria.npy", allow_pickle=True)
try:
    obstaculos = np.load("obstaculos.npy")
except FileNotFoundError:
    obstaculos = np.empty((0,2))

# normaliza obstaculos a shape (M,2)
if obstaculos.ndim == 1 and obstaculos.size == 2:
    obstaculos = obstaculos.reshape(1,2)

# prepara xs, ys    
xs = trayectoria[:, 0] * Escala
# invertimos Y **una sola vez** para que Y+ sea norte arriba
ys = -trayectoria[:, 1] * Escala

fig, ax = plt.subplots(figsize=(6,6))
ax.plot(xs, ys, 'b.-', label="Trayectoria")
ax.scatter(xs[0], ys[0], c='red',   label="Inicio")
ax.scatter(xs[-1],ys[-1],c='green', label="Meta")

# Obstáculos
ox = obstaculos[:,0]*Escala
oy = -obstaculos[:,1]*Escala
if len(ox):
    ax.scatter(ox, oy, c='k', s=80, label="Obstáculo")
    for x0,y0 in zip(ox,oy):
        circle = plt.Circle((x0,y0), 10*Escala,
                            color='gray', alpha=0.3)
        ax.add_patch(circle)

ax.set_aspect('equal')
ax.set_xlim(xs.min()-10, xs.max()+10)
ax.set_ylim(ys.min()-10, ys.max()+10)
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.legend()
ax.set_title("Trayectoria USV (Y invertido: norte arriba)")
plt.show()
