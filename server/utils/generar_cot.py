from datetime import datetime, timezone

nombre_emisor = "Proveedor de obstaculos"

def generar_mensaje_cot(nombre_emisor):
    uuid = "DIPRIDA-01"

    cot_xml = f"""<?xml version="1.0" standalone="yes"?>
<event version="2.0">
  <detail contact_callsign="{nombre_emisor}"
          obstaculo1="-33.027319, -71.614251"
          tipo_obstaculo1="Vessel"
          obstaculo2="-33.027561, -71.614829"
          tipo_obstaculo2="Roca"
          obstaculo3="-33.027113, -71.614009"
          tipo_obstaculo3="Boya"
          obstaculo4="-33.027667, -71.614518"
          tipo_obstaculo4="Vessel"
          obstaculo5="-33.027495, -71.614354"
          tipo_obstaculo5="Roca"
          obstaculo6="-33.027886, -71.614760"
          tipo_obstaculo6="Roca"
          obstaculo7="-33.027946, -71.614694"
          tipo_obstaculo57="Roca"
          obstaculo8="-33.027916, -71.615040"
          tipo_obstaculo8="Roca"
          obstaculo9="-33.028204, -71.615427"
          tipo_obstaculo9="Roca"
          obstaculo10="-33.028458, -71.615115"
          tipo_obstaculo10="Roca"
          obstaculo11="-33.028407, -71.615192"
          tipo_obstaculo11="Roca"
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

