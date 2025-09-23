from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from datetime import datetime
from app import db
from app.models.credencial import Credencial
from app.models.registro import Registro
from app.models.tipo_registro import TipoRegistro
from app.models.persona import Persona

registro_bp = Blueprint('registro', __name__, url_prefix='/registro')

@registro_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Maneja la página principal de registro de ingreso/salida
    """
    if request.method == 'POST':
        pin = request.form.get('pin')
        accion = request.form.get('accion')
        
        if not pin:
            flash('Por favor ingrese un PIN válido', 'error')
            return redirect(url_for('registro.index'))
        
        # Buscar la credencial asociada con el PIN
        credencial = Credencial.query.filter_by(
            valor=pin, 
            activo=True, 
            id_tipo_credencial=2 # Asumiendo que 2 es el ID para tipo 'PIN'
        ).first()
        
        if not credencial:
            flash('Credencial no reconocida o inactiva', 'error')
            return redirect(url_for('registro.index'))
        
        # Obtener la persona asociada con la credencial
        persona = Persona.query.get(credencial.id_persona)
        
        if not persona:
            flash('No se encontró información de la persona asociada a esta credencial', 'error')
            return redirect(url_for('registro.index'))
        
        # Determinar el tipo de registro (ingreso o salida)
        tipo_registro_id = 1 if accion == 'ingreso' else 2
        
        # Si es un ingreso, verificar si ya existe un ingreso sin salida
        if accion == 'ingreso':
            # Buscar el último ingreso de la persona
            ultimo_ingreso = Registro.query.filter_by(
                id_persona=persona.id_persona,
                id_tipo_registro=1  # Tipo ingreso
            ).order_by(Registro.fecha_hora.desc()).first()
            
            if ultimo_ingreso:
                # Buscar si hay una salida después de ese ingreso
                salida_posterior = Registro.query.filter(
                    Registro.id_persona == persona.id_persona,
                    Registro.id_tipo_registro == 2,
                    Registro.fecha_hora > ultimo_ingreso.fecha_hora
                ).first()
                
                # Si no hay salida posterior al último ingreso, no permitir un nuevo ingreso
                if not salida_posterior:
                    flash(f'Ya tiene un registro de ingreso activo desde {ultimo_ingreso.fecha_hora.strftime("%d-%m-%Y %H:%M:%S")}. '
                          f'Debe registrar una salida antes de poder registrar un nuevo ingreso.', 'warning')
                    return redirect(url_for('registro.index'))
        
        # Verificar si ya hay un registro de ingreso sin salida correspondiente
        if accion == 'salida':
            ultimo_registro = Registro.query.filter_by(
                id_persona=persona.id_persona,
                id_tipo_registro=1
            ).order_by(Registro.fecha_hora.desc()).first()
            
            if not ultimo_registro:
                flash('No se encontró un registro de ingreso para esta persona', 'warning')
                return redirect(url_for('registro.index'))
            
            # Verificamos si ya tiene un registro de salida después del último ingreso
            ultimo_salida = Registro.query.filter_by(
                id_persona=persona.id_persona,
                id_tipo_registro=2
            ).order_by(Registro.fecha_hora.desc()).first()
            
            if ultimo_salida and ultimo_salida.fecha_hora > ultimo_registro.fecha_hora:
                flash('Ya tiene un registro de salida después de su último ingreso', 'warning')
                return redirect(url_for('registro.index'))
        
        # Crear el nuevo registro
        nuevo_registro = Registro(
            id_persona=persona.id_persona,
            id_credencial=credencial.id_credencial,
            id_tipo_registro=tipo_registro_id,
            fecha_hora=datetime.now(),
            observacion=f"Registro de {'ingreso' if accion == 'ingreso' else 'salida'} automático"
        )
        
        try:
            db.session.add(nuevo_registro)
            db.session.commit()
            
            mensaje = f"Registro de {'ingreso' if accion == 'ingreso' else 'salida'} exitoso para {persona.primer_nombre} {persona.primer_apellido}"
            flash(mensaje, 'success')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al guardar registro: {str(e)}")
            flash('Error al procesar el registro. Por favor, inténtelo nuevamente.', 'error')
            
        return redirect(url_for('registro.index'))
    
    fecha_actual = datetime.now().strftime('%d-%B-%Y')
    # Meses al español
    meses_es = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre', 
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    
    for mes_en, mes_es in meses_es.items():
        fecha_actual = fecha_actual.replace(mes_en, mes_es)

    for mes_en, mes_es in meses_es.items():
        fecha_actual = fecha_actual.replace(mes_en, mes_es)
    
    return render_template('registro/registro.html', fecha_actual=fecha_actual)
