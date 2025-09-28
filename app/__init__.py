from flask import Flask, render_template, send_from_directory
import os
import locale
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configurar localización en español
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, "es_ES")
        except locale.Error:
            # Si no se puede configurar la localización, usar una función personalizada
            pass

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    migrate.init_app(app, db)

    # Función personalizada para formatear fechas en español
    def format_date_spanish(date_obj, format_str="%d de %B de %Y"):
        """Formatea una fecha en español"""
        if not date_obj:
            return "No disponible"

        # Nombres de meses en español
        meses_es = {
            1: "enero",
            2: "febrero",
            3: "marzo",
            4: "abril",
            5: "mayo",
            6: "junio",
            7: "julio",
            8: "agosto",
            9: "septiembre",
            10: "octubre",
            11: "noviembre",
            12: "diciembre",
        }

        try:
            # Intentar usar la localización del sistema
            return date_obj.strftime(format_str)
        except:
            # Si falla, usar la función personalizada
            if format_str == "%d de %B de %Y":
                return (
                    f"{date_obj.day} de {meses_es[date_obj.month]} de {date_obj.year}"
                )
            else:
                return str(date_obj)

    # Registrar la función como filtro de Jinja2
    app.jinja_env.filters["fecha_es"] = format_date_spanish

    from .routers.auth import auth_bp
    from .routers.registro import registro_bp
    from .routers.admin import admin_bp
    from .routers.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(registro_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profile_bp)

    @app.route("/")
    def index():
        return render_template("registro/registro.html")

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
    from .models import Usuario

    return Usuario.query.get(int(user_id))
