from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from .. import db
from ..models import (
    Usuario,
    Persona,
    Credencial,
    TipoCredencial,
    Registro,
    TipoRegistro,
    Empleado,
    CargoEmpleado,
)

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

    # Obtener datos del empleado con la relación del cargo cargada
    empleado = (
        Empleado.query.join(CargoEmpleado, Empleado.cargo_id == CargoEmpleado.id_cargo)
        .filter(Empleado.id_persona == current_user.id_persona)
        .first()
    )

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

    return render_template(
        "auth/profile.html", persona=persona, empleado=empleado, pin=pin
    )


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


@profile_bp.route("/profile/history", methods=["GET"])
@login_required
def get_history():
    """Obtener historial de registros por semana"""
    if current_user.id_rol == 1:
        return jsonify({"success": False, "message": "Acceso denegado"}), 403

    try:
        week_string = request.args.get("week")
        if not week_string:
            return (
                jsonify({"success": False, "message": "Parámetro de semana requerido"}),
                400,
            )

        # Ajustar para que se muestre la fecha en (formato: YYYY-WWW)
        year, week = week_string.split("-W")
        year = int(year)
        week = int(week)

        # Calcular el rango de fechas para la semana solicitada
        # Encontrar el primer día del año
        jan_1 = datetime(year, 1, 1)

        # Obtener el día de la semana de enero 1
        jan_1_iso_year, jan_1_iso_week, jan_1_weekday = jan_1.isocalendar()

        # Calcular el primer lunes del año
        if jan_1_iso_week > 1:
            jan_4 = datetime(year, 1, 4)
            days_to_monday = (jan_4.weekday()) % 7
            first_monday = jan_4 - timedelta(days=days_to_monday)
        else:
            days_to_monday = (jan_1.weekday()) % 7
            first_monday = jan_1 - timedelta(days=days_to_monday)

        # Calcular el inicio y fin de la semana
        week_start = first_monday + timedelta(weeks=week - 1)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

        # Obtener el PIN del usuario actual
        pin_credencial = (
            Credencial.query.join(TipoCredencial)
            .filter(
                Credencial.id_persona == current_user.id_persona,
                TipoCredencial.nombre == "PIN",
                Credencial.activo == True,
            )
            .first()
        )

        if not pin_credencial:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "No se encontró PIN para este usuario",
                    }
                ),
                400,
            )

        # Buscar registros por el PIN del usuario (no por id_persona)
        # Esto permite que el usuario vea los registros hechos con su PIN
        registros = (
            Registro.query.join(TipoRegistro)
            .join(Credencial)
            .filter(
                Credencial.valor == pin_credencial.valor,
                Registro.fecha_hora >= week_start,
                Registro.fecha_hora <= week_end,
            )
            .order_by(Registro.fecha_hora)
            .all()
        )

        # Format the data for JSON response
        registros_data = []
        for registro in registros:
            registros_data.append(
                {
                    "fecha_hora": registro.fecha_hora.isoformat(),
                    "tipo_registro": registro.tipo_registro.descripcion,
                    "observacion": registro.observacion,
                }
            )

        return jsonify(
            {
                "success": True,
                "registros": registros_data,
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
            }
        )

    except ValueError as e:
        return jsonify({"success": False, "message": "Formato de semana inválido"}), 400
    except Exception as e:
        return (
            jsonify(
                {"success": False, "message": f"Error al obtener historial: {str(e)}"}
            ),
            500,
        )
