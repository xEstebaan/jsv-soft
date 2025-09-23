from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models.empleado import Empleado
from app.models.persona import Persona
from app.models.cargo_empleado import CargoEmpleado
from app.models.credencial import Credencial
from app.models.tipo_credencial import TipoCredencial
from app.models.usuarios import Usuario
from werkzeug.security import generate_password_hash
from datetime import datetime
import random
import string
from flask_login import login_required, current_user
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Verificar si el usuario es administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Validar el rol del usuario admin
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/empleados', methods=['GET'])
def lista_empleados():
    """Lista de empleados con opciones de filtrado"""
    empleados = (Empleado.query
                 .join(Persona, Empleado.id_persona == Persona.id_persona)
                 .join(CargoEmpleado, Empleado.cargo_id == CargoEmpleado.id_cargo)
                 .add_columns(
                     Persona.primer_nombre,
                     Persona.segundo_nombre,
                     Persona.primer_apellido,
                     Persona.segundo_apellido,
                     Persona.documento,
                     Persona.fecha_creacion,
                     CargoEmpleado.descripcion.label('cargo'),
                     Empleado.empleado_id,
                     Empleado.fecha_contratacion
                 )
                 .all())
    
    return render_template('admin/vista_empleados.html', empleados=empleados)

@admin_bp.route('/empleados/crear', methods=['GET', 'POST'])
def crear_empleado():
    # Cargar los cargos disponibles
    cargos = CargoEmpleado.query.all()
    
    if request.method == 'POST':
        try:
            # Datos de la persona
            primer_nombre = request.form.get('primer_nombre')
            segundo_nombre = request.form.get('segundo_nombre', '')
            primer_apellido = request.form.get('primer_apellido')
            segundo_apellido = request.form.get('segundo_apellido', '')
            documento = request.form.get('documento')
            correo = request.form.get('correo')
            celular = request.form.get('celular', '')
            
            # Datos de acceso
            contrasena = request.form.get('contrasena')
            confirmar_contrasena = request.form.get('confirmar_contrasena')
            
            # Datos del empleado
            cargo_id = request.form.get('cargo_id', type=int)
            fecha_contratacion = request.form.get('fecha_contratacion')
            
            # Validaciones básicas
            if not primer_nombre or not primer_apellido or not documento or not correo or not cargo_id or not fecha_contratacion or not contrasena or not confirmar_contrasena:
                flash('Todos los campos marcados con * son obligatorios', 'error')
                return render_template('admin/crear_empleado.html', cargos=cargos)
                
            # Validar formato de correo electrónico
            import re
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(correo):
                flash('El formato del correo electrónico no es válido', 'error')
                return render_template('admin/crear_empleado.html', cargos=cargos)
            
            # Validar que las contraseñas coincidan
            if contrasena != confirmar_contrasena:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('admin/crear_empleado.html', cargos=cargos)
                
            # Validar longitud mínima de contraseña
            if len(contrasena) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'error')
                return render_template('admin/crear_empleado.html', cargos=cargos)
            
            # Verificar si la persona ya existe (por documento o correo)
            persona_existente = Persona.query.filter(
                (Persona.documento == documento) | (Persona.correo == correo)
            ).first()
            
            if persona_existente:
                flash('Ya existe una persona con ese documento o correo', 'error')
                return render_template('admin/crear_empleado.html', cargos=cargos)
            
            # Crear persona
            persona = Persona(
                primer_nombre=primer_nombre,
                segundo_nombre=segundo_nombre if segundo_nombre else None,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido if segundo_apellido else None,
                documento=documento,
                correo=correo,
                celular=celular if celular else None
            )
            
            db.session.add(persona)
            db.session.flush()  # Para obtener el ID de la persona
            
            # Crear empleado
            fecha_contratacion_obj = datetime.strptime(fecha_contratacion, '%Y-%m-%d').date()
            empleado = Empleado(
                id_persona=persona.id_persona,
                cargo_id=cargo_id,
                fecha_contratacion=fecha_contratacion_obj
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
                activo=True
            )
            
            db.session.add(credencial)
            
            # Crear un usuario para el empleado (para poder iniciar sesión)
            usuario = Usuario(
                id_persona=persona.id_persona,
                # ID 2 para rol de empleado (según inicializar_roles en init_db.py)
                id_rol=2,  
                contrasena=generate_password_hash(contrasena)
            )
            
            db.session.add(usuario)
            db.session.commit()
            
            flash(f'Empleado creado con éxito. PIN generado: {pin}', 'success')
            flash(f'Se ha creado un usuario con el correo: {correo} y la contraseña que has establecido.', 'info')
            return redirect(url_for('admin.lista_empleados'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el empleado: {str(e)}', 'error')
            
    return render_template('admin/crear_empleado.html', cargos=cargos)

def generate_pin(primer_nombre):
    """Genera un PIN"""
    nombre_seguro = primer_nombre.strip().upper()
    while len(nombre_seguro) < 3:
        nombre_seguro += 'X'
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