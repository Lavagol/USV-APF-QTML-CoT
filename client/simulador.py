from PySide6.QtCore import QObject, QTimer, Signal, QPointF, QDateTime
import numpy as np
from recomendacion import calcular_recomendacion
import csv  # exportación del log

class SimuladorAPF(QObject):
    alertaActualizada    = Signal(str)
    actualizarObstaculos = Signal(list)
    posicionInterna      = Signal(float, float)  # X, Y con Y+→norte
    metaInterna          = Signal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.v_knots       = 5.0
        self.v_max         = self.v_knots * 0.514444  # m/s
        #self._origin_raw   = None    # (x0, y0_invertido)
        self._origin_raw =None   # (x0, y0) en UTM
        self._start_time   = None
        self._dist_inicial = None

        self.robot_pos     = QPointF(0.0, 0.0)
        self.goal_pos      = None
        self.obstaculos    = []
        self.hist_pos      = []
        self._origin_fijado= False
        self._meta_fijada  = False

        self.trayectoria   = []
        self.log           = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.avanzar)
        self.actualizarObstaculos.connect(self._on_obstaculos_actualizados)

    def fijar_origin(self, x0, y0):
        # Invertimos y para que nuestro sistema interno tenga Y+→norte
        #self._origin_raw = (x0, -y0)
        #Almacenar origen UTM tal cual como recibe
        self._origin_raw=(x0, y0)
        if not self._origin_fijado:
            self.robot_pos       = QPointF(0.0, 0.0)
            self._origin_fijado  = True
            #print(f"🌐 Origin (invertido)={self._origin_raw} → interna (0,0)")
            print(f"🌐 Origin={self._origin_raw} → interna (0,0)")
            self._maybe_start()

    def fijar_meta(self, x_meta, y_meta):
        if self._meta_fijada:
            return
        self._meta_fijada = True

        ox, oy = self._origin_raw
        xi     = (x_meta - ox) * 1.0   # la escala ya la aplica geo_to_xy en el handler
        #yi     = (-y_meta) - oy
        yi = (y_meta - oy) * 1.0
        self.goal_pos = QPointF(xi, yi)

        self._start_time   = QDateTime.currentDateTime()
        self._dist_inicial = np.hypot(xi, yi)

        print(f"🏁 Meta interna → X={xi:.1f}, Y={yi:.1f}")
        self.metaInterna.emit(xi, yi)
        self._maybe_start()

    def _on_obstaculos_actualizados(self, lista_xy):
        #ox, oy = self._origin_raw
        #self.obstaculos = [
        #    #QPointF(x - ox, -y - oy)
        #    QPointF(x,-y)
        #    for x, y in lista_xy
        #]
        #print("🛑 Obstáculos internos →", 
        #    ", ".join(f"({o.x():.1f},{o.y():.1f})" for o in self.obstaculos))         
        #print("🛑 Obstáculos internos →",
        #Lal lista ya viene relativa al origen y sin invertir
        #self.obstaculos = [QPointF(x,y)for x, y in lista_xy]
                # almacenar la lista de obstáculos (coordenadas internas)
        self.obstaculos = [QPointF(x, y) for x, y in lista_xy]
        print("🛑 Obstáculos internos →",
            ", ".join(f"({o.x():.1f},{o.y():.1f})" for o in self.obstaculos))
    def _maybe_start(self):
        if self._origin_fijado and self.goal_pos and not self.timer.isActive():
            print(f"▶️ Iniciando APF @ {self.v_knots} kn")
            self.timer.start(500)

    def avanzar(self):
        dt = self.timer.interval() / 1000.0

        dx   = self.goal_pos.x()  - self.robot_pos.x()
        dy   = self.goal_pos.y()  - self.robot_pos.y()
        dist = np.hypot(dx, dy)

        # emito X, Y con Y+→norte
        self.posicionInterna.emit(self.robot_pos.x(), self.robot_pos.y())

        if dist < 1.0:
            elapsed_ms  = self._start_time.msecsTo(QDateTime.currentDateTime())
            elapsed_min = elapsed_ms/1000/60
            teoric_min  = self._dist_inicial/1852.0/self.v_knots*60
            self.alertaActualizada.emit(
                f"✅ Llegó en {elapsed_min:.1f} min (teórico {teoric_min:.1f})"
            )
            self._guardar_logs()
            return
        # ✉️ Recomendación desde algoritmo APF
        reco = calcular_recomendacion(
            (self.robot_pos.x(), self.robot_pos.y()),
            (self.goal_pos.x(),   self.goal_pos.y()),
            [(o.x(), o.y()) for o in self.obstaculos],
            historial=self.hist_pos,
            v_max=self.v_max
        )

        # ✉️ EDITADO: Se agrega corrección de declinación magnética de 1.4
        rumbo_apf  = reco["rumbo"]
        # si tu QML quiere 0°=N y giro horario:
        grados_gui = (90 - rumbo_apf) % 360
        grados_gui = (90 - rumbo_apf + 1.45) % 360

        # movimiento
        ang    = np.radians(rumbo_apf)
        vx     = np.cos(ang) * reco["velocidad"]
        vy     = np.sin(ang) * reco["velocidad"]

        self.robot_pos.setX(self.robot_pos.x() + vx * dt)
        self.robot_pos.setY(self.robot_pos.y() + vy * dt)
        self.trayectoria.append((self.robot_pos.x(), self.robot_pos.y()))

        # log
        self.hist_pos.append((self.robot_pos.x(), self.robot_pos.y()))
        if len(self.hist_pos) > 5:
            self.hist_pos.pop(0)

        msg  = (reco["alerta"] + "\n") if reco["alerta"] else ""
        msg += (f"📍 ({self.robot_pos.x():.1f},{self.robot_pos.y():.1f})\n"
                f"🧭 Rumbo: {grados_gui:.1f}°\n"
                f"🚀 Vel.: {reco['velocidad']} m/s\n"
                f"🛑 Maniobra: {reco['maniobra']}")

        self.alertaActualizada.emit(msg)

    def _guardar_logs(self):
        np.save("trayectoria.npy", np.array(self.trayectoria))
        np.save("obstaculos.npy", np.array([[o.x(),o.y()] for o in self.obstaculos]))
        if self.log:
            with open("log_usv.csv","w",newline="") as f:
                w = csv.DictWriter(f, fieldnames=self.log[0].keys())
                w.writeheader()
                w.writerows(self.log)
