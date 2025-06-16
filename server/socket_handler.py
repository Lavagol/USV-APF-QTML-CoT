import socket
import time
import xml.etree.ElementTree as ET
import re

from PyQt6.QtCore import QThread, pyqtSignal


class SocketHandler(QThread):
    mensajeRecibido = pyqtSignal(str)
    conexionCaida = pyqtSignal()
    coordenadasRecibidas = pyqtSignal(str, str, str, str, str, str, str, str, str)
    conexionExitosa = pyqtSignal()
    solicitarCOT = pyqtSignal()

    # NUEVA SEÑAL PARA EL ESTADO DEL MOTOR
    motorEstadoCambiado = pyqtSignal(bool)  # True = ON , False = OFF

    def __init__(self, host="127.0.0.1", port=65432): #self, host="10.3.141.201", port=65432
        super().__init__()
        self.host = host
        self.port = port
        self.is_running = True
        self.conectado = False
        self.socket = None
        self.cr_enviado = False
        self.ultimo_mensaje = None

        self.connected_since = None  # <--- Nuevo atributo
        self.ultimo_envio = 0  # Timestamp del último envío
        self.intervalo_minimo = 1  # segundos entre comandos (1000ms)

    def estaConectado(self):
        """Devuelve True si el socket está conectado, de lo contrario False."""
        return self.conectado and self.socket is not None

    def procesarMensaje(self, response):
        """Procesar el mensaje recibido desde el servidor"""
        print(f"Respuesta del servidor: {response}")
        self.ultimo_mensaje = response  # 1) guardar

        # 2) Comprobación rápida de “XML válido”
        if (
            not response.startswith("<?xml")
            or "<event" not in response
            or "</event>" not in response
        ):
            print("El mensaje recibido no es un XML válido.")
            self.conexionExitosa.emit()
            return

        self.mensajeRecibido.emit(response)  # 3) señal cruda

        try:
            root = ET.fromstring(response)
            point = root.find("point")
            detail = root.find("detail")

            # ───────── 4) ESTADO DEL MOTOR ─────────
            
            
                        
            estado_motor = "0"                                    # "0", "1", "2"…
            
            
            
            if detail is not None and detail.text:
                m = re.search(r'estado_motor="(\d+)"', detail.text)
                if m:
                        estado_motor = m.group(1)

            encendido = estado_motor in ("1", "2")      # True cuando viene "1" o "2"

            self.motorEstadoCambiado.emit(encendido)    # ✅ sólo una llamada, sólo bool




            # ───────── 5) DATOS numéricos ──────────
            lat = lon = ce = speed = temp = fuel = vbat = rpm = "0"

            if point is not None:  # coords
                lat = point.get("lat", "0")
                lon = point.get("lon", "0")
                ce = point.get("ce", "0")

            if detail is not None and detail.text:  # resto con regex
                detail_text = detail.text
                speed = re.search(r'speed="(\d+)"', detail_text)
                temp = re.search(r'temp="(\d+)"', detail_text)
                fuel = re.search(r'fuel_level="(\d+)"', detail_text)
                vbat = re.search(r'vbat="([\d.]+)"', detail_text)
                rpm = re.search(r'rpm="(\d+)"', detail_text)

                speed = speed.group(1) if speed else "0"
                temp = temp.group(1) if temp else "0"
                fuel = fuel.group(1) if fuel else "0"
                vbat = vbat.group(1) if vbat else "0"
                rpm = rpm.group(1) if rpm else "0"

            # ───────── 6) EMITIR datos completos ───
                if lat is not None and lon is not None:
                    print(
                        f"""📢 Emisión de coordenadasRecibidas ->
        lat:{lat}, lon:{lon}, ce:{ce}, temp:{temp},
        speed:{speed}, fuel:{fuel}, vbat:{vbat},
        estado_motor:{estado_motor}, rpm:{rpm}"""
                    )

                self.coordenadasRecibidas.emit(
                    lat, lon, ce, temp, speed, fuel, vbat, estado_motor, rpm
                )

            # ───────── 7) Conexión exitosa ─────────
            if detail is not None and 'contact_callsign="USV-DIPRIDA"' in detail.text:
                self.conexionExitosa.emit()

        except ET.ParseError as e:
            print(f"Error al parsear el XML: {e}")

    def obtenerUltimoMensaje(self):
        """Devuelve el último mensaje recibido"""
        return self.ultimo_mensaje

    def run(self):
        print("Ejecutando hilo del socket.")

        while self.is_running:
            # Intentamos conectarnos hasta que lo logremos o se detenga el hilo
            if not self.socket:
                try:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.settimeout(5.0)  # Timeout más pequeño, por ejemplo 5s
                    print(f"Conectando a {self.host}:{self.port}...")
                    self.socket.connect((self.host, self.port))
                    self.conectado = True

                    # Guardar la hora de conexión
                    self.connected_since = time.time()  # <--- Hora actual en segundos

                    self.cr_enviado = False
                    print("Conexión establecida con el servidor.")

                    # Podrías emitir aquí una señal de “conexionExitosa”
                    
                    self.solicitarCOT.emit()

                except socket.error as e:
                    print(f"Error al conectar al servidor: {e}")
                    self.conexionCaida.emit()
                    self.conectado = False
                    self.socket.close()
                    self.socket = None
                    # En lugar de break, hacemos un continue para reintentar
                    print("Reintentando conectar en 5s...")
                    time.sleep(5)
                    continue  # Vuelve al inicio del while self.is_running
            print("Terminando hilo del socket: self.is_running = False")

            # Si estamos conectados y no hemos enviado CR, lo enviamos
            if self.conectado and not self.cr_enviado:
                try:
                    print("Enviando mensaje CR...")
                    self.socket.sendall(b"CR")
                    response = self.socket.recv(4096)
                    if not response:
                        raise socket.error("No se recibió respuesta al CR.")
                    print(f"Mensaje XML recibido:\n{response}")

                    self.procesarMensaje(response.decode().strip())

                    print("bucle")

                    self.cr_enviado = True
                    time.sleep(10)

                    
                except (socket.timeout, socket.error) as e:
                    print(f"Error durante el envío de CR: {e}")
                    self.conexionCaida.emit()
                    self._handle_disconnect()
                    # Reintentar tras 5s
                    time.sleep(5)
                    continue

            # Ahora, mientras sigamos conectados, hacemos el polling "GET_COT"
            
            
            
            
                print("Esperando 10 segundos antes de enviar el primer GET_COT...")
                #time.sleep(10)
            if self.conectado:
                try:
                    print("Solicitando lectura de COT...")
                    
                    
                    
                    delay = 0  # segundos entre solicitudes GET_COT
                    time.sleep(3)
                    self.enviar_comando("GET_COT")

                    # 🔹 Validar que el socket está activo antes de llamar a recv()
                    if self.socket is None:
                        print(
                            "❌ Error: El socket es None antes de recibir datos. Intentando reconectar..."
                        )
                        self._handle_disconnect()
                        #time.sleep(10)
                        continue  # Volver a intentar la conexión en el próximo ciclo

                    response = self.socket.recv(4096)

                    if not response:
                        raise socket.error("No se recibió respuesta al GET_COT.")

                    self.procesarMensaje(response.decode().strip())

                except (socket.timeout, socket.error) as e:
                    print(f"Error recibiendo COT o servidor desconectado: {e}")
                    self.conexionCaida.emit()
                    self._handle_disconnect()
                    time.sleep(5)
                    continue  # Volvemos al while para reintentar conectar

            time.sleep(6)  # Espera entre GET_COT

        print("Terminando hilo del socket: self.is_running = False")

    def _handle_disconnect(self):
        """Cierra el socket y marca la conexión como caída."""
        self.conectado = False
        self.connected_since = None

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.cr_enviado = False

    def enviar_comando(self, comando: str):
        if not self.conectado or self.socket is None:
            print("❌ Socket desconectado; comando descartado")
            return

        ahora = time.time()
        if ahora - self.ultimo_envio < self.intervalo_minimo:
            print(f"⏱️  Ignorado (≤{self.intervalo_minimo}s): {comando}")
            return

        try:
            payload = f"{comando}".encode()  # ← separador
            self.socket.sendall(payload)
            self.ultimo_envio = ahora  # ← registra el envío ✅
            print(f"✅ Comando enviado: {comando}")
        except socket.error as e:
            print(f"⚠️  Error al enviar: {e}")
            self._handle_disconnect()
            print(f"Error al enviar el comando: {e}")
            self.conexionCaida.emit()

            self.socket = None
            # self.socket.close()

            self.conectado = False
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            self.socket.close()

    def stop(self):
        """Detener la ejecución del hilo del socket."""
        self.is_running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        self.quit()
        self.wait()
