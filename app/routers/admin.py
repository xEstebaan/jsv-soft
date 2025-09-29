from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models.empleado import Empleado
from app.models.persona import Persona
from app.models.cargo_empleado import CargoEmpleado
from app.models.credencial import Credencial
from app.models.tipo_credencial import TipoCredencial
from app.models.usuarios import Usuario
from app.models.registro import Registro
from app.models.tipo_registro import TipoRegistro
from werkzeug.security import generate_password_hash
from datetime import datetime
import random
import string
from flask_login import login_required, current_user
from functools import wraps

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Verificar si el usuario es administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Validar el rol del usuario admin
        if not current_user.is_authenticated or current_user.id_rol != 1:
            flash("No tienes permisos para acceder a esta sección", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route("/empleados", methods=["GET"])
@login_required
@admin_required
def lista_empleados():
    # Lista de empleados
    empleados = (
        Empleado.query.join(Persona, Empleado.id_persona == Persona.id_persona)
        .join(CargoEmpleado, Empleado.cargo_id == CargoEmpleado.id_cargo)
        .add_columns(
            Persona.primer_nombre,
            Persona.segundo_nombre,
            Persona.primer_apellido,
            Persona.segundo_apellido,
            Persona.documento,
            Persona.fecha_creacion,
            CargoEmpleado.descripcion.label("cargo"),
            Empleado.empleado_id,
            Empleado.fecha_contratacion,
            Empleado.id_persona,
        )
        .all()
    )

    # Obtenemos información sobre las credenciales de cada empleado
    empleados_con_credenciales = []
    for emp in empleados:
        credencial = (
            Credencial.query.join(TipoCredencial)
            .filter(
                Credencial.id_persona == emp.id_persona, TipoCredencial.nombre == "PIN"
            )
            .first()
        )

        tiene_credencial = credencial is not None
        credencial_activa = tiene_credencial and credencial.activo

        empleados_con_credenciales.append(
            {
                "info": emp,
                "tiene_credencial": tiene_credencial,
                "credencial_activa": credencial_activa,
            }
        )

    return render_template(
        "admin/vista_empleados.html",
        empleados_con_credenciales=empleados_con_credenciales,
    )


@admin_bp.route("/empleados/crear", methods=["GET", "POST"])
def crear_empleado():
    # Cargar los cargos disponibles
    cargos = CargoEmpleado.query.all()

    if request.method == "POST":
        try:
            # Datos de la persona
            primer_nombre = request.form.get("primer_nombre")
            segundo_nombre = request.form.get("segundo_nombre", "")
            primer_apellido = request.form.get("primer_apellido")
            segundo_apellido = request.form.get("segundo_apellido", "")
            documento = request.form.get("documento")
            correo = request.form.get("correo")
            celular = request.form.get("celular", "")

            # Datos de acceso
            contrasena = request.form.get("contrasena")
            confirmar_contrasena = request.form.get("confirmar_contrasena")

            # Datos del empleado
            cargo_id = request.form.get("cargo_id", type=int)
            fecha_contratacion = request.form.get("fecha_contratacion")

            # Validaciones básicas
            if (
                not primer_nombre
                or not primer_apellido
                or not documento
                or not correo
                or not cargo_id
                or not fecha_contratacion
                or not contrasena
                or not confirmar_contrasena
            ):
                flash("Todos los campos marcados con * son obligatorios", "error")
                return render_template("admin/crear_empleado.html", cargos=cargos)

            # Validar formato de correo electrónico
            import re

            email_pattern = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            if not email_pattern.match(correo):
                flash("El formato del correo electrónico no es válido", "error")
                return render_template("admin/crear_empleado.html", cargos=cargos)

            # Validar que las contraseñas coincidan
            if contrasena != confirmar_contrasena:
                flash("Las contraseñas no coinciden", "error")
                return render_template("admin/crear_empleado.html", cargos=cargos)

            # Validar longitud mínima de contraseña
            if len(contrasena) < 6:
                flash("La contraseña debe tener al menos 6 caracteres", "error")
                return render_template("admin/crear_empleado.html", cargos=cargos)

            # Verificar si la persona ya existe (por documento o correo)
            persona_existente = Persona.query.filter(
                (Persona.documento == documento) | (Persona.correo == correo)
            ).first()

            if persona_existente:
                flash("Ya existe una persona con ese documento o correo", "error")
                return render_template("admin/crear_empleado.html", cargos=cargos)

            # Crear persona
            persona = Persona(
                primer_nombre=primer_nombre,
                segundo_nombre=segundo_nombre if segundo_nombre else None,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido if segundo_apellido else None,
                documento=documento,
                correo=correo,
                celular=celular if celular else None,
            )

            db.session.add(persona)
            db.session.flush()  # Para obtener el ID de la persona

            # Crear empleado
            fecha_contratacion_obj = datetime.strptime(
                fecha_contratacion, "%Y-%m-%d"
            ).date()
            empleado = Empleado(
                id_persona=persona.id_persona,
                cargo_id=cargo_id,
                fecha_contratacion=fecha_contratacion_obj,
            )

            db.session.add(empleado)

            # Generar PIN para el empleado
            pin = generate_pin(primer_nombre)

            # Obtener o crear el tipo de credencial PIN
            tipo_pin = TipoCredencial.query.filter_by(nombre="PIN").first()
            if not tipo_pin:
                tipo_pin = TipoCredencial(nombre="PIN")
                db.session.add(tipo_pin)
                db.session.flush()

            # Crear credencial PIN para el empleado
            credencial = Credencial(
                id_persona=persona.id_persona,
                id_tipo_credencial=tipo_pin.id_tipo_credencial,
                valor=pin,
                activo=True,
            )

            db.session.add(credencial)

            # Crear un usuario para el empleado (para poder iniciar sesión)
            usuario = Usuario(
                id_persona=persona.id_persona,
                id_rol=2,
                contrasena=generate_password_hash(contrasena),
            )

            db.session.add(usuario)
            db.session.commit()

            flash(f"Empleado creado con éxito. PIN generado: {pin}", "success")
            flash(
                f"Se ha creado un usuario con el correo: {correo} y la contraseña que has establecido.",
                "info",
            )
            return redirect(url_for("admin.lista_empleados"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear el empleado: {str(e)}", "error")

    return render_template("admin/crear_empleado.html", cargos=cargos)


@admin_bp.route("/reportes", methods=["GET"])
def reportes():
    """Vista de reportes para administradores"""
    # Obtener todos los empleados para el contador
    empleados = (
        Empleado.query.join(Persona, Empleado.id_persona == Persona.id_persona)
        .add_columns(
            Persona.primer_nombre,
            Persona.segundo_nombre,
            Persona.primer_apellido,
            Persona.segundo_apellido,
            Empleado.empleado_id,
        )
        .all()
    )

    # Obtener parámetros de filtro
    busqueda_nombre = request.args.get("busqueda_nombre", "").strip()
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")

    # Validar fechas
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

            if fecha_inicio_obj > fecha_fin_obj:
                # Si la fecha de inicio es mayor que la fecha de fin, intercambiar las fechas
                fecha_inicio, fecha_fin = fecha_fin, fecha_inicio
                fecha_inicio_obj, fecha_fin_obj = fecha_fin_obj, fecha_inicio_obj
        except ValueError:
            # Si hay error en el formato de fechas, limpiar las fechas
            fecha_inicio = None
            fecha_fin = None

    # Construir consulta base para registros
    query = (
        Registro.query.join(Persona, Registro.id_persona == Persona.id_persona)
        .join(TipoRegistro, Registro.id_tipo_registro == TipoRegistro.id_tipo_registro)
        .add_columns(
            Persona.primer_nombre,
            Persona.segundo_nombre,
            Persona.primer_apellido,
            Persona.segundo_apellido,
            Registro.fecha_hora,
            Registro.id_tipo_registro,
            TipoRegistro.descripcion.label("tipo_registro"),
        )
    )

    # Aplicar filtros
    if busqueda_nombre:
        # Buscar por nombre completo (primer nombre, segundo nombre, primer apellido, segundo apellido)
        busqueda_terms = busqueda_nombre.split()
        condiciones = []

        for term in busqueda_terms:
            term_like = f"%{term}%"
            condiciones.append(
                db.or_(
                    Persona.primer_nombre.ilike(term_like),
                    Persona.segundo_nombre.ilike(term_like),
                    Persona.primer_apellido.ilike(term_like),
                    Persona.segundo_apellido.ilike(term_like),
                )
            )

        # Combinar todas las condiciones con AND (todos los términos deben coincidir)
        if condiciones:
            query = query.filter(db.and_(*condiciones))

    if fecha_inicio:
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        # Convertir a datetime para comparación precisa
        fecha_inicio_datetime = datetime.combine(fecha_inicio_obj, datetime.min.time())
        query = query.filter(Registro.fecha_hora >= fecha_inicio_datetime)

    if fecha_fin:
        # Para la fecha fin, incluir todo el día (hasta las 23:59:59)
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        fecha_fin_completa = datetime.combine(fecha_fin_obj, datetime.max.time())
        query = query.filter(Registro.fecha_hora <= fecha_fin_completa)

    # Ordenar por fecha descendente
    registros = query.order_by(Registro.fecha_hora.desc()).all()

    # Procesar registros para crear pares de ingreso-salida
    registros_procesados = []

    # Agrupar registros por empleado y fecha
    registros_por_empleado_fecha = {}

    for registro in registros:
        empleado_nombre = f"{registro.primer_nombre} {registro.segundo_nombre if registro.segundo_nombre else ''} {registro.primer_apellido} {registro.segundo_apellido if registro.segundo_apellido else ''}".strip()
        fecha = registro.fecha_hora.date()
        hora = registro.fecha_hora.time()
        tipo = registro.tipo_registro

        # Crear clave única por empleado y fecha
        clave = f"{empleado_nombre}_{fecha}"

        if clave not in registros_por_empleado_fecha:
            registros_por_empleado_fecha[clave] = {
                "empleado": empleado_nombre,
                "fecha": fecha,
                "ingresos": [],
                "salidas": [],
            }

        # Agregar a la lista correspondiente
        if registro.id_tipo_registro == 1:  # ID 1 = Ingreso
            registros_por_empleado_fecha[clave]["ingresos"].append(hora)
        elif registro.id_tipo_registro == 2:  # ID 2 = Salida
            registros_por_empleado_fecha[clave]["salidas"].append(hora)

    # Crear pares de ingreso-salida
    for clave, datos in registros_por_empleado_fecha.items():
        ingresos = sorted(datos["ingresos"])
        salidas = sorted(datos["salidas"])

        # Crear registros separados para cada ingreso (todos los ingresos deben mostrarse)
        for ingreso in ingresos:
            registros_procesados.append(
                {
                    "empleado": datos["empleado"],
                    "fecha": datos["fecha"],
                    "hora_entrada": ingreso,
                    "hora_salida": None,  # Inicialmente sin salida
                }
            )
            
        # Crear registros para cada salida que no tenga ingreso correspondiente
        for salida in salidas:
            # Intentar encontrar un registro existente que pueda emparejar con esta salida
            match_found = False
            for registro in registros_procesados:
                # Si es del mismo empleado, misma fecha, tiene entrada pero no tiene salida y la entrada es anterior a la salida
                if (registro["empleado"] == datos["empleado"] and 
                    registro["fecha"] == datos["fecha"] and 
                    registro["hora_entrada"] and 
                    not registro["hora_salida"] and
                    registro["hora_entrada"] < salida):
                    
                    # Asignar esta salida al registro
                    registro["hora_salida"] = salida
                    match_found = True
                    break
            
            # Si no se encontró un registro para emparejar, crear uno nuevo
            if not match_found:
                registros_procesados.append(
                    {
                        "empleado": datos["empleado"],
                        "fecha": datos["fecha"],
                        "hora_entrada": None,
                        "hora_salida": salida,
                    }
                )

    # Filtrar registros procesados para asegurar que estén dentro del rango de fechas
    registros_filtrados = []
    for registro in registros_procesados:
        fecha_registro = registro["fecha"]

        # Verificar que la fecha esté dentro del rango especificado
        fecha_valida = True

        if fecha_inicio and fecha_registro < fecha_inicio_obj:
            fecha_valida = False
        if fecha_fin and fecha_registro > fecha_fin_obj:
            fecha_valida = False

        if fecha_valida:
            registros_filtrados.append(registro)

    # Ordenar por fecha descendente y luego por hora de entrada
    registros_filtrados.sort(
        key=lambda x: (x["fecha"], x["hora_entrada"] or x["hora_salida"]), reverse=True
    )

    # Calcular métricas
    total_empleados = len(empleados)
    hoy = datetime.now().date()
    entradas_hoy = Registro.query.filter(
        Registro.fecha_hora >= hoy, Registro.id_tipo_registro == 1  # Tipo ingreso
    ).count()
    salidas_hoy = Registro.query.filter(
        Registro.fecha_hora >= hoy, Registro.id_tipo_registro == 2  # Tipo salida
    ).count()

    return render_template(
        "admin/reportes.html",
        registros=registros_filtrados,
        total_empleados=total_empleados,
        entradas_hoy=entradas_hoy,
        salidas_hoy=salidas_hoy,
        busqueda_nombre=busqueda_nombre,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


def generate_pin(primer_nombre):
    # Función para generar pin
    nombre_seguro = primer_nombre.strip().upper()
    while len(nombre_seguro) < 3:
        nombre_seguro += "X"
    letras = nombre_seguro[:3]

    numeros = "".join(random.choices(string.digits, k=4))

    pin = letras + numeros

    # Verificar que el PIN no exista
    tries = 0
    max_tries = 10

    while tries < max_tries:
        try:
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
            tries += 1
        except Exception as e:
            # Manejo de excepciones de base de datos
            print(f"Error al verificar PIN existente: {str(e)}")
            break

    return pin


@admin_bp.route("/empleados/ver/<int:empleado_id>", methods=["GET"])
def ver_empleado(empleado_id):
    # Obtener información del empleado
    empleado = Empleado.query.get_or_404(empleado_id)
    persona = Persona.query.get_or_404(empleado.id_persona)
    cargo = CargoEmpleado.query.get_or_404(empleado.cargo_id)

    # Obtener credencial PIN
    credencial_pin = (
        Credencial.query.join(TipoCredencial)
        .filter(
            Credencial.id_persona == persona.id_persona, TipoCredencial.nombre == "PIN"
        )
        .first()
    )

    # Calcular el tiempo en la empresa
    fecha_contratacion = empleado.fecha_contratacion
    hoy = datetime.now().date()
    delta = hoy - fecha_contratacion
    anios = delta.days // 365
    meses = (delta.days % 365) // 30

    tiempo_empresa = ""
    if anios > 0:
        tiempo_empresa += f"{anios} año{'s' if anios != 1 else ''}"
    if meses > 0:
        tiempo_empresa += (
            f"{' y ' if tiempo_empresa else ''}{meses} mes{'es' if meses != 1 else ''}"
        )
    if not tiempo_empresa:
        tiempo_empresa = "Menos de un mes"

    return render_template(
        "admin/ver_empleado.html",
        empleado=empleado,
        persona=persona,
        cargo=cargo,
        credencial_pin=credencial_pin,
        tiempo_empresa=tiempo_empresa,
    )


@admin_bp.route("/empleados/editar/<int:empleado_id>", methods=["GET", "POST"])
def editar_empleado(empleado_id):
    # Editar la información del empleado
    # Obtener información del empleado
    empleado = Empleado.query.get_or_404(empleado_id)
    persona = Persona.query.get_or_404(empleado.id_persona)
    usuario = Usuario.query.filter_by(id_persona=persona.id_persona).first()
    cargos = CargoEmpleado.query.all()

    if request.method == "POST":
        try:
            # Datos de la persona
            primer_nombre = request.form.get("primer_nombre")
            segundo_nombre = request.form.get("segundo_nombre", "")
            primer_apellido = request.form.get("primer_apellido")
            segundo_apellido = request.form.get("segundo_apellido", "")
            documento = request.form.get("documento")
            correo = request.form.get("correo")
            celular = request.form.get("celular", "")

            # Datos de acceso (opcionales)
            contrasena = request.form.get("contrasena")
            confirmar_contrasena = request.form.get("confirmar_contrasena")

            # Datos del empleado
            cargo_id = request.form.get("cargo_id", type=int)
            fecha_contratacion = request.form.get("fecha_contratacion")

            if (
                not primer_nombre
                or not primer_apellido
                or not documento
                or not correo
                or not cargo_id
                or not fecha_contratacion
            ):
                flash("Todos los campos marcados con * son obligatorios", "error")
                return render_template(
                    "admin/editar_empleado.html",
                    empleado=empleado,
                    persona=persona,
                    cargos=cargos,
                )

            # Validar el correo electrónico
            import re

            email_pattern = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            if not email_pattern.match(correo):
                flash("El formato del correo electrónico no es válido", "error")
                return render_template(
                    "admin/editar_empleado.html",
                    empleado=empleado,
                    persona=persona,
                    cargos=cargos,
                )

            # Verificar si otro empleado ya tiene el mismo documento o correo
            persona_existente = Persona.query.filter(
                (Persona.documento == documento) | (Persona.correo == correo),
                Persona.id_persona != persona.id_persona,
            ).first()

            if persona_existente:
                flash("Ya existe otra persona con ese documento o correo", "error")
                return render_template(
                    "admin/editar_empleado.html",
                    empleado=empleado,
                    persona=persona,
                    cargos=cargos,
                )

            # Actualizar datos de la persona
            persona.primer_nombre = primer_nombre
            persona.segundo_nombre = segundo_nombre if segundo_nombre else None
            persona.primer_apellido = primer_apellido
            persona.segundo_apellido = segundo_apellido if segundo_apellido else None
            persona.documento = documento
            persona.correo = correo
            persona.celular = celular if celular else None

            if contrasena and contrasena.strip() != "":
                # Validar contraseña
                if len(contrasena) < 6:
                    flash("La contraseña debe tener al menos 6 caracteres", "error")
                    return render_template(
                        "admin/editar_empleado.html",
                        empleado=empleado,
                        persona=persona,
                        cargos=cargos,
                    )

                if contrasena != confirmar_contrasena:
                    flash("Las contraseñas no coinciden", "error")
                    return render_template(
                        "admin/editar_empleado.html",
                        empleado=empleado,
                        persona=persona,
                        cargos=cargos,
                    )

                if usuario:
                    usuario.contrasena = generate_password_hash(contrasena)

            fecha_contratacion_obj = datetime.strptime(
                fecha_contratacion, "%Y-%m-%d"
            ).date()
            empleado.cargo_id = cargo_id
            empleado.fecha_contratacion = fecha_contratacion_obj

            db.session.commit()

            flash("Empleado actualizado correctamente", "success")
            return redirect(url_for("admin.lista_empleados"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar el empleado: {str(e)}", "error")

    return render_template(
        "admin/editar_empleado.html", empleado=empleado, persona=persona, cargos=cargos
    )


@admin_bp.route("/empleados/credencial/<int:empleado_id>/toggle", methods=["POST"])
def toggle_credencial_empleado(empleado_id):
    try:
        # Obtener el empleado
        empleado = Empleado.query.get_or_404(empleado_id)
        persona = Persona.query.get_or_404(empleado.id_persona)

        # Buscar la credencial PIN del empleado
        credencial = (
            Credencial.query.join(TipoCredencial)
            .filter(
                Credencial.id_persona == persona.id_persona,
                TipoCredencial.nombre == "PIN",
            )
            .first()
        )

        if not credencial:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "El empleado no tiene una credencial PIN asociada",
                    }
                ),
                404,
            )

        # Cambiar el estado de la credencial
        credencial.activo = not credencial.activo
        db.session.commit()

        nuevo_estado = "activada" if credencial.activo else "inactivada"

        return jsonify(
            {
                "success": True,
                "message": f"Credencial {nuevo_estado} exitosamente",
                "activo": credencial.activo,
            }
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Error al actualizar la credencial: {str(e)}",
                }
            ),
            500,
        )
