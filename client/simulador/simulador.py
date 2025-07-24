"""
- Este simulador escucha señales Qt( como la posiciónUSV_real, metaActualizada_real,obstaculosActualizados) que llegan de la función del SocketHandler del script socket_handlercorreo.py.
- Convierte esas señales en posiciones relativas internas (Origen (0,0), del el punto de inicio), que se usan en un plano XY para simular el avance del vehículo.
- Cada 500 ms (por el QTimer), se ejecuta el método avanzar(), que hace lo siguiente:
    - CCalcula la dirección recomendada con el método calcular_recomendacion().
    - Mueve la posición actual del USV en esa dirección.
    - Guarda historial, trayectoria y exporta los datos de simulación.
    - Actualiza la interfaz gráfica (.qml)  con un mensaje textual.
"""
from PySide6.QtCore import QObject, QTimer, Signal, QPointF, QDateTime  #obj, clase base para objeto Qt. timer, temporizador que llama avanzar cada cierto tiempo. Signal para emitir señales QY hacia el QML, Qpoint representa coordenadas en 2 D con puntoflotantes (representa numneors) y el Qdatepermite calcular el timepo transcurrido.
import numpy as np #para cálculos y exportaciones.npy
from client.APF.recomendacion import calcular_recomendacion 
import csv  # exportación del log
import json #exportaciones
from pyproj import Transformer # para convertir coordenadas UTM ↔ lat/lon.

