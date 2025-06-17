from pyproj import Geod, Transformer
import numpy as np

# Geodesia para distancia y rumbo
geod = Geod(ellps="WGS84")

# Coordenadas geográficas
lon1, lat1 = -71.621932, -33.030181  # Punto A
lon2, lat2 = -71.575721, -32.929493  # Punto B

# Rumbo y distancia reales
azimut_inicial, azimut_final, distancia_m = geod.inv(lon1, lat1, lon2, lat2)
rumbo_360 = (azimut_inicial + 360) % 360

# Transformador WGS84 → UTM (19S para Chile central)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32719", always_xy=True)

x1, y1 = transformer.transform(lon1, lat1)
x2, y2 = transformer.transform(lon2, lat2)

# Cálculo en el plano cartesiano
dx = x2 - x1
dy = y2 - y1
distancia_xy = np.hypot(dx, dy)
rumbo_rad = np.arctan2(dx, dy)
rumbo_plano = (np.degrees(rumbo_rad) + 360) % 360

# Conversión a millas náuticas
distancia_nm = distancia_m / 1852
tiempo_horas = distancia_nm / 5.0
tiempo_minutos = tiempo_horas * 60

# Mostrar resultados
print(f"--- Datos geodésicos (WGS84) ---")
print(f"Rumbo inicial (CRS): {rumbo_360:.1f}°")
print(f"Distancia geodésica: {distancia_m:.1f} m ({distancia_nm:.3f} MN)")
print(f"Tiempo estimado a 5 nudos: {tiempo_minutos:.2f} minutos")

print(f"\n--- Datos en plano XY (UTM) ---")
print(f"Delta X: {dx:.2f} m, Delta Y: {dy:.2f} m")
print(f"Distancia XY: {distancia_xy:.1f} m")
print(f"Rumbo plano: {rumbo_plano:.1f}°")
