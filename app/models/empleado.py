from app import db
from datetime import datetime

class Empleado(db.Model):
    __tablename__ = 'empleado'

    empleado_id = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona', ondelete="CASCADE"), nullable=False)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargo_empleado.id_cargo'), nullable=False)
    fecha_contratacion = db.Column(db.Date, nullable=False)
    fecha_finalizacion = db.Column(db.Date)

    # Relaciones de las tablas
    persona = db.relationship("Persona", backref="empleado", uselist=False, passive_deletes=True)
    cargo = db.relationship("CargoEmpleado", backref="empleados")

    def __repr__(self):
        return f"<Empleado {self.empleado_id} - Persona {self.id_persona}>"