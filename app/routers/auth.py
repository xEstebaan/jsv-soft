from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .. import db
from ..forms.auth import LoginForm, RegistrationForm
from ..models import Usuario, Persona


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
            return redirect(next_page or url_for("index"))
        flash("Credenciales inválidas", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()
    if form.validate_on_submit():
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

        usuario = Usuario(
            id_persona=persona.id_persona,
            id_rol=2,
            contrasena=generate_password_hash(form.contrasena.data),
        )
        db.session.add(usuario)
        db.session.commit()
        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
