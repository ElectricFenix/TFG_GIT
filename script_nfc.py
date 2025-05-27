import time
import board
import busio
import sqlite3
import pytz
import digitalio
from datetime import datetime
from adafruit_pn532.i2c import PN532_I2C

i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()

print("Esperando una tarjeta NFC...")

LED_VERDE = digitalio.DigitalInOut(board.D23)
LED_VERDE.direction = digitalio.Direction.OUTPUT

LED_ROJO = digitalio.DigitalInOut(board.D12)
LED_ROJO.direction = digitalio.Direction.OUTPUT

db_path = "../gaiteapp/instance/data.db"
CLASE_ID = 1

def tiempo_españa():
    españa_tz = pytz.timezone('Europe/Madrid')
    now_utc = datetime.now(pytz.utc)
    return now_utc.astimezone(españa_tz)

def registrar_acceso(user_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        ahora = tiempo_españa()
        cursor.execute("""INSERT INTO accesos (user_id, clase_id, accedido) VALUES (?, ?, ?) """,
                       (user_id, CLASE_ID, ahora))
        conn.commit()
        conn.close()
        print(f"Acceso registrado a las {ahora.strftime('%H:%M:%S')}")
    except sqlite3.Error as e:
        print("Error al registrar acceso:", e)

def comprobar_uid(uid_str):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario FROM users WHERE nfc_uid = ?", (uid_str,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            user_id, nombre = usuario
            print(f"Acceso concedido → {nombre}")
            registrar_acceso(user_id)
            return True
        else:
            print("UID no encontrado en la base de datos.")
            return False

    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        return False

try:
    while True:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid:
            uid_str = ''.join('{:02X}'.format(i) for i in uid)
            print("📡 UID leído:", uid_str)

            acceso = comprobar_uid(uid_str)

            LED_VERDE.value = acceso
            LED_ROJO.value = not acceso

            time.sleep(3)

            LED_VERDE.value = False
            LED_ROJO.value = False

            time.sleep(1)

except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario.")
finally:
    LED_VERDE.value = False
    LED_ROJO.value = False
