from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Crea el objeto db para la base de datos
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos (asegúrate de tener configurada la URI)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'  # Si usas SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactiva las modificaciones de seguimiento

    db.init_app(app)

    return app
