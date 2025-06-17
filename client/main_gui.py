from pathlib import Path
from PySide6.QtCore    import QObject, Signal, Property, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtQml     import QQmlApplicationEngine
from simulador             import SimuladorAPF
from socket_handlercorreo  import SocketHandler
import sys

# ───────── Modelo que expone el texto al QML ─────────
class ModeloEstado(QObject):
    estadoTextoChanged = Signal()

    def __init__(self):
        super().__init__()
        self._estado = "Sin alertas"

    def getEstado(self):
        return self._estado

    def setEstado(self, valor):
        if self._estado != valor:
            self._estado = valor
            self.estadoTextoChanged.emit()

    estadoTexto = Property(str, getEstado, setEstado, notify=estadoTextoChanged)


# ───────────────────── MAIN ──────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    modelo = ModeloEstado()
    engine.rootContext().setContextProperty("estadoUSV", modelo)

    # 🔧 Ruta correcta al QML (…/client/ui/interface.qml)
    qml_path = Path(__file__).parent / "ui" / "interface.qml"
    engine.load(QUrl.fromLocalFile(qml_path.as_posix()))
    if not engine.rootObjects():
        sys.exit("❌ No se pudo cargar interface.qml")

    # ─── lógica de red y planificador ───
    socket_thread = SocketHandler(host="127.0.0.1", port=65432)
    simulador     = SimuladorAPF()

    # conectar posición y meta reales (UTM) al simulador
    socket_thread.posicionUSV_real.connect(simulador.fijar_origen)
    socket_thread.metaActualizada_real.connect(simulador.fijar_meta)

    # debug: mostrar internamente en consola con Y invertida
    simulador.posicionInterna.connect(
        lambda x, y: print(f"[GUI] Pos interna → X={x:.1f}, Y={y:.1f}")
    )
    simulador.metaInterna.connect(
        lambda xm, ym: print(f"[GUI] Meta interna → X={xm:.1f}, Y={ym:.1f}")
    )

    # escalado para visualización en la GUI (no afecta al simulador),
    # también invierte Y para mostrar “norte arriba”
    socket_thread.posicionUSV.connect(
        lambda x, y: print(f"[VALID GUI] USV escalado → X={x:.2f}, Y={-y:.2f}")
    )
    socket_thread.metaActualizada.connect(
        lambda xm, ym: print(f"[VALID GUI] Meta escalada → X={xm:.2f}, Y={-ym:.2f}")
    )

    # obstáculos proyectados (escalados) a la vista, y enviados al simulador
    #socket_thread.obstaculosActualizados.connect(simulador.actualizarObstaculos)
    #socket_thread.obstaculosActualizados.connect(
     # Obstáculos reales (UTM) para el simulador
    socket_thread.obstaculosActualizados_real.connect(simulador.actualizarObstaculos)
    socket_thread.obstaculosActualizados_real.connect(
        lambda obs: print(
            #"[VALID GUI] Obstáculos escalados → " +
            "[VALID GUI] Obstáculos reales → " +
            "; ".join(f"({x:.2f},{y:.2f})" for x, y in obs)
        )
    )

    # conectamos alertas del simulador al modelo de estado (QML)
    simulador.alertaActualizada.connect(modelo.setEstado)

    socket_thread.start()
    app.aboutToQuit.connect(socket_thread.stop)

    sys.exit(app.exec())
