import json
import queue
import secrets
import string
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import paho.mqtt.client as mqtt

BASE = 'http://127.0.0.1:8090'
TOPIC = 'prueba/sos'
PENDIENTES = queue.Queue(maxsize=100)


def post(ruta, datos, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = token

    pedido = urllib.request.Request(
        BASE + ruta,
        data=json.dumps(datos).encode(),
        headers=headers,
        method='POST'
    )

    with urllib.request.urlopen(pedido, timeout=10) as respuesta:
        return json.load(respuesta)


def guardar(evento_id, credenciales):
    sesion = post(
        '/api/collections/servicio_alertas/auth-with-password',
        {
            'identity': credenciales['email'],
            'password': credenciales['password']
        }
    )
    return post(
        '/api/cerca/alertas/sos',
        {'evento_id': evento_id},
        sesion['token']
    )


def procesar(credenciales):
    while True:
        evento_id = PENDIENTES.get()

        try:
            for intento in range(1, 4):
                try:
                    resultado = guardar(evento_id, credenciales)

                    if not resultado.get('guardada'):
                        raise ValueError('Respuesta inválida')

                    print('SOS guardado en PocketBase.', flush=True)
                    break

                except urllib.error.HTTPError as error:
                    print(
                        f'No se pudo guardar el SOS. PocketBase respondió {error.code}.',
                        flush=True
                    )
                    if error.code < 500:
                        break

                except Exception as error:
                    print(
                        f'No se pudo guardar el SOS: {type(error).__name__}.',
                        flush=True
                    )

                if intento < 3:
                    time.sleep(3)
            else:
                print('El SOS no se pudo guardar tras los intentos.', flush=True)

        finally:
            PENDIENTES.task_done()


def conectado(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print('No se pudo conectar a MQTT.', flush=True)
        return

    client.subscribe(TOPIC, qos=1)


def suscripto(client, userdata, mid, reason_codes, properties):
    if any(code.is_failure for code in reason_codes):
        print('No se pudo escuchar el tema SOS.', flush=True)
    else:
        print('Escuchando SOS. Esperando señal de la Raspberry.', flush=True)


def mensaje(client, userdata, msg):
    if msg.retain:
        print('Se ignoró una señal retenida para no generar una alerta vieja.', flush=True)
        return

    texto = msg.payload.decode('utf-8', errors='replace').strip()

    if not texto.startswith('SOS emergencia '):
        print('Se ignoró un mensaje con formato desconocido.', flush=True)
        return

    evento_id = ''.join(
        secrets.choice(string.ascii_lowercase + string.digits)
        for _ in range(15)
    )

    try:
        PENDIENTES.put_nowait(evento_id)
        print('SOS recibido; intentando guardarlo.', flush=True)
    except queue.Full:
        print('ERROR: SOS no guardado; cola llena.', flush=True)


def main():
    ruta = Path.home() / 'cerca-alertas' / 'credenciales.json'

    with ruta.open(encoding='utf-8') as archivo:
        credenciales = json.load(archivo)

    threading.Thread(
        target=procesar,
        args=(credenciales,),
        daemon=True
    ).start()

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id='cerca-alertas-vm',
        clean_session=True
    )

    client.on_connect = conectado
    client.on_subscribe = suscripto
    client.on_message = mensaje
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.connect_async('127.0.0.1', 1883, keepalive=60)

    try:
        client.loop_forever(retry_first_connection=True)
    except KeyboardInterrupt:
        print('Servicio detenido.', flush=True)
        client.disconnect()


if __name__ == '__main__':
    main()
