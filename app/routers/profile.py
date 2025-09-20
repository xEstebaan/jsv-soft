from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .. import db
from ..models import Usuario, Persona, Credencial, TipoCredencial

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    """Vista del perfil del usuario no administrador"""
    # Verificar que el usuario no sea administrador (id_rol = 1)
    if current_user.id_rol == 1:
        flash(
            "Acceso denegado. Esta vista es solo para usuarios no administradores.",
            "danger",
        )
        return redirect(url_for("index"))

    # Obtener datos de la persona asociada al usuario
    persona = Persona.query.get(current_user.id_persona)

    # Obtener el PIN del usuario
    pin_credencial = (
        Credencial.query.join(TipoCredencial)
        .filter(
            Credencial.id_persona == current_user.id_persona,
            TipoCredencial.nombre == "PIN",
            Credencial.activo == True,
        )
        .first()
    )

    pin = pin_credencial.valor if pin_credencial else "No disponible"

    return render_template("auth/profile.html", persona=persona, pin=pin)


@profile_bp.route("/profile/update-personal", methods=["POST"])
@login_required
def update_personal_data():
    """Actualizar datos personales del usuario"""
    if current_user.id_rol == 1:
        return jsonify({"success": False, "message": "Acceso denegado"}), 403

    try:
        # Obtener datos del formulario
        data = request.get_json()

        # Obtener la persona asociada al usuario
        persona = Persona.query.get(current_user.id_persona)
        if not persona:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

        # Actualizar datos
        persona.primer_nombre = data.get("primer_nombre", persona.primer_nombre)
        persona.segundo_nombre = data.get("segundo_nombre", persona.segundo_nombre)
        persona.primer_apellido = data.get("primer_apellido", persona.primer_apellido)
        persona.segundo_apellido = data.get(
            "segundo_apellido", persona.segundo_apellido
        )
        persona.documento = data.get("documento", persona.documento)
        persona.correo = data.get("correo", persona.correo)
        persona.celular = data.get("celular", persona.celular)

        db.session.commit()

        return jsonify({"success": True, "message": "Datos actualizados correctamente"})

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {"success": False, "message": f"Error al actualizar datos: {str(e)}"}
            ),
            500,
        )


@profile_bp.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    """Cambiar contraseña del usuario"""
    if current_user.id_rol == 1:
        return jsonify({"success": False, "message": "Acceso denegado"}), 403

    try:
        # Obtener datos del formulario
        data = request.get_json()
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        # Validaciones
        if not current_password or not new_password or not confirm_password:
            return (
                jsonify(
                    {"success": False, "message": "Todos los campos son requeridos"}
                ),
                400,
            )

        if new_password != confirm_password:
            return (
                jsonify(
                    {"success": False, "message": "Las contraseñas nuevas no coinciden"}
                ),
                400,
            )

        if len(new_password) < 6:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "La nueva contraseña debe tener al menos 6 caracteres",
                    }
                ),
                400,
            )

        # Verificar contraseña actual
        usuario = Usuario.query.get(current_user.id_usuario)
        if not check_password_hash(usuario.contrasena, current_password):
            return (
                jsonify(
                    {"success": False, "message": "La contraseña actual es incorrecta"}
                ),
                400,
            )

        # Actualizar contraseña
        usuario.contrasena = generate_password_hash(new_password)
        db.session.commit()

        return jsonify(
            {"success": True, "message": "Contraseña actualizada correctamente"}
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {"success": False, "message": f"Error al cambiar contraseña: {str(e)}"}
            ),
            500,
        )
