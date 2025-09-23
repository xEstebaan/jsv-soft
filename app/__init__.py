from flask import Flask, render_template, send_from_directory
import os
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

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    migrate.init_app(app, db)

    from .routers.auth import auth_bp
    from .routers.profile import profile_bp
    from .routers.registro import registro_bp
    from .routers.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(registro_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        return render_template("registro/registro.html")

    @app.route("/admin/empleados")
    def empleados():
        return render_template("admin/vista_empleados.html")

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