from app import create_app
from app.models import db, User, Clase, Acceso
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():
    db.drop_all()  # Limpia la base de datos anterior
    db.create_all()

    # Crear usuarios con contraseñas cifradas
    user1 = User(
        usuario='juan',
        email='juan@example.com',
        password_hash=generate_password_hash('1234'),
        rol='estudiante',
        nfc_uid='04AABBCCDD11'
    )

    user2 = User(
        usuario='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('admin'),
        rol='admin',
        nfc_uid='04DDEEFF0011'
    )

    # Crear clases
    clase1 = Clase(nombre='Aula 101', capacidad=30, descripcion='Laboratorio de informática')
    clase2 = Clase(nombre='Aula 202', capacidad=25, descripcion='Sala de reuniones')

    # Guardar usuarios y clases
    db.session.add_all([user1, user2, clase1, clase2])
    db.session.commit()

    # Crear accesos
    acceso1 = Acceso(user_id=user1.id, clase_id=clase1.id, accedido=datetime.now())
    acceso2 = Acceso(user_id=user2.id, clase_id=clase2.id, accedido=datetime.now())

    db.session.add_all([acceso1, acceso2])
    db.session.commit()

    print("Datos de prueba insertados con contraseñas encriptadas y NFC.")
