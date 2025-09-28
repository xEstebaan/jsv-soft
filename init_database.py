#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de referencia necesarios
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.utils.init_db import inicializar_datos_referencia


def main():
    """Función principal para inicializar la base de datos"""
    app = create_app()

    with app.app_context():
        try:
            print("Inicializando datos de referencia...")
            inicializar_datos_referencia()
            print("✅ Datos de referencia inicializados correctamente")
            print("\nDatos creados:")
            print("- Tipos de registro: Ingreso (ID: 1), Salida (ID: 2)")
            print("- Roles: Administrador (ID: 1), Empleado (ID: 2), Visitante (ID: 3)")
            print("- Tipos de credencial: PIN (ID: 1)")
            print(
                "- Cargos de empleado: Administrador, Operario, Recursos Humanos, etc."
            )
            print("- Usuario administrador por defecto (si no existía)")

        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
