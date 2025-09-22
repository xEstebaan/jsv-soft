from app import db
from app.models.tipo_registro import TipoRegistro
from app.models.roles import Rol
from app.models.tipo_credencial import TipoCredencial
from flask import current_app


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
