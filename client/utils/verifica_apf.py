import numpy as np

Escala = 10                # igual que en tu simulador
radio_real        = 100    # m
margen_seguridad  = 20     # m

# 1) trayectoria: PX → m
tray_px = np.load('trayectoria.npy')        # (N,2)   en px
tray_m  = tray_px * Escala                  #  ← MULTIPLICAR

# 2) longitud
longitud_m = np.linalg.norm(np.diff(tray_m, axis=0), axis=1).sum()
print(f"Longitud simulada: {longitud_m:.1f} m")

# 3) obstáculo
obs_raw = np.load('obstaculos.npy', allow_pickle=True)
obs_raw = np.atleast_2d(obs_raw)
if obs_raw.size == 0:
    print("⚠️  Sin obstáculos")
else:
    obs_m = obs_raw[0, :2].astype(float) * Escala     #  ← MULTIPLICAR
    dist  = np.linalg.norm(tray_m - obs_m, axis=1).min()
    objetivo = radio_real + margen_seguridad
    print(f"Distancia mínima al obstáculo: {dist:.1f} m "
          f"(objetivo ≥ {objetivo} m) → {'✅' if dist>=objetivo else '❌'}")
