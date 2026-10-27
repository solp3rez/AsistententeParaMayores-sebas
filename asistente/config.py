"""Configuración central: lo que cambia de una instalación a otra va acá."""
import os

# --- Servidor MQTT ---
BROKER = os.getenv("MQTT_BROKER", "10.56.2.30")
PORT = int(os.getenv("MQTT_PORT", "1883"))

# Si el broker pide usuario y clave, se definen como variables de entorno
# (ver INSTALAR.md, archivo /etc/asistente.env). Nunca los escribas en el código.
USUARIO = os.getenv("MQTT_USER")
CLAVE = os.getenv("MQTT_PASS")

# --- Topics ---
TOPIC_MENSAJE = "prueba"       
TOPIC_PARAR = "prueba/parar"   
TOPIC_SOS = "prueba/sos"                                      

PIN_SOS = 20   
PIN_PARAR = 21  
# El otro extremo de cada botón va a GND (pin físico 9, 14, 20...).
# Se usa la resistencia pull-up interna, no hace falta resistencia externa.

# --- Voz ---
VOZ = "es"
PAUSA_ENTRE_REPETICIONES = 1.0  # segundos
