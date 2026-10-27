"""Locutor: lee mensajes en voz alta y guarda los que van llegando en una casilla."""
import subprocess
import threading
import time


class Locutor:
    def __init__(self, voz="es", pausa=1):
        self.voz = voz                # idioma de la voz
        self.pausa = pausa            # segundos de silencio entre repeticiones
        self.cola = []                # la casilla: mensajes esperando su turno
        self.mensaje_actual = None    # el que está sonando (None = silencio)
        self.proceso = None           # el programa espeak-ng que está hablando

        # Un hilo que trabaja siempre en segundo plano, leyendo los mensajes
        threading.Thread(target=self._trabajar, daemon=True).start()

    def agregar(self, texto):
        """Llega un mensaje nuevo. Si ya suena otro, queda guardado en la casilla."""
        if self.mensaje_actual is not None:
            print("Guardado en la casilla")
        self.cola.append(texto)

    def parar(self):
        """Corta el mensaje que suena. El siguiente de la casilla empieza solo."""
        self.mensaje_actual = None
        if self.proceso is not None and self.proceso.poll() is None:
            self.proceso.terminate()

    def _trabajar(self):
        """Se repite para siempre: toma un mensaje de la casilla y lo dice."""
        while True:
            # Si no suena nada y hay mensajes guardados, tomar el primero
            if self.mensaje_actual is None and self.cola:
                self.mensaje_actual = self.cola.pop(0)

            texto = self.mensaje_actual
            if texto is None:
                time.sleep(0.2)       # no hay nada que decir, esperar un momento
            else:
                self._decir(texto)    # decirlo una vez
                time.sleep(self.pausa)  # y repetirlo, hasta que lo paren

    def _decir(self, texto):
        try:
            self.proceso = subprocess.Popen(["espeak-ng", "-v", self.voz, texto])
        except FileNotFoundError:
            print("Falta instalar espeak-ng: sudo apt install espeak-ng")
            self.mensaje_actual = None
            return

        # Si justo mientras arrancaba llegó "parar", cortarlo de inmediato
        if self.mensaje_actual is not texto:
            self.proceso.terminate()

        self.proceso.wait()  # esperar a que termine de hablar