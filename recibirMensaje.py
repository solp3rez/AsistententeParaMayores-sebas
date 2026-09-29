import paho.mqtt.client as client

BROKER = "10.56.31.11"
PORT = 9090
TOPIC = "mi/topico/prueba"

def recibir_mensaje(client,msg):
    if client.subscribe(TOPIC):
        print(f"Suscripto a {TOPIC}")
        print(f"Mensaje recibido en {msg.topic}: {msg.payload.decode()}")