from geopy.distance import geodesic

# Diccionario de 4 puntos, con 2 tuplas: CoT vs JSON
puntos = {
    "obstaculo1": [(-33.030643, -71.624418), (-33.030643,-71.624418)],
    "obstaculo2": [(-33.031128, -71.624267), (-33.031128, -71.624267)],
    "inicio":     [(-33.029107, -71.625760), (-33.029109, -71.625758)],
    "meta":       [(-33.031539, -71.623552), (-33.031531, -71.623555)],
}

for nombre, (cot, json) in puntos.items():
    dist = geodesic(cot, json).meters
    print(f"{nombre}: error = {dist:.2f} m")
