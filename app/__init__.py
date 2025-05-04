from flask import Flask
from .models import db


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'una-clave-muy-secreta-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    
    from .routes import main
    app.register_blueprint(main)

    return app