import os

BROKER = os.getenv("MQTT_BROKER", "10.56.31.45")
PORT = int(os.getenv("MQTT_PORT", "1883"))

USUARIO = os.getenv("MQTT_USER")
CLAVE = os.getenv("MQTT_PASS")

TOPIC_MENSAJE = "prueba"       
TOPIC_PARAR = "prueba/parar"   
TOPIC_SOS = "prueba/sos"                                      

PIN_SOS = 20   
PIN_PARAR = 21  

VOZ = "es"
PAUSA_ENTRE_REPETICIONES = 4.0 
