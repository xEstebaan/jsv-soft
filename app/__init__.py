from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from .models import Usuario

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    # Establecer la vista de login por defecto
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    migrate.init_app(app, db)

    # Registrar blueprints aquí

    return app


@login_manager.user_loader
def load_user(user_id):
    # Cargar usuario por id para Flask-Login
    return Usuario.query.get(int(user_id))
