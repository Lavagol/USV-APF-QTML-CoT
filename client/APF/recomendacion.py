import numpy as np
from ..models.parametros_obstaculos import PARAMS  # radio / repulsión por tipo

# ───────────────────────────────────────────────────────────
#  PARÁMETROS GLOBALES (solo valores por defecto)
# ───────────────────────────────────────────────────────────
Escala_sim = 1
k_att      = 2.0
k_rep_base = 500
d0_base    = 30

v_max_def  = 2.57                 # no la mocupo, porque cambiare el escape lateral
k_tan      = 300.0
d_pre      = 15.0
angle_pre  = 8.0
cos_pre    = np.cos(np.deg2rad(angle_pre))

radio_alerta        = 150
radio_recomendacion = 100
# ───────────────────────────────────────────────────────────


def calcular_recomendacion(
        
    pos_usv,
    pos_objetivo,
    obstaculos,
    *,
    v_max=v_max_def,      # ← el simulador puede pasar otro valor
    historial=None
):
    """
    Planificador local con 5 etiquetas posibles:
        avance_libre / avance_alerta / avance_APF /
        avance_preventivo / escape_lateral
    """
    # ——— parámetros que dependen de la escala ———
    k_rep_global = k_rep_base
    d0_global    = d0_base * Escala_sim

    # ——— umbrales que dependen de la V_max recibida ———
    umbral_escape_local = 0.10 * v_max   #ojo debo borrar ersto
 
    robot = np.array(pos_usv,      dtype=float)
    goal  = np.array(pos_objetivo, dtype=float)

    # ======================================================
    # 1) Escaneo de obstáculos → decidir si activamos planner
    # ======================================================
    alerta, recomendar = None, False

    # vamos a trackear la distancia mínima global
    distancia_min = float("inf")
    obst_min_id   = None
    pos_min_iter  = None
    
    for idx,(x_obs, y_obs, _) in enumerate(obstaculos):
        d = np.linalg.norm(robot - (x_obs, y_obs))
        # si esta es la mínima hasta ahora:
        if d < distancia_min:
            distancia_min  = d
            obst_min_id    = idx
            pos_min_iter   = tuple(robot)
  

        if radio_recomendacion <= d < radio_alerta:
            vec_obs  = np.array([x_obs, y_obs]) - robot
            vec_goal = goal - robot
            ang = (np.degrees(np.arctan2(vec_obs[1],  vec_obs[0])) -
                   np.degrees(np.arctan2(vec_goal[1], vec_goal[0]))) % 360
            if   45 <= ang < 135:  sector = "izquierda"
            elif 135 <= ang < 225: sector = "trasera"
            elif 225 <= ang < 315: sector = "derecha"
            else:                  sector = "frontal"
            alerta = f"⚠️ Obstáculo a {d:.1f} m, sector {sector}"

        if d < radio_recomendacion:
            recomendar = True

    # ======================================================
    # 2) MODO LIBRE / ALERTA (no se usa APF)
    # ======================================================
    if not recomendar:
        dir_unit = (goal - robot) / np.linalg.norm(goal - robot)
        rumbo    = (np.degrees(np.arctan2(dir_unit[1], dir_unit[0])))% 360
        #rumbo    = (np.degrees(np.arctan2(dir_unit[1], dir_unit[0])) + 1.45) % 360 # transformacion del el vector unitario direction (la dirección hacia donde se moverá el USV) en un ángulo en grados
        maniobra = "AVANCE ALERTA" if alerta else "AVANCE LIBRE"
        return {
            "rumbo"           : round(rumbo, 1),
            "velocidad"       : round(v_max, 2),
            "distancia_minima": round(distancia_min, 2),
            "maniobra"        : maniobra,
            "alerta"          : alerta,
            "force_total"     : np.array([0.0, 0.0]),
            "norm_F"          : 0.0
        }

    # ======================================================
    # 3) PLANIFICADOR LOCAL  (radio ≤ 100 m)
    # ======================================================
    # 3‑a) Atractiva
    F_att = k_att * (goal - robot)

    # 3‑b) Repulsiva por tipo
    F_rep = np.zeros(2)
    for x_obs, y_obs, tipo in obstaculos:
        vec = robot - np.array((x_obs, y_obs))
        d   = np.linalg.norm(vec)

        d0_i   = PARAMS.get(tipo, {}).get('radio',     d0_global)
        krep_i = PARAMS.get(tipo, {}).get('repulsion', k_rep_global)

        if 1e-6 < d <= d0_i:
            F_rep += krep_i * ((1/d) - (1/d0_i)) / d**2 * (vec / d)

    # 3‑c) Tangente preventiva
    F_tan = np.zeros(2)
    if np.linalg.norm(F_att) > 1e-6:
        hdir = F_att / np.linalg.norm(F_att)
        for x_obs, y_obs, _ in obstaculos:
            vec = robot - np.array((x_obs, y_obs))
            d   = np.linalg.norm(vec)
            if 1e-3 < d < d_pre:
                u_r    = vec / d
                cos_th = np.dot(hdir, -u_r)
                if cos_th > cos_pre:
                    gamma = (cos_th - cos_pre) / (1 - cos_pre)
                    beta  = (d_pre - d) / d_pre
                    k_eff = k_tan * beta * gamma
                    u_t   = np.array([-u_r[1], u_r[0]])
                    if np.dot(u_t, goal - robot) < 0:
                        u_t = -u_t
                    F_tan = k_eff * u_t
                    break

    # 3‑d) Gradiente total
    F_tot  = F_att + F_rep + F_tan
    norm_F = np.linalg.norm(F_tot)

   

    # 3‑e) Maniobra
    if norm_F < umbral_escape_local:             # ── MODO 4
        tangent   = np.array([-F_tot[1], F_tot[0]])
        direction = tangent / np.linalg.norm(tangent)
        maniobra  = "ESCAPE LATERAL"

    elif np.any(F_tan):                          # ── MODO 3
        direction = F_tot / norm_F
        maniobra  = "AVANCE PREVENTIVO"

    else:                                        # ── MODO 2
        direction = F_tot / norm_F
        maniobra  = "AVANCE APF"

    # ─────────────────────────────────────────────────────────────
    # 3‑f) BLOQUE DE INERCIA  (opcional: alpha = 0 ⇢ sin inercia)
    # -----------------------------------------------------------------
    alpha = 0.30                      # <‑‑ ajusta o pásalo como parámetro

    prev = getattr(calcular_recomendacion, "_dir_prev", None)
    if prev is not None and alpha > 0 and np.linalg.norm(prev) > 1e-6:
        direction = (1 - alpha) * direction + alpha * prev
        direction /= np.linalg.norm(direction)

    # Guarda para la siguiente llamada
    calcular_recomendacion._dir_prev = direction
    # ─────────────────────────────────────────────────────────────

    rumbo = np.degrees(np.arctan2(direction[1], direction[0])) % 360
    distancia_min_m = distancia_min * Escala_sim
    return {
        "rumbo"           : round(rumbo, 1),
        "velocidad"       : round(v_max, 2),  # Por defecto, se devuelve la misma velocidad que recibió.
        "maniobra"        : maniobra,
        "alerta"          : alerta,
        "force_total"     : F_tot,
        "norm_F"          : norm_F,
        "distancia_minima": round(distancia_min_m, 2),
        "pos_min_iter"    : pos_min_iter,
        "obst_min_id"     : obst_min_id,
}  
