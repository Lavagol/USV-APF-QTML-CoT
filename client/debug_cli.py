import sys          #para el loop
from PySide6.QtCore import QCoreApplication  #para el loop
from socket_handlercorreo import SocketHandler
from simulador import SimuladorAPF   # tu script con la clase SimuladorAPF

app = QCoreApplication(sys.argv)   #enciende el bucle de eventos

socket_thread = SocketHandler(host="127.0.0.1", port=65432)  #10.3.141.201 #señal
simulador     = SimuladorAPF()             #slot o función conectada

#socket_thread.obstaculosActualizados.connect(simulador.actualizarObstaculos) #comunicacion entre señal y simulador
socket_thread.obstaculosActualizados_real.connect(simulador.actualizarObstaculos)  # comunicación con el simulador
simulador.alertaActualizada.connect(print)  # solo para ver los mensajes

socket_thread.start()   # ¡señal encendido,comienza a escuchar!

sys.exit(app.exec())    # corre hasta que cierres con Ctrl-C
