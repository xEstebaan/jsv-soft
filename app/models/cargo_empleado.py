from app import db
from datetime import datetime

class CargoEmpleado(db.Model):
    __tablename__ = 'cargo_empleado'

    id_cargo = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<CargoEmpleado {self.descripcion}>"