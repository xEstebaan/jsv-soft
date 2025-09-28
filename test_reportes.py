#!/usr/bin/env python3
"""
Script de prueba para generar datos de ejemplo para la funcionalidad de reportes
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.empleado import Empleado
from app.models.persona import Persona
from app.models.registro import Registro
from app.models.tipo_registro import TipoRegistro
from app.models.credencial import Credencial
from app.models.tipo_credencial import TipoCredencial


def generar_datos_prueba():
    """Genera datos de prueba para la funcionalidad de reportes"""
    app = create_app()

    with app.app_context():
        try:
            # Verificar si ya existen datos
            if Registro.query.count() > 0:
                print(
                    "Ya existen registros en la base de datos. Saltando generación de datos de prueba."
                )
                return

            # Obtener empleados existentes
            empleados = Empleado.query.join(Persona).all()
            if not empleados:
                print(
                    "No hay empleados en la base de datos. Creando empleados de prueba..."
                )
                crear_empleados_prueba()
                empleados = Empleado.query.join(Persona).all()

            # Obtener tipos de registro
            tipo_ingreso = TipoRegistro.query.filter_by(descripcion="Ingreso").first()
            tipo_salida = TipoRegistro.query.filter_by(descripcion="Salida").first()

            if not tipo_ingreso or not tipo_salida:
                print("Error: No se encontraron los tipos de registro necesarios.")
                return

            # Generar registros para los últimos 30 días
            fecha_inicio = datetime.now() - timedelta(days=30)

            for empleado in empleados:
                # Obtener credencial del empleado
                credencial = Credencial.query.filter_by(
                    id_persona=empleado.id_persona, activo=True
                ).first()

                if not credencial:
                    continue

                # Generar registros para cada día de la semana (lunes a viernes)
                for i in range(30):
                    fecha = fecha_inicio + timedelta(days=i)

                    # Solo generar registros para días laborables (lunes a viernes)
                    if fecha.weekday() < 5:  # 0-4 = lunes a viernes
                        # Hora de entrada aleatoria entre 7:00 y 9:00
                        hora_entrada = 7 + random.randint(0, 120) // 60
                        minuto_entrada = random.randint(0, 59)

                        # Hora de salida aleatoria entre 16:00 y 19:00
                        hora_salida = 16 + random.randint(0, 180) // 60
                        minuto_salida = random.randint(0, 59)

                        # Crear registro de entrada
                        entrada = Registro(
                            id_persona=empleado.id_persona,
                            id_credencial=credencial.id_credencial,
                            id_tipo_registro=tipo_ingreso.id_tipo_registro,
                            fecha_hora=datetime.combine(
                                fecha,
                                datetime.min.time().replace(
                                    hour=hora_entrada, minute=minuto_entrada
                                ),
                            ),
                            observacion="Registro de prueba - Entrada",
                        )

                        # Crear registro de salida
                        salida = Registro(
                            id_persona=empleado.id_persona,
                            id_credencial=credencial.id_credencial,
                            id_tipo_registro=tipo_salida.id_tipo_registro,
                            fecha_hora=datetime.combine(
                                fecha,
                                datetime.min.time().replace(
                                    hour=hora_salida, minute=minuto_salida
                                ),
                            ),
                            observacion="Registro de prueba - Salida",
                        )

                        db.session.add(entrada)
                        db.session.add(salida)

            db.session.commit()
            print("✅ Datos de prueba generados correctamente")
            print(f"   - Empleados: {len(empleados)}")
            print(f"   - Registros generados para los últimos 30 días")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al generar datos de prueba: {str(e)}")
            raise e


def crear_empleados_prueba():
    """Crea empleados de prueba si no existen"""
    from app.models.cargo_empleado import CargoEmpleado
    from app.models.usuarios import Usuario
    from werkzeug.security import generate_password_hash

    # Obtener o crear cargo de prueba
    cargo = CargoEmpleado.query.filter_by(descripcion="Operario").first()
    if not cargo:
        cargo = CargoEmpleado(descripcion="Operario")
        db.session.add(cargo)
        db.session.flush()

    # Obtener tipo de credencial PIN
    tipo_pin = TipoCredencial.query.filter_by(nombre="PIN").first()
    if not tipo_pin:
        tipo_pin = TipoCredencial(nombre="PIN")
        db.session.add(tipo_pin)
        db.session.flush()

    # Crear empleados de prueba
    empleados_prueba = [
        {
            "primer_nombre": "Carlos",
            "segundo_nombre": "Alberto",
            "primer_apellido": "Mendoza",
            "segundo_apellido": "López",
            "documento": "12345678",
            "correo": "carlos.mendoza@empresa.com",
            "celular": "3001234567",
        },
        {
            "primer_nombre": "Elena",
            "segundo_nombre": "María",
            "primer_apellido": "Ramirez",
            "segundo_apellido": "García",
            "documento": "87654321",
            "correo": "elena.ramirez@empresa.com",
            "celular": "3007654321",
        },
        {
            "primer_nombre": "Diego",
            "segundo_nombre": "Fernando",
            "primer_apellido": "Herrera",
            "segundo_apellido": "Martínez",
            "documento": "11223344",
            "correo": "diego.herrera@empresa.com",
            "celular": "3001122334",
        },
        {
            "primer_nombre": "Sofia",
            "segundo_nombre": "Alejandra",
            "primer_apellido": "Vargas",
            "segundo_apellido": "Rodríguez",
            "documento": "44332211",
            "correo": "sofia.vargas@empresa.com",
            "celular": "3004433221",
        },
        {
            "primer_nombre": "Lucia",
            "segundo_nombre": "Isabel",
            "primer_apellido": "Fernandez",
            "segundo_apellido": "González",
            "documento": "55667788",
            "correo": "lucia.fernandez@empresa.com",
            "celular": "3005566778",
        },
    ]

    for emp_data in empleados_prueba:
        # Crear persona
        persona = Persona(
            primer_nombre=emp_data["primer_nombre"],
            segundo_nombre=emp_data["segundo_nombre"],
            primer_apellido=emp_data["primer_apellido"],
            segundo_apellido=emp_data["segundo_apellido"],
            documento=emp_data["documento"],
            correo=emp_data["correo"],
            celular=emp_data["celular"],
        )
        db.session.add(persona)
        db.session.flush()

        # Crear empleado
        empleado = Empleado(
            id_persona=persona.id_persona,
            cargo_id=cargo.id_cargo,
            fecha_contratacion=datetime.now().date(),
        )
        db.session.add(empleado)

        # Crear usuario
        usuario = Usuario(
            id_persona=persona.id_persona,
            id_rol=2,  # Empleado
            contrasena=generate_password_hash("123456"),
        )
        db.session.add(usuario)

        # Crear credencial PIN
        pin = f"{emp_data['primer_nombre'][:3].upper()}{random.randint(1000, 9999)}"
        credencial = Credencial(
            id_persona=persona.id_persona,
            id_tipo_credencial=tipo_pin.id_tipo_credencial,
            valor=pin,
            activo=True,
        )
        db.session.add(credencial)

        print(
            f"   - Empleado creado: {emp_data['primer_nombre']} {emp_data['primer_apellido']} (PIN: {pin})"
        )

    db.session.commit()


if __name__ == "__main__":
    generar_datos_prueba()
