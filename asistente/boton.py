"""Botones físicos conectados a los pines GPIO de la Raspberry."""
from datetime import datetime

import config


def iniciar_botones(client, locutor):
    """Configura el botón SOS y el botón de parar.

    Devuelve la lista de botones: hay que guardarla en una variable para que
    no se destruyan. Si no hay GPIO (por ejemplo probando en una PC), el resto
    del programa sigue funcionando sin botones.
    """
    try:
        from gpiozero import Button
    except ImportError:
        print("gpiozero no está instalado: botones físicos desactivados")
        return []

    try:
        sos = Button(config.PIN_SOS, bounce_time=0.05)
        parar = Button(config.PIN_PARAR, bounce_time=0.05)
    except Exception as e:
        print(f"No se pudieron iniciar los botones: {e}")
        return []

    def al_apretar_sos():
        hora = datetime.now().strftime("%H:%M:%S")
        # qos=1: si justo se cayó la conexión, se envía apenas vuelva
        client.publish(config.TOPIC_SOS, f"SOS emergencia {hora}", qos=1)
        print("SOS enviado a las", hora)

    def al_apretar_parar():
        locutor.parar()  # corta el audio al instante, aunque no haya red
        client.publish(config.TOPIC_PARAR, "parar", qos=1)  # y avisa al servidor
        print("Parar apretado")

    sos.when_pressed = al_apretar_sos
    parar.when_pressed = al_apretar_parar
    print(f"Botones listos (SOS: GPIO{config.PIN_SOS}, parar: GPIO{config.PIN_PARAR})")
    return [sos, parar]
