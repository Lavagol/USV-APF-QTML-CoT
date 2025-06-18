PARAMS = {
    'piedra':  { 'repulsion': 5.0,  'radio': 10.0 },
    'barco':   { 'repulsion': 8.0,  'radio': 30.0 },
    'boya':    { 'repulsion': 3.0,  'radio': 5.0  },
    'default': { 'repulsion': 4.0,  'radio': 15.0 },
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
