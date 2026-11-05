import subprocess
import threading
import time
import hashlib
import os
from gtts import gTTS


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
        while True:
            if self.mensaje_actual is None and self.cola:
                self.mensaje_actual = self.cola.pop(0)

            texto = self.mensaje_actual
            if texto is None:
                time.sleep(0.2)       
            else:
                self._decir(texto)    # decirlo una vez
                time.sleep(self.pausa)  # y repetirlo, hasta que lo paren

    def _decir(self, texto):
        """Reproduce el mensaje con mpg123 y espera a que termine de hablar."""
        archivo = self._preparar_audio(texto)
        if archivo is None:
            self.mensaje_actual = None
            return

        try:
            self.proceso = subprocess.Popen(["mpg123", "-q", archivo])
        except FileNotFoundError:
            print("Falta instalar mpg123: sudo apt install mpg123")
            self.mensaje_actual = None
            return

        # Si justo mientras arrancaba llegó "parar", cortarlo de inmediato
        if self.mensaje_actual is not texto:
            self._cortar_voz()

        self.proceso.wait()

    def _preparar_audio(self, texto):
        """Convierte el texto en un mp3 (una sola vez por mensaje) y devuelve su ruta."""
        archivo = f"/tmp/{hashlib.md5(texto.encode()).hexdigest()}.mp3"
        if not os.path.exists(archivo):
            try:
                gTTS(texto, lang="es", tld="com.ar").save(archivo)
            except Exception as e:
                print(f"No se pudo generar la voz (¿hay internet?): {e}")
                return None
        return archivo