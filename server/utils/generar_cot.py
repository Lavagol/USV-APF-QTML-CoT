from datetime import datetime, timezone #Importa datetime y timezone, pero no se utilizan en el resto de la función. Normalmente se usan para los campos time, start, stale del CoT.

nombre_emisor = "Proveedor de obstaculos" #Variable global con el callsign que aparecerá en el atributo contact_callsign

def generar_mensaje_cot(nombre_emisor): #Función que recibe el nombre del emisor y devuelve el XML.
    uuid = "DIPRIDA-01"

    cot_xml = f"""<?xml version="1.0" standalone="yes"?>   
<event version="2.0">
  <detail contact_callsign="{nombre_emisor}"
          obstaculo1="-33.030643, -71.624418"
          tipo_obstaculo1="Boya"
                    obstaculo2="-33.031128, -71.624267"
          tipo_obstaculo2="Roca"
                    obstaculo11="-33.030698, -71.623891"
          tipo_obstaculo11="Roca"
          
          meta="-33.031539, -71.623552" />
  <point lat="-33.029107" lon="-71.625760" ce="0.0" hae="13" le="0.0" />
</event>"""
    return cot_xml #Entrega la cadena XML.



"""
    cot_xml = f<?xml version="1.0" standalone="yes"?>   
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
          tipo_obstaculo7="Roca"
          obstaculo8="-33.027916, -71.615040"
          tipo_obstaculo8="Roca"
          obstaculo9="-33.028204, -71.615427"
          tipo_obstaculo9="Roca"
          obstaculo10="-33.028458, -71.615115"
          tipo_obstaculo10="Roca"
          obstaculo11="-33.030698, -71.623891"
          tipo_obstaculo11="Roca"

          meta="-33.031654, -71.620245" />
  <point lat="-33.026181" lon="-71.612689" ce="0.0" hae="13" le="0.0" />
</event>
"""