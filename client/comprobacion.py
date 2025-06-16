import numpy as np
from pyproj import Transformer

# Coordenadas de ejemplo (lat, lon)
start = (-33.026181, -71.62689)
goal  = (-33.031654, -71.620245)

# Transformador WGS84 → UTM 19S
tr = Transformer.from_crs("EPSG:4326", "EPSG:32719", always_xy=True)

# Convertir lat/lon a UTM (x, y)
x0, y0 = tr.transform(start[1], start[0])
xm, ym = tr.transform(goal[1],  goal[0])

# 1) Distancia en metros
distance_m = np.hypot(xm - x0, ym - y0)

# 2) Convertir a millas náuticas
distance_nm = distance_m / 1852

# 3) Velocidad y tiempo
speed_kn = 5.0  # nudos
time_h = distance_nm / speed_kn
time_min = time_h * 60

print(f"Distancia: {distance_m:.1f} m ({distance_nm:.3f} NM)")
print(f"Tiempo estimado a {speed_kn} kn: {time_min:.1f} minutos")