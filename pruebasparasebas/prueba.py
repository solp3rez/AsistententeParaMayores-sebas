from datetime import datetime
import paho.mqtt.publish as publish

topic = "prueba"
mensaje = "llego el mensajeee"
broker = "10.56.31.11"
puerto = 1883
horaActual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

print("ejecutando")
publish.single(topic, f"{mensaje} - {horaActual}", hostname=broker, port=puerto)
print("Mensaje enviado:", f"{mensaje} - {horaActual}")