class SimuladorAPF(QObject):    #QObject parapoder emitir señales y ser conectado al Qt/QML
    alertaActualizada    = Signal(str) #
    actualizarObstaculos = Signal(list) #de la matriz de objetos de obstaculo.py
    posicionInterna      = Signal(float, float)  # decimales
    metaInterna          = Signal(float, float)
    tiempoActualizado    = Signal(float) #para mostrar el timer del simulador
    def __init__(self, parent=None):  #llama al QObject
        super().__init__(parent)
        self.v_knots       = 10.0     #Velocidad de avancedel USV en nudos
        self.v_max         = self.v_knots * 0.514444  # nudos a m/s
        #self._origin_raw   = None    # (x0, y0_invertido)
        self._origin_raw   = None   # Origen UTM real del sistema (primer punto recibido)
        self._start_time   = None
        self._dist_inicial = None

        self.robot_pos     = QPointF(0.0, 0.0) #Posición del USV  en  sistema interno relativo.
        self.goal_pos      = None               #Posición de la meta en el sistema interno relativo.
        self.obstaculos    = []     #Lista de obstáculos en coordenadas internas.
        self.hist_pos      = []     #Historial de posiciones pasadas (para suavizar trayectorias, etc).
        self._origin_fijado= False #Flags para evitar fijar origen/meta más de una vez.
        self._meta_fijada  = False #OJO que este flag me puede jugar en contra cuando quiera actulizar meta.

        self.trayectoria   = [] #guarda los puntos hechos y para después exportarlos
        self.log           = [] #lo mismo, pero no lo estoy ocupando

        self.timer = QTimer(self) #Cada 500 ms se ejecutará avanzar(), temporizador
        self.timer.timeout.connect(self.avanzar) #Cuando se recibe una nueva lista de obstáculos, se ejecuta _on_obstaculos_actualizados. temporizador
        self.actualizarObstaculos.connect(self._on_obstaculos_actualizados)
        self.min_pos   = []           #  guarda la posición más cercana al obstáculo por iteración


    # ----- Punto de inicio (origen en el sistema interno) -----

    def fijar_origin(self, x0, y0): #Se fija el origen UTM, y se considera como (0,0) en el sistema interno.
        #Almacenar origen UTM tal cual como recibe
        self._origin_raw = (x0, y0)  
        if not self._origin_fijado:
            self.robot_pos       = QPointF(0.0, 0.0) #Se asume que el robot comienza en ese punto.
            self._origin_fijado  = True
            #print(f"🌐 Origin (invertido)={self._origin_raw} → interna (0,0)")
            print(f"🌐 Origin={self._origin_raw} → interna (0,0)")
            self._maybe_start()  #Revisa si ya se tiene meta para iniciar la simulación, sin meta no se inicia la simualción.


    # ----- Meta (convertida a coordenadas internas) -----
    def fijar_meta(self, x_meta, y_meta): 
        if self._meta_fijada:
            return
        self._meta_fijada = True

        ox, oy = self._origin_raw
        xi     = (x_meta - ox) * 1.0   # la escala ya la aplica geo_to_xy en el handler y transforma la meta a coordenadas relativas internas
        yi = (y_meta - oy) * 1.0 #Se transforma la meta a coordenadas relativas internas.

        #Calcula la distancia inicial y tiempo.
        self.goal_pos = QPointF(xi, yi)
        self._start_time   = QDateTime.currentDateTime()
        self._dist_inicial = np.hypot(xi, yi)

        print(f"🏁 Meta interna → X={xi:.1f}, Y={yi:.1f}")
        self.metaInterna.emit(xi, yi)
        self._maybe_start()


    # ----- Obstáculos actualizados (señal externa) -----
    def _on_obstaculos_actualizados(self, lista_xy_tipo): #Recibe lista de obstáculos con (x, y, tipo) en sistema interno
        """
        lista_xy_tipo viene de SocketHandler.obstaculosActualizados.emit(obs_xy_tipo)
        como una lista de tuplas (x_internal, y_internal, tipo_str)
        """
        # Guardamos tanto la posición como el tipo en self.obstaculos
        # de modo que luego podamos pasar ambos al APF o colorearlos en la GUI
        self.obstaculos = [(QPointF(x, y), tipo)
            for x, y, tipo 
                in lista_xy_tipo
        ]

        # Para depurar, imprimimos cada obstáculo en la TERMINAL:
        for pt, tipo in self.obstaculos:
            print(f"🛑 Obstáculo de tipo '{tipo}' en interna → "
                f"({pt.x():.1f},{pt.y():.1f})")
            

    # ----- Inicia la simulación si origen y meta están listos -----
    def _maybe_start(self):
        if self._origin_fijado and self.goal_pos and not self.timer.isActive():
            print(f"▶️ Iniciando APF @ {self.v_knots} kn")
            self.timer.start(500) #ojo cadaXXX milisegundo

    # ----- Movimiento del USV (cada 500 ms) -----
    def avanzar(self): 
        dt = self.timer.interval() / 1000.0  #Delta de tiempo en segundos (0.5 s). dt = 500 / 1000 = 0.5 s
        dx   = self.goal_pos.x()  - self.robot_pos.x()
        dy   = self.goal_pos.y()  - self.robot_pos.y()
        dist = np.hypot(dx, dy)  #Calcula distancia actual a la meta

        # emito X, Y con Y+→norte
        self.posicionInterna.emit(self.robot_pos.x(), self.robot_pos.y())

        if dist < 1.0:  #Si llegó a la meta, emite alerta, calcula tiempo real y esperado.
            elapsed_ms  = self._start_time.msecsTo(QDateTime.currentDateTime()) #timer que inicia desde que incia la simulación hasta llegar a la meta
            elapsed_min = elapsed_ms/1000/60  #cálculo del tiempo ejecutado
            teoric_min  = self._dist_inicial/1852.0/self.v_knots*60   #cálculo del tiempo teórico
            self.alertaActualizada.emit(
                f"✅ Llegó en {elapsed_min:.1f} min (teórico {teoric_min:.1f})"
            )
            self._guardar_logs()
            return
        # Recomendación APF, aquí se llama a la función caLCULAR RECOMENDACIÓN DE Recomendacion.py
        reco = calcular_recomendacion(
            (self.robot_pos.x(), self.robot_pos.y()),
            (self.goal_pos.x(),   self.goal_pos.y()),
            #[(pt.x(), pt.y()) for pt, tipo in self.obstaculos],
            [(pt.x(), pt.y(), tipo) for pt, tipo in self.obstaculos], #(x, y, tipo) para obstáculo
            historial=self.hist_pos,
            v_max=self.v_max #el simulador le indica al algoritmo: “haz la planificación asumiendo que puedo moverme hasta esta velocidad
        )
        if reco.get("pos_min_iter") is not None:
            self.min_pos.append((
                reco["obst_min_id"],                 # índice de obstáculo
                *reco["pos_min_iter"],               # x_min , y_min  (interno)
                reco["distancia_minima"]             # distancia
        ))
        # : Se agrega corrección de declinación magnética de 1.4
        rumbo_apf  = reco["rumbo"]
        #  QML con 0°=N y giro horario: %ojop rumbo apf me llega antihorRIO, por eso hacemos esto
        #grados_gui = (90 - rumbo_apf) % 360  #Normalmente, el rumbo tiene origen en el eje X positivo (Este) y va en sentido antihorario (como es estándar en matemáticas).
        grados_gui = (90 - rumbo_apf + 1.4) % 360 #aplicamos %360 para mantener entre 0-360

        # movimiento del USV en el simulador
        ang    = np.radians(rumbo_apf)    #Las funciones trigonométricas en Python (cos, sin) trabajan en radianes, no en grados., por lo tanto paso a radianes el angulo
        vx     = np.cos(ang) * reco["velocidad"] #Estos dos cálculos convierten el ángulo en un vector de movimiento en X e Y.
        vy     = np.sin(ang) * reco["velocidad"] #se genera cuantos m/s muevo el vehículo respecto rumbo apf

        self.robot_pos.setX(self.robot_pos.x() + vx * dt)  #aquí es el movimiento aplicado al vehículo o robot
        self.robot_pos.setY(self.robot_pos.y() + vy * dt)
        self.trayectoria.append((self.robot_pos.x(), self.robot_pos.y()))

        # log
        self.hist_pos.append((self.robot_pos.x(), self.robot_pos.y()))
        if len(self.hist_pos) > 5:
            self.hist_pos.pop(0)


        # 1) ----- calcula tiempo transcurrido desde que partió -----------
        secs = 0.0
        if self._start_time is not None:
            secs = self._start_time.msecsTo(QDateTime.currentDateTime()) / 1000.0
            self.tiempoActualizado.emit(secs)

        # --- formato mm:ss.s
        mm    = int(secs // 60)
        ss    = secs % 60

        msg  = (reco["alerta"] + "\n") if reco["alerta"] else ""
        msg += (f"📍 ({self.robot_pos.x():.1f},{self.robot_pos.y():.1f})\n"
                f"🧭 Rumbo: {grados_gui:.1f}°\n"
                f"🚀 Vel.: {reco['velocidad']} m/s\n"
                f"🛑 Maniobra: {reco['maniobra']}\n"
                f"⏱️ Tiempo: {mm:02d}:{ss:04.1f} s")

        self.alertaActualizada.emit(msg)


    # ----- Guarda datos de simulación (trayectoria, obstáculos, mínimos) -----
    def _guardar_logs(self):
        # 1) Guardar la trayectoria
        np.save("trayectoria.npy", np.array(self.trayectoria))
        if self._origin_raw is not None:
            transformer = Transformer.from_crs("EPSG:32719", "EPSG:4326", always_xy=True)

            tray_json = []
            for x, y in self.trayectoria:
                x_utm = x + self._origin_raw[0]
                y_utm = y + self._origin_raw[1]
                lon, lat = transformer.transform(x_utm, y_utm)
                tray_json.append({"lat": lat, "lon": lon})

            with open("trayectoria_gps.json", "w", encoding="utf-8") as f:
                json.dump(tray_json, f, indent=2, ensure_ascii=False)

            print("[✔] Exportado → trayectoria_gps.json")
        else:
            print("[⚠] No se pudo exportar trayectoria GPS: origen UTM no fijado.")
        #obst_coords = []
        #for entry in self.obstaculos:
            # si entry viene como (QPointF, tipo)
        #    if isinstance(entry, tuple):
        #        pt, _ = entry
        #    else:
        #        pt = entry
        #    obst_coords.append([pt.x(), pt.y()])
        # 2) Extraer coordenadas y tipo de cada obstáculo
        obst_data = []
        for pt, tipo in self.obstaculos:
            obst_data.append([pt.x(), pt.y(), tipo])
        # 3) Guardar array de shape (N,2)
        np.save("obstaculos.npy", 
        np.array(obst_data, dtype=object))
        # --- guarda posiciones mínimas para post‑análisis ----------------------
        if self.min_pos:                                  
            #solo con el primer mínimo por obstáculo
            best={}
            for idx, xm, ym, d in self.min_pos:
                # si aún no tenemos este obstáculo o encontramos una distancia menor:
                if idx not in best or d < best[idx][2]:
                    best[idx] = (xm, ym, d)

            min_pos_arr  = np.array([[x, y] for _, (x, y, _) in sorted(best.items())],
                            dtype=float)
            min_dist_arr = np.array([d for _, (_, _, d) in sorted(best.items())],
                            dtype=float)
            np.save("min_pos.npy",  min_pos_arr)         # (N,2) internas
            np.save("min_dist.npy", min_dist_arr)        # (N,)  metros
            print("[✔] Exportado → min_pos.npy  /  min_dist.npy")
        # --- NUEVO: Exportar obstáculos a coordenadas GPS ---
        if self._origin_raw is not None:
            transformer = Transformer.from_crs("EPSG:32719", "EPSG:4326", always_xy=True)

            obst_json = []
            for pt, tipo in self.obstaculos:
                x_utm = pt.x() + self._origin_raw[0]
                y_utm = pt.y() + self._origin_raw[1]
                lon, lat = transformer.transform(x_utm, y_utm)
                obst_json.append({
                    "lat": lat,
                    "lon": lon,
                    "tipo": tipo
                })

            with open("obstaculos_gps.json", "w", encoding="utf-8") as f:
                json.dump(obst_json, f, indent=2, ensure_ascii=False)

            print("[✔] Exportado → obstaculos_gps.json")
        else:
            print("[⚠] No se pudo exportar obstáculos: origen UTM no fijado.")


        # 4) Guardar el log CSV si existe
        if self.log:
            with open("log_usv.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=self.log[0].keys())
                w.writeheader()
                w.writerows(self.log)
