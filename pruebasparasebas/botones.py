from datetime import datetime
import paho.mqtt.client as mqtt

broker = "10.56.31.11"
puerto = 1883
topic = "prueba"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(broker, puerto, 60)
client.loop_start()

print("Botón SOS listo. Presioná Enter para enviar (Ctrl+C para salir)")

try:
    while True:
        input()
        hora = datetime.now().strftime("%H:%M:%S")
        client.publish(topic, f"SOS emergencia {hora}").wait_for_publish()
        print("SOS enviado a las", hora)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
    print("\nSaliendo")