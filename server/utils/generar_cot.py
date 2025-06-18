from datetime import datetime, timezone

nombre_emisor = "Proveedor de obstaculos"

def generar_mensaje_cot(nombre_emisor):
    uuid = "DIPRIDA-01"

    cot_xml = f"""<?xml version="1.0" standalone="yes"?>
<event version="2.0">
  <detail contact_callsign="{nombre_emisor}"
          obstaculo1="-33.030356, -71.618463"
          tipo_obstaculo1="Rocas"
          obstaculo2="-33.028871, -71.616492"
          tipo_obstaculo2="Vessel"
          obstaculo3="-33.028766, -71.616307"
          tipo_obstaculo3="Boya"
          meta="-33.031654, -71.620245" />
  <point lat="-33.026181" lon="-71.612689" ce="0.0" hae="13" le="0.0" />
</event>"""
    return cot_xml

#<event version="2.0">
#  <detail contact_callsign="{nombre_emisor}"
#          obstaculo1="-33.030267, -71.618550"
#          obstaculo2="-33.028871, -71.616492"
#          obstaculo3="-33.028766, -71.616307"
#          meta="-33.031654, -71.620245" />
#  <point lat="-33.026181" lon="-71.612689" ce="0.0" hae="13" le="0.0" />
#</event>"""
          #obstaculo1="-33.02916, -71.61683"
          #obstaculo2="-33.02722, -71.61555"
          #obstaculo3="-33.02916, -71.61683"
          #aaa


          #  obstaculo2="-33.0322, -71.615702"
          #meta="-33.0329, -71.609254"
          #obstaculo1="-33.0329, -71.609254"
          #obstaculo2="-33.0322, -71.615702"
          #obstaculo3="-33.0317, -71.613015"
          #obstaculo2="-33.03220, -71.61824"
          #obstaculo3="-33.03170, -71.619033"

