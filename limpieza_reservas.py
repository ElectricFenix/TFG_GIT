import sqlite3
from datetime import datetime, timedelta
import pytz

DB_PATH = "../gaiteapp/instance/data.db"

tz = pytz.timezone('Europe/Madrid')

def obtener_fecha_dia_anterior():
    ahora = datetime.now(tz)
    ayer = ahora - timedelta(days=1)
    return ayer.date()

def borrar_reservas_dia_anterior():
    fecha_ayer = obtener_fecha_dia_anterior()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        inicio = datetime.combine(fecha_ayer, datetime.min.time())
        fin = datetime.combine(fecha_ayer, datetime.max.time())

        print(f"Borrando reservas del {fecha_ayer}...")

        cursor.execute("""
            DELETE FROM reservas
            WHERE fecha_reserva >= ? AND fecha_reserva <= ?
        """, (inicio, fin))

        conn.commit()
        print(f"{cursor.rowcount} reserva(s) eliminada(s).")

    except sqlite3.Error as e:
        print("Error al acceder a la base de datos:", e)

    finally:
        conn.close()

if __name__ == "__main__":
    borrar_reservas_dia_anterior()
