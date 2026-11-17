import fcntl
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import paho.mqtt.client as mqtt

BASE = 'http://127.0.0.1:8090'
RUTA = '/api/cerca/mensajes/nuevos'
TOPIC = 'prueba'


def enviar(ruta, datos, token=None):
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


def autenticar(credenciales):
    respuesta = enviar(
        '/api/collections/servicio_alertas/auth-with-password',
        {
            'identity': credenciales['email'],
            'password': credenciales['password']
        }
    )
    return respuesta['token']


def main():
    carpeta = Path.home() / 'cerca-alertas'
    bloqueo = (carpeta / 'enviar_mensajes.lock').open('w')

    try:
        fcntl.flock(bloqueo, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('El mensajero ya está funcionando.', flush=True)
        return

    with (carpeta / 'credenciales.json').open() as archivo:
        credenciales = json.load(archivo)

    cliente = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id='cerca-mensajes-vm',
        clean_session=True
    )
    cliente.reconnect_delay_set(min_delay=1, max_delay=30)
    cliente.connect_async('127.0.0.1', 1883, keepalive=60)
    cliente.loop_start()

    token = None
    cursor = None
    print('Iniciando mensajero. No se enviarán mensajes viejos.', flush=True)

    try:
        while True:
            try:
                if not token:
                    token = autenticar(credenciales)

                if cursor is None:
                    cursor = enviar(RUTA, {'iniciar': True}, token)
                    if not cursor.get('fecha') or not cursor.get('id'):
                        raise ValueError('Inicio inválido')
                    print('Esperando mensajes nuevos.', flush=True)

                respuesta = enviar(RUTA, cursor, token)
                items = respuesta['items']

                for item in items:
                    if item.get('texto'):
                        if cliente.is_connected():
                            resultado = cliente.publish(
                                TOPIC, item['texto'], qos=0, retain=False
                            )
                            if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
                                print('Publicación solicitada a MQTT.', flush=True)
                            else:
                                print('No se pudo publicar el mensaje.', flush=True)
                        else:
                            print('Mensaje omitido: MQTT desconectado.', flush=True)

                    cursor = {'fecha': item['fecha'], 'id': item['id']}

                time.sleep(1 if len(items) == 50 else 2)

            except urllib.error.HTTPError as error:
                print('Error de PocketBase:', error.code, flush=True)
                if error.code in (401, 403):
                    token = None
                cursor = None
                time.sleep(5)

            except (urllib.error.URLError, OSError, ValueError, KeyError) as error:
                print('No se pudo consultar PocketBase:', type(error).__name__, flush=True)
                cursor = None
                time.sleep(5)

    except KeyboardInterrupt:
        print('Mensajero detenido.', flush=True)
    finally:
        cliente.disconnect()
        cliente.loop_stop()
        bloqueo.close()


if __name__ == '__main__':
    main()
