# client/proceso/posproceso.py
from pathlib import Path
import numpy as np, json, re
import glob, json, numpy as np, pathlib as pl
# 1) mapa “caso lógico” → “prefijo real”  (sin la parte .npy / .json)
MAPPING = {
    "barco": "barco",                 # ← coincide con obstaculos_baroc.npy
    "roca" : "roca",                  # ← usamos regex para el (1) del gps
    "boya" : "boya"
}

BASE = Path(__file__).parent          # carpeta donde está este script


def _cargar(fname_npy: str, fname_json: str, allow_regex=False):
    """
    Devuelve un np.array leyendo .npy o, si no existe, el .json.
    Si allow_regex=True se permite comodín (p.e. *_gps*.json).
    """
    f_npy  = BASE / fname_npy
    if f_npy.exists():
        return np.load(f_npy, allow_pickle=True)

    if allow_regex:                             # busca cualquier variante
        candidatos = list(BASE.glob(fname_json))
        if candidatos:
            with open(candidatos[0]) as fh:
                return np.array(json.load(fh))
    else:
        f_json = BASE / fname_json
        if f_json.exists():
            with open(f_json) as fh:
                return np.array(json.load(fh))

    raise FileNotFoundError(f"No se halló {fname_npy} ni {fname_json}")


def cargar_ruta(caso: str):
    pref = MAPPING[caso]

    tray = _cargar(f"trayectoria_{pref}.npy",
                   f"trayectoria_{pref}_gps*.json", allow_regex=True)

    obs  = _cargar(f"obstaculos_{pref}.npy",
                   f"obstaculos_{pref}_gps*.json", allow_regex=True)
    return tray, obs


def resumen(tray, obs, nombre):
    d_long = np.sum(np.linalg.norm(np.diff(tray, axis=0), axis=1))
    d_min  = min(np.linalg.norm(tray - o, axis=1).min() for o in obs)

    print(f"── {nombre.upper():5} ──")
    print(f" Ruta total          : {d_long:8.1f} m")
    print(f" Distancia mínima obs: {d_min:8.1f} m\n")


def main():
    for caso in ("barco", "roca", "boya"):
        tray, obs = cargar_ruta(caso)
        resumen(tray, obs, caso)


if __name__ == "__main__":
    main()
