from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import random
import string
from .. import db
from ..forms.auth import LoginForm, RegistrationForm
from ..models import Usuario, Persona, Credencial, TipoCredencial


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = (
            Usuario.query.join(Persona, Usuario.id_persona == Persona.id_persona)
            .filter(Persona.correo == form.correo.data)
            .first()
        )
        if usuario and check_password_hash(usuario.contrasena, form.contrasena.data):
            login_user(usuario, remember=form.recordar.data)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("profile.profile"))
        flash("Credenciales inválidas", "danger")
    return render_template("auth/form.html", form=form, form_type="login")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("profile.profile"))

    form = RegistrationForm()

    # Si es una petición AJAX y hay errores de validación, devolver JSON
    if request.method == "POST" and not form.validate():
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = (
                    field_errors[0] if field_errors else "Error de validación"
                )

            return jsonify(
                {
                    "success": False,
                    "message": "Error de validación en el formulario",
                    "errors": errors,
                }
            )

    if form.validate_on_submit():
        try:
            # Crear persona
            persona = Persona(
                primer_nombre=form.primer_nombre.data,
                segundo_nombre=form.segundo_nombre.data or None,
                primer_apellido=form.primer_apellido.data,
                segundo_apellido=form.segundo_apellido.data or None,
                documento=form.documento.data,
                correo=form.correo.data,
                celular=form.celular.data or None,
            )
            db.session.add(persona)
            db.session.flush()

            # Crear usuario
            usuario = Usuario(
                id_persona=persona.id_persona,
                id_rol=2,
                contrasena=generate_password_hash(form.contrasena.data),
            )
            db.session.add(usuario)

            # Generar PIN con formato: 3 primeras letras del nombre + 4 números
            pin = generate_pin(form.primer_nombre.data)

            # Obtener o crear el tipo de credencial PIN
            tipo_pin = TipoCredencial.query.filter_by(nombre="PIN").first()
            if not tipo_pin:
                tipo_pin = TipoCredencial(nombre="PIN")
                db.session.add(tipo_pin)
                db.session.flush()

            # Crear credencial PIN
            credencial = Credencial(
                id_persona=persona.id_persona,
                id_tipo_credencial=tipo_pin.id_tipo_credencial,
                valor=pin,
                activo=True,
            )
            db.session.add(credencial)

            db.session.commit()

            # Si es una petición AJAX, devolver JSON
            if (
                request.headers.get("Content-Type") == "application/json"
                or request.is_json
                or request.headers.get("X-Requested-With") == "XMLHttpRequest"
            ):
                return jsonify(
                    {
                        "success": True,
                        "pin": pin,
                        "message": "Usuario creado correctamente",
                    }
                )

            # Si no es AJAX, mostrar modal (esto se manejará con JavaScript)
            return render_template(
                "auth/form.html",
                form=form,
                form_type="register",
                show_pin_modal=True,
                generated_pin=pin,
            )

        except Exception as e:
            db.session.rollback()
            print(f"Error en registro: {str(e)}")  # Log del error
            import traceback

            traceback.print_exc()  # Log completo del error

            if (
                request.headers.get("Content-Type") == "application/json"
                or request.is_json
                or request.headers.get("X-Requested-With") == "XMLHttpRequest"
            ):
                return jsonify(
                    {
                        "success": False,
                        "message": f"Error al registrar: {str(e)}",
                    }
                )
            flash(
                f"Error al registrar: {str(e)}",
                "danger",
            )
    return render_template("auth/form.html", form=form, form_type="register")


def generate_pin(primer_nombre):
    """Genera un PIN con formato: 3 primeras letras del nombre + 4 números aleatorios"""
    # Tomar las primeras 3 letras del nombre (en mayúsculas)
    letras = primer_nombre[:3].upper()

    # Generar 4 números aleatorios
    numeros = "".join(random.choices(string.digits, k=4))

    pin = letras + numeros

    # Verificar que el PIN no exista
    while True:
        existing = (
            Credencial.query.join(TipoCredencial)
            .filter(TipoCredencial.nombre == "PIN", Credencial.valor == pin)
            .first()
        )
        if not existing:
            break
        # Si existe, generar nuevos números
        numeros = "".join(random.choices(string.digits, k=4))
        pin = letras + numeros

    return pin


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
