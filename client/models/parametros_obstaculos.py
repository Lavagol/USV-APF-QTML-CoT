Escala=10
PARAMS = {
    'piedra':  { 'repulsion': 500*Escala**3,  'radio': 20.0 *Escala },# 100 m
    'barco':   { 'repulsion': 800*Escala**3,  'radio': 50.0*Escala },# 300 m
    'boya':    { 'repulsion': 250*Escala**3,  'radio': 15.0  *Escala},# 50 m
    'default': { 'repulsion': 150*Escala**3,  'radio': 15.0 *Escala},
    #'piedra':  { 'repulsion': 500*Escala**3,  'radio': 10.0 *Escala },# 100 m
    #'barco':   { 'repulsion': 800*Escala**3,  'radio': 30.0*Escala },# 300 m
    #'boya':    { 'repulsion': 250*Escala**3,  'radio': 5.0  *Escala},# 50 m
    #'default': { 'repulsion': 400*Escala**3,  'radio': 15.0 *Escala},
}

def clasificar_obstaculo(raw_tag: str) -> str:
    """
    Dada la etiqueta recibida en el CoT (por ejemplo 'Rocas', 'Vessel', 'Buoy'),
    normaliza y devuelve uno de los tipos en PARAMS.
    """
    tag = raw_tag.strip().lower()
    if 'roc' in tag or 'rock' in tag:
        return 'piedra'
    if 'buoy' in tag or 'boya' in tag:
        return 'boya'
    if 'vessel' in tag or 'ship' in tag or 'boat' in tag:
        return 'barco'
    return 'default'
