from app import db
from app.models.tipo_registro import TipoRegistro
from app.models.roles import Rol
from app.models.tipo_credencial import TipoCredencial
from app.models.usuarios import Usuario
from app.models.persona import Persona
from app.models.credencial import Credencial
from app.models.cargo_empleado import CargoEmpleado
from app.models.empleado import Empleado
from werkzeug.security import generate_password_hash
from flask import current_app
from datetime import datetime


def inicializar_datos_referencia():
    """
    Inicializa todos los datos de referencia necesarios para el funcionamiento de la aplicación
    """
    try:
        # Inicializar tipos de registro
        inicializar_tipos_registro()

        # Inicializar roles
        inicializar_roles()

        # Inicializar tipos de credencial
        inicializar_tipos_credencial()

        # Inicializar cargos de empleado
        inicializar_cargos_empleado()

        # Inicializar usuario administrador por defecto
        inicializar_admin_por_defecto()

        db.session.commit()
        current_app.logger.info("Datos de referencia inicializados correctamente")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al inicializar datos de referencia: {str(e)}")
        raise e


def inicializar_tipos_registro():
    """
    Inicializa los tipos de registro si no existen
    """
    # Verificar si ya existen los tipos de registro
    ingreso = TipoRegistro.query.filter_by(id_tipo_registro=1).first()
    salida = TipoRegistro.query.filter_by(id_tipo_registro=2).first()

    if not ingreso:
        ingreso = TipoRegistro(id_tipo_registro=1, descripcion="Ingreso")
        db.session.add(ingreso)
        current_app.logger.info("Tipo de registro 'Ingreso' creado")

    if not salida:
        salida = TipoRegistro(id_tipo_registro=2, descripcion="Salida")
        db.session.add(salida)
        current_app.logger.info("Tipo de registro 'Salida' creado")


def inicializar_roles():
    """
    Inicializa los roles si no existen
    """
    # Verificar si ya existen los roles
    admin = Rol.query.filter_by(id_rol=1).first()
    empleado = Rol.query.filter_by(id_rol=2).first()
    visitante = Rol.query.filter_by(id_rol=3).first()

    if not admin:
        admin = Rol(id_rol=1, nombre_rol="Administrador")
        db.session.add(admin)
        current_app.logger.info("Rol 'Administrador' creado")

    if not empleado:
        empleado = Rol(id_rol=2, nombre_rol="Empleado")
        db.session.add(empleado)
        current_app.logger.info("Rol 'Empleado' creado")

    if not visitante:
        visitante = Rol(id_rol=3, nombre_rol="Visitante")
        db.session.add(visitante)
        current_app.logger.info("Rol 'Visitante' creado")


def inicializar_tipos_credencial():
    """
    Inicializa los tipos de credencial si no existen
    """
    # Verificar si ya existe el tipo de credencial PIN
    pin = TipoCredencial.query.filter_by(id_tipo_credencial=1).first()

    if not pin:
        pin = TipoCredencial(id_tipo_credencial=1, nombre="PIN")
        db.session.add(pin)
        current_app.logger.info("Tipo de credencial 'PIN' creado")


def inicializar_cargos_empleado():
    """
    Inicializa los cargos de empleado básicos si no existen
    """
    cargos_basicos = [
        "Administrador",
        "Operario",
        "Recursos Humanos",
        "Director Administrativo",
        "Director de Operaciones",
    ]

    for cargo_desc in cargos_basicos:
        cargo_existente = CargoEmpleado.query.filter_by(descripcion=cargo_desc).first()
        if not cargo_existente:
            cargo = CargoEmpleado(descripcion=cargo_desc)
            db.session.add(cargo)
            current_app.logger.info(f"Cargo '{cargo_desc}' creado")


def inicializar_admin_por_defecto():
    """
    Crea un usuario administrador por defecto si no existe ningún administrador
    """
    # Verificar si ya existe algún administrador
    admin_existente = Usuario.query.filter_by(id_rol=1).first()

    if not admin_existente:
        try:
            # Crear persona administradora
            persona_admin = Persona(
                primer_nombre="Admin",
                segundo_nombre="Sistema",
                primer_apellido="Administrador",
                segundo_apellido="Principal",
                documento="00000000",
                correo="admin@sistema.com",
                celular="0000000000",
            )
            db.session.add(persona_admin)
            db.session.flush()  # Para obtener el ID

            # Crear usuario administrador
            usuario_admin = Usuario(
                id_persona=persona_admin.id_persona,
                id_rol=1,  # Administrador
                contrasena=generate_password_hash("admin123"),
            )
            db.session.add(usuario_admin)

            # Crear credencial PIN
            tipo_pin = TipoCredencial.query.filter_by(nombre="PIN").first()
            if tipo_pin:
                credencial_pin = Credencial(
                    id_persona=persona_admin.id_persona,
                    id_tipo_credencial=tipo_pin.id_tipo_credencial,
                    valor="ADM0000",
                    activo=True,
                )
                db.session.add(credencial_pin)

            # Crear empleado administrador
            cargo_admin = CargoEmpleado.query.filter_by(
                descripcion="Administrador"
            ).first()
            if cargo_admin:
                empleado_admin = Empleado(
                    id_persona=persona_admin.id_persona,
                    cargo_id=cargo_admin.id_cargo,
                    fecha_contratacion=datetime.now().date(),
                )
                db.session.add(empleado_admin)

            current_app.logger.info("Usuario administrador por defecto creado")
            print("✅ Usuario administrador por defecto creado:")
            print("   📧 Correo: admin@sistema.com")
            print("   🔑 Contraseña: admin123")
            print("   🔢 PIN: ADM0000")
            print("   👤 Documento: 00000000")

        except Exception as e:
            current_app.logger.error(
                f"Error al crear usuario administrador por defecto: {str(e)}"
            )
            raise e
    else:
        current_app.logger.info(
            "Ya existe un usuario administrador, no se crea uno nuevo"
        )
