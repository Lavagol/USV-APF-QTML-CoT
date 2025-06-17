from pyproj import Geod

geod = Geod(ellps="WGS84")

lon1, lat1 = -71.612689, -33.026181
lon2, lat2 = -71.620245, -33.031654

azimut_inicial, azimut_final, distancia_m = geod.inv(lon1, lat1, lon2, lat2)
rumbo_360 = (azimut_inicial + 360) % 360

# Conversión de distancia a millas náuticas
distancia_nm = distancia_m / 1852

# Velocidad en nudos
velocidad_nudos = 5.0

# Tiempo en horas y minutos
tiempo_horas = distancia_nm / velocidad_nudos
tiempo_minutos = tiempo_horas * 60

print(f"Rumbo inicial (CRS): {rumbo_360:.1f}°")
print(f"Distancia: {distancia_m:.1f} m ({distancia_nm:.3f} MN)")
print(f"Tiempo estimado a {velocidad_nudos} nudos: {tiempo_minutos:.2f} minutos")
