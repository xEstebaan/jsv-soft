from app import db
from datetime import datetime

class Rol(db.Model):
    __tablename__ = 'roles'

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Rol {self.nombre_rol}>"