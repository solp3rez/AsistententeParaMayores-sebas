"""Reproduce un texto en voz alta, repitiéndolo hasta que se pida parar."""
import subprocess
import threading


class Locutor:
    def __init__(self, voz="es", pausa=1.0):
        self.voz = voz
        self.pausa = pausa
        self._parar = threading.Event()
        self._lock = threading.Lock()
        self._hilo = None
        self._proceso = None

    def hablando(self):
        return self._hilo is not None and self._hilo.is_alive()

    def iniciar(self, texto):
        """Empieza a repetir el texto. Devuelve False si ya estaba sonando."""
        with self._lock:
            if self.hablando():
                return False
            self._parar.clear()
            self._hilo = threading.Thread(
                target=self._repetir, args=(texto,), daemon=True
            )
            self._hilo.start()
            return True

    def parar(self):
        """Frena la reproducción (si no hay nada sonando, no hace nada)."""
        self._parar.set()
        with self._lock:
            proceso = self._proceso
            hilo = self._hilo
        if proceso is not None and proceso.poll() is None:
            proceso.terminate()
        # Esperar un momento a que el hilo termine, así un mensaje nuevo
        # que llegue justo después de "parar" no se ignora por error.
        if hilo is not None and hilo is not threading.current_thread():
            hilo.join(timeout=2)

    def _repetir(self, texto):
        while not self._parar.is_set():
            try:
                proceso = subprocess.Popen(["espeak-ng", "-v", self.voz, texto])
            except FileNotFoundError:
                print("espeak-ng no está instalado: sudo apt install espeak-ng")
                return
            with self._lock:
                self._proceso = proceso
            if self._parar.is_set():  # llegó "parar" justo mientras arrancaba
                proceso.terminate()
            proceso.wait()
            self._parar.wait(self.pausa)
