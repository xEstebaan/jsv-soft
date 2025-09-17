from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)  # usa app/templates y app/static por defecto
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    # Establecer la vista de login por defecto
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    migrate.init_app(app, db)

    # Registrar blueprints aquí (import diferido)
    from .routers.auth import auth_bp

    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        return "OK"

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            app.static_folder + "/img",
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    return app


@login_manager.user_loader
def load_user(user_id):
    # Cargar usuario por id para Flask-Login
    from .models import Usuario  # import diferido para evitar import circular

    return Usuario.query.get(int(user_id))
