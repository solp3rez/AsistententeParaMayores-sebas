import subprocess
import threading
import paho.mqtt.client as mqtt

broker = "10.56.31.11"
puerto = 1883
topic = "prueba"
topic_parar = "prueba/parar"

parar = threading.Event()
hilo = None
proceso = None

def repetir(texto):
    global proceso
    while not parar.is_set():
        proceso = subprocess.Popen(["espeak-ng", "-v", "es", texto])
        proceso.wait()
        parar.wait(1)  # pausa de 1 s entre repeticiones

def on_connect(client, userdata, flags, reason_code, properties):
    print("Conectado:", reason_code)
    client.subscribe([(topic, 0), (topic_parar, 0)])

def on_message(client, userdata, msg):
    global hilo
    texto = msg.payload.decode("utf-8")

    if msg.topic == topic_parar:
        print("Botón de parar presionado")
        parar.set()
        if proceso and proceso.poll() is None:
            proceso.terminate()
    else:
        print("Recibido:", texto)
        if hilo and hilo.is_alive():
            return  # ya está sonando
        parar.clear()
        hilo = threading.Thread(target=repetir, args=(texto,), daemon=True)
        hilo.start()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, puerto, 60)
client.loop_forever()