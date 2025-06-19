import numpy as np
# Al inicio de recomendacion.py
from ..models.parametros_obstaculos import PARAMS



def calcular_recomendacion(
    pos_usv,
    pos_objetivo,
    obstaculos,
    *,
    # ───────────── Parámetros de fuerzas ─────────────
    k_att = 2.0,          # ganancia atractiva
    k_rep = 500,         # ganancia repulsiva
    d0    = 15,         # radio de influencia repulsiva
    v_max = 2.5,          # velocidad máx. permitida    # ───────────── Parámetros ISS / escape ───────────
    EPS_REL = 0.15,       # fracción de v_max para gatillar ISS
    NU_ESC  = 2.0,        # radio en torno a la meta donde NO se impulsa
    K_IMP   = 1.0,        # magnitud del impulso: K_IMP · v_max
    umbral_escape_lateral = None,  # ← se fija internamente al 10 % de v_max
    # ───────────── Otros ajustes ─────────────────────
    historial           = None,    # lista de últimas posiciones
    radio_alerta        = 80,      # solo avisa
    radio_recomendacion = 60       # activa planificador local
):
    # -------------------------------------------------
    # 0) Ajuste dinámico de parámetros dependientes
    # -------------------------------------------------
    if umbral_escape_lateral is None:
        umbral_escape_lateral = 0.10 * v_max   # ← 10 % de v_max

    robot = np.array(pos_usv,  dtype=float)    # posición del USV
    goal  = np.array(pos_objetivo, dtype=float) # posición objetivo

    # -------------------------------------------------
    # 1) Escaneo de obstáculos y radios
    # -------------------------------------------------
    alerta, recomendar   = None, False
    distancia_minima     = float("inf")
    # desempaquetamos (x, y, tipo). Si no vas a usar el tipo aquí,
    # puedes capturarlo en “_” para indicar “lo ignoro”.
    for x_obs, y_obs, _ in obstaculos:
        #obs_arr = np.array(obs, dtype=float)
        obs_arr = np.array((x_obs, y_obs), dtype=float)
        dist    = np.linalg.norm(robot - obs_arr)
        distancia_minima = min(distancia_minima, dist)

        # Dentro del radio de alerta → solo avisar
        if radio_recomendacion <= dist < radio_alerta:
            vec_obs  = obs_arr - robot
            vec_goal = goal    - robot
            ang = ( np.degrees(np.arctan2(vec_obs[1],  vec_obs[0])) -
                    np.degrees(np.arctan2(vec_goal[1], vec_goal[0])) ) % 360
            if   45 <= ang < 135:  sector = "izquierda"
            elif 135 <= ang < 225: sector = "trasera"
            elif 225 <= ang < 315: sector = "derecha"
            else:                  sector = "frontal"
            alerta = f"⚠️ Obstáculo a {dist:.1f} m, sector {sector}"

        # Dentro del radio de recomendación → activar APF
        if dist < radio_recomendacion:
            recomendar = True

    # -------------------------------------------------
    # 2) MODO LIBRE / AVISO  (no se usa APF)
    # -------------------------------------------------
    if not recomendar:
        direction = (goal - robot) / np.linalg.norm(goal - robot)
        #rumbo     = np.degrees(np.arctan2(direction[1], direction[0])) % 360
        rumbo_plano = np.degrees(np.arctan2(direction[1], direction[0])) % 360
        rumbo = (rumbo_plano + 1.45) % 360
        maniobra  = "avance_alerta" if alerta else "avance_libre"
        return {
            "rumbo"           : round(rumbo, 1),
            "velocidad"       : round(v_max, 2),
            "distancia_minima": round(distancia_minima, 2),
            "maniobra"        : maniobra,          # etiqueta modo
            "impulso_ISS"     : False,             # no hay impulso
            "alerta"          : alerta,
            "force_total"     : np.array([0.0, 0.0]),
            "norm_F"          : 0.0
        }

    # -------------------------------------------------
    # 3) PLANIFICADOR LOCAL (APF)
    # -------------------------------------------------
    # 3-a) Calcular fuerzas
    force_att = k_att * (goal - robot)            # fuerza atractiva 𝐅_atractiva = k_att · (objetivo − posición)
    force_rep = np.zeros(2)                        # inicializamos vector repulsivo
    #for obs in obstaculos:
    #    vec  = robot - np.array(obs, dtype=float)
    #    dist = np.linalg.norm(vec)
    #    if dist <= d0:                            # dentro de radio repulsivo
    #        dist = max(dist, 1e-3)                # evita división /0
    #        rep  = k_rep * ((1/dist) - (1/d0)) / (dist**2)
    #        force_rep += rep * (vec / dist)       # dirección + magnitud
    for x_obs, y_obs, tipo in obstaculos:
        # 1) vector USV → obstáculo
        vec  = robot - np.array((x_obs, y_obs), dtype=float)
        dist = np.linalg.norm(vec)          # distancia actual

        # 2) sacamos de PARAMS la influencia según el tipo:
        #    • rho0: radio a partir del cual REPULSION=0
        #    • eta : ganancia repulsiva
        params = PARAMS.get(tipo, {})
        d0_i   = params.get('radio', d0)     # si no está, usamos el d0 global
        krep_i = params.get('repulsion',  k_rep)  # idem para k_rep

        # 3) si estamos dentro de ese radio de influencia...
        if dist <= d0_i:
            dist = max(dist, 1e-3)           # evitamos división por cero
            # fórmula clásica de APF repulsiva:
            #   rep = η · (1/dist − 1/d0) / dist²
            rep  = krep_i * ((1/dist) - (1/d0_i)) / (dist**2)
            # 4) sumamos componente repulsiva normalizada
            force_rep += rep * (vec / dist)

    force_total = force_att + force_rep           # ∇U completo
    norm_F      = np.linalg.norm(force_total)
    d_goal      = np.linalg.norm(goal - robot)

    # 3-b) Detectar mínimo local (gradiente pequeño o poco avance)
    activar_escape = (
        (norm_F < EPS_REL * v_max and d_goal > NU_ESC) or
        (historial is not None and len(historial) == 5 and
         max( np.hypot(h[0] - historial[0][0],
                       h[1] - historial[0][1]) for h in historial[1:] ) < 1.0)
    )

    # 3-c) Seleccionar maniobra
    if activar_escape:
        # Impulso ISS (perpendicular a ∇U)
        ortho = np.array([-force_total[1], force_total[0]])
        if np.linalg.norm(ortho) < 1e-6:          # caso degenerado
            ortho = np.array([1.0, 0.0])
        direction = ortho / np.linalg.norm(ortho)
        velocidad = K_IMP * v_max
        maniobra  = "impulso_ISS"

    elif norm_F < umbral_escape_lateral:
        # Escape lateral clásico (tangente)
        tangent   = np.array([-force_total[1], force_total[0]])
        direction = tangent / np.linalg.norm(tangent)
        velocidad = v_max
        maniobra  = "escape_lateral"

    else:
        # Avance normal por gradiente
        direction = force_total / norm_F
        velocidad = min(v_max, norm_F)            # limita a v_max
        maniobra  = "avance_APF"

    rumbo = np.degrees(np.arctan2(direction[1], direction[0])) % 360

    # -------------------------------------------------
    # 4) Devuelve diccionario con la recomendación
    # -------------------------------------------------
    return {
        "rumbo"           : round(rumbo, 1),
        "velocidad"       : round(velocidad, 2),
        "distancia_minima": round(distancia_minima, 2),
        "maniobra"        : maniobra,
        "impulso_ISS"     : activar_escape,
        "alerta"          : alerta,
        "force_total"     : force_total,
        "norm_F"          : norm_F
    }
