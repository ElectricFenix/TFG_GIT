import time
import board
import busio
import sqlite3
import pytz
from datetime import datetime
from digitalio import DigitalInOut, Direction
from adafruit_pn532.spi import PN532_SPI

def tiempo_españa():
    españa_tz = pytz.timezone('Europe/Madrid')
    now_utc = datetime.now(pytz.utc)
    return now_utc.astimezone(españa_tz)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)
pn532 = PN532_SPI(spi, cs_pin, debug=False)
pn532.SAM_configuration()

print("Esperando una tarjeta NFC...")

led_verde = DigitalInOut(board.GPIO17)
led_verde.direction = Direction.OUTPUT

led_rojo = DigitalInOut(board.GPIO27)
led_rojo.direction = Direction.OUTPUT


db_path = "../gaiteapp/instance/data.db"
CLASE_ID = 1  


def registrar_acceso(user_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        ahora = tiempo_españa()
        cursor.execute("""
            INSERT INTO accesos (user_id, clase_id, accedido)
            VALUES (?, ?, ?)
        """, (user_id, CLASE_ID, ahora))

        conn.commit()
        conn.close()
        print(f"✔ Acceso registrado a las {ahora.strftime('%H:%M:%S')}")

    except sqlite3.Error as e:
        print("Error al registrar acceso:", e)

def comprobar_uid(uid_str):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, usuario FROM usuario WHERE nfc_uid = ?", (uid_str,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            user_id, nombre = usuario
            print(f"Acceso concedido → {nombre}")
            registrar_acceso(user_id)
            return True
        else:
            print("UID no encontrado.")
            return False

    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        return False

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        uid_str = ''.join('{:02X}'.format(i) for i in uid)
        print("📡 UID leído:", uid_str)

        acceso = comprobar_uid(uid_str)

        led_verde.value = acceso
        led_rojo.value = not acceso

        time.sleep(3)
        led_verde.value = False
        led_rojo.value = False

        time.sleep(1)
