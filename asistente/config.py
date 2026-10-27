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
TOPIC_MENSAJE = "prueba"       # llega el texto que hay que decir en voz alta
TOPIC_PARAR = "prueba/parar"   # frena la reproducción
TOPIC_SOS = "prueba/sos"       # lo publica el botón SOS (distinto de TOPIC_MENSAJE
                               # para que la Pi no se lea a sí misma el SOS)

# --- Botones físicos (numeración BCM, no el número de pin de la placa) ---
PIN_SOS = 20   # pin físico 11
PIN_PARAR = 21   # pin físico 13
# El otro extremo de cada botón va a GND (pin físico 9, 14, 20...).
# Se usa la resistencia pull-up interna, no hace falta resistencia externa.

# --- Voz ---
VOZ = "es"
PAUSA_ENTRE_REPETICIONES = 1.0  # segundos
