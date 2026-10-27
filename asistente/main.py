"""Punto de entrada: es lo único que ejecuta el servicio de systemd."""
import signal

import paho.mqtt.client as mqtt

import config
from audio import Locutor
from boton import iniciar_botones

locutor = Locutor(voz=config.VOZ, pausa=config.PAUSA_ENTRE_REPETICIONES)


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code.is_failure:
        print(f"Error de conexión MQTT: {reason_code}")
        return
    print(f"Conectado a {config.BROKER}:{config.PORT}")
    # Suscribirse acá (y no una sola vez) hace que se renueve tras cada reconexión
    client.subscribe([(config.TOPIC_MENSAJE, 0), (config.TOPIC_PARAR, 0)])


def on_disconnect(client, userdata, flags, reason_code, properties=None):
    print(f"Desconectado ({reason_code}). Se reintenta solo.")


def on_message(client, userdata, msg):
    if msg.topic == config.TOPIC_PARAR:
        print("Parar recibido")
        locutor.parar()
    elif msg.topic == config.TOPIC_MENSAJE:
        texto = msg.payload.decode("utf-8", errors="replace").strip()
        if not texto:
            return
        print("Recibido:", texto)
        locutor.agregar(texto)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if config.USUARIO:
        client.username_pw_set(config.USUARIO, config.CLAVE)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    botones = iniciar_botones(client, locutor)  # noqa: F841 (mantener referencias)

    def salir(*_):
        locutor.parar()
        client.disconnect()

    signal.signal(signal.SIGTERM, salir)
    signal.signal(signal.SIGINT, salir)

    # connect_async + retry_first_connection: si la Pi arranca antes de que
    # haya red o de que el servidor esté listo, sigue intentando en vez de caerse.
    client.connect_async(config.BROKER, config.PORT, keepalive=60)
    client.loop_forever(retry_first_connection=True)


if __name__ == "__main__":
    main()