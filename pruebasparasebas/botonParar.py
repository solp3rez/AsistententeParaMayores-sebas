import paho.mqtt.publish as publish

input("Presioná Enter para parar el mensaje...")
publish.single("prueba/parar", "parar", hostname="10.56.31.11", port=1883)
print("Parar enviado")