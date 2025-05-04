from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

def get_spanish_time():
    españa_tz = pytz.timezone('Europe/Madrid')
    now_utc = datetime.now(pytz.utc)
    now_españa = now_utc.astimezone(españa_tz)
    return now_españa

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50))
    nfc_uid = db.Column(db.String(100), unique=True, nullable=False)
    usuario_creado = db.Column(db.DateTime, default=get_spanish_time)

    accesos = db.relationship('Acceso', back_populates='user', cascade='all, delete-orphan')


class Clase(db.Model):
    __tablename__ = 'clase'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text)

    accesos = db.relationship('Acceso', back_populates='clase', cascade='all, delete-orphan')


class Acceso(db.Model):
    __tablename__ = 'accesos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    clase_id = db.Column(db.Integer, db.ForeignKey('clase.id'), nullable=False)
    accedido = db.Column(db.DateTime, default=get_spanish_time)

    user = db.relationship('User', back_populates='accesos')
    clase = db.relationship('Clase', back_populates='accesos')
