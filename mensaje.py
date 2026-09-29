import paho.mqtt.client as client
from datetime import datetime

BROKER = "10.56.31.11"
PORT = 9090
TOPIC = "mi/topico/prueba"
MENSAJE = "hola"

def on_connect(reason_code):
    if reason_code.is_failure:
        print(f"Error de conexion MQTT: {reason_code}")
        return
    else:
        print("Conectado al broker MQTT")


def enviar_mensaje(client):
    client.publish(TOPIC, MENSAJE, hostname=BROKER, port=PORT, auth={"username": "albornozito2", "password": "albornozitos"})
    print(f"Enviado '{MENSAJE}' a {TOPIC}")



 
 
