import fcntl
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import paho.mqtt.client as mqtt

BASE = 'http://127.0.0.1:8090'
RUTA = '/api/cerca/programados/procesar'


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
    bloqueo = (carpeta / 'ejecutar_programados.lock').open('w')

    try:
        fcntl.flock(bloqueo, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('El programa de recordatorios ya está funcionando.', flush=True)
        return

    with (carpeta / 'credenciales.json').open() as archivo:
        credenciales = json.load(archivo)

    cliente = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id='cerca-programados-vm',
        clean_session=True
    )
    cliente.reconnect_delay_set(min_delay=1, max_delay=30)
    cliente.connect_async('127.0.0.1', 1883, keepalive=60)
    cliente.loop_start()

    token = None
    inicio = None
    esperando = False

    print('Iniciando programa de recordatorios.', flush=True)

    try:
        while True:
            try:
                if not cliente.is_connected():
                    inicio = None
                    if not esperando:
                        print('Esperando conexión MQTT.', flush=True)
                        esperando = True
                    time.sleep(2)
                    continue

                esperando = False

                if not token:
                    token = autenticar(credenciales)

                if inicio is None:
                    inicio = enviar(RUTA, {'iniciar': True}, token)['inicio']
                    print(
                        'Esperando próximos recordatorios. '
                        'Los atrasados no se enviarán.',
                        flush=True
                    )

                respuesta = enviar(RUTA, {'inicio': inicio}, token)

                for item in respuesta['items']:
                    if not cliente.is_connected():
                        print(
                            'Recordatorio procesado, pero MQTT se desconectó.',
                            flush=True
                        )
                        continue

                    resultado = cliente.publish(
                        'prueba', item['texto'], qos=0, retain=False
                    )

                    if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
                        print(
                            'Recordatorio procesado: publicación solicitada a MQTT.',
                            flush=True
                        )
                    else:
                        print(
                            'Recordatorio procesado, pero no se pudo publicar.',
                            flush=True
                        )

                time.sleep(2)

            except urllib.error.HTTPError as error:
                print('Error de PocketBase:', error.code, flush=True)
                if error.code in (401, 403):
                    token = None
                inicio = None
                time.sleep(5)

            except (urllib.error.URLError, OSError, ValueError, KeyError, TypeError) as error:
                print(
                    'No se pudo consultar PocketBase:',
                    type(error).__name__,
                    flush=True
                )
                inicio = None
                time.sleep(5)

    except KeyboardInterrupt:
        print('Programa de recordatorios detenido.', flush=True)
    finally:
        cliente.disconnect()
        cliente.loop_stop()
        bloqueo.close()


if __name__ == '__main__':
    main()
