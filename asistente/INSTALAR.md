# Instalar el asistente en la Raspberry Pi

Todo esto se hace por SSH en la Pi (usuario `pi`; si usás otro, cambialo también en `asistente.service`).

## 1. Subir estos archivos al repo
Poné esta carpeta como `asistente/` dentro de tu repo `AsistententeParaMayores-sebas`, hacé commit y push desde tu PC.

## 2. Preparar la Pi
```
sudo apt update
sudo apt install -y git espeak-ng python3-venv python3-gpiozero python3-lgpio
cd ~
git clone https://github.com/solp3rez/AsistententeParaMayores-sebas.git
python3 -m venv --system-site-packages ~/venv-asistente
~/venv-asistente/bin/pip install -r ~/AsistententeParaMayores-sebas/asistente/requirements.txt
```
(`--system-site-packages` es para que el entorno vea `gpiozero`, que se instaló con apt.)

## 3. Probar a mano antes de dejarlo como servicio
```
cd ~/AsistententeParaMayores-sebas/asistente
~/venv-asistente/bin/python main.py
```
Tendría que decir "Conectado a 10.56.31.11:1883". Desde tu PC corré `prueba.py`: la Pi habla el mensaje en loop. Con `botonParar.py` (o el botón físico de parar) se frena. Cortá con Ctrl+C.

## 4. Que arranque solo
```
sudo cp ~/AsistententeParaMayores-sebas/asistente/asistente.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now asistente.service
```
- Estado: `systemctl status asistente.service`
- Logs en vivo: `journalctl -u asistente.service -f`
- Después de un `git pull`: `sudo systemctl restart asistente.service`

## Conexión de los botones
Cada botón une un pin GPIO con GND (no hace falta resistencia):

| Botón | GPIO (BCM) | Pin físico | Otro extremo |
|-------|-----------|------------|--------------|
| SOS   | 17        | 11         | GND (pin 9)  |
| Parar | 27        | 13         | GND (pin 14) |

Si usás otros pines, cambialos en `config.py`.

## Si el servidor pide usuario y clave
Crear `/etc/asistente.env` (fuera del repo):
```
sudo nano /etc/asistente.env
```
con estas dos líneas:
```
MQTT_USER=tu_usuario
MQTT_PASS=tu_clave
```
Y protegerlo: `sudo chmod 600 /etc/asistente.env`. Después `sudo systemctl restart asistente.service`.

## Si no suena
- Probá `espeak-ng -v es "hola"` a mano. Si ahí no suena, es la salida de audio: `sudo raspi-config` → System Options → Audio (jack o HDMI).
- Si suena a mano pero no como servicio, descomentá la línea `XDG_RUNTIME_DIR` de `asistente.service`.
