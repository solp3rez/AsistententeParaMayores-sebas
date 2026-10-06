import subprocess
import paho.mqtt.client as mqtt

broker = "10.56.31.11"
puerto = 1883
topic = "prueba"

def on_connect(client, userdata, flags, reason_code, properties):
    print("Conectado:", reason_code)
    client.subscribe(topic)
    print("suscripto a el topic")

def on_message(client, userdata, msg):
    texto = msg.payload.decode("utf-8")
    print("Recibido:", texto)
    subprocess.run(["espeak-ng", "-v", "es", texto])

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, puerto, 60)
client.loop_forever()