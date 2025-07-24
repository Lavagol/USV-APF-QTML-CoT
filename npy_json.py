import numpy as np
import json
import folium
from pyproj import Transformer

# 1. ORIGEN UTM FIJO (de tu simulación real)
x0 = 255970.99504084507
y0 = 6342776.915033079
transformer = Transformer.from_crs("EPSG:32719", "EPSG:4326", always_xy=True)

# 2. Cargar trayectoria interna
trayectoria = np.load("trayectoria.npy")  # (N, 2)

# 3. Convertir trayectoria a GPS
trayectoria_gps = []
for x, y in trayectoria:
    x_utm = x0 + x
    y_utm = y0 + y
    lon, lat = transformer.transform(x_utm, y_utm)
    trayectoria_gps.append({"lat": lat, "lon": lon})

# Guardar como JSON
with open("trayectoria_gps.json", "w", encoding="utf-8") as f:
    json.dump(trayectoria_gps, f, indent=2, ensure_ascii=False)

print("✔ trayectoria_gps.json generado correctamente.")

# 4. Cargar obstáculos (ya vienen en GPS)
with open("obstaculos_gps.json", "r", encoding="utf-8") as f:
    obstaculos = json.load(f)

# 5. Crear mapa con folium
if trayectoria_gps:
    centro_lat = trayectoria_gps[0]["lat"]
    centro_lon = trayectoria_gps[0]["lon"]
else:
    centro_lat = obstaculos[0]["lat"]
    centro_lon = obstaculos[0]["lon"]

m = folium.Map(location=[centro_lat, centro_lon], zoom_start=15)

# Trayectoria azul
tray_coords = [(p["lat"], p["lon"]) for p in trayectoria_gps]
folium.PolyLine(tray_coords, color="blue", weight=3, opacity=0.8, tooltip="Trayectoria USV").add_to(m)

# Obstáculos
for obs in obstaculos:
    folium.Marker(
        location=(obs["lat"], obs["lon"]),
        icon=folium.Icon(color="red", icon="exclamation-sign"),
        tooltip=f"Obstáculo ({obs['tipo']})"
    ).add_to(m)

# Guardar mapa final
m.save("mapa_simulacion.html")
print("✔ Mapa generado: mapa_simulacion.html")
