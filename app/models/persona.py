from app import db
from datetime import datetime

class Persona(db.Model):
    __tablename__ = "persona"

    id_persona = db.Column(db.Integer, primary_key=True, autoincrement=True)
    primer_nombre = db.Column(db.String(50), nullable=False)
    segundo_nombre = db.Column(db.String(50))
    primer_apellido = db.Column(db.String(255), nullable=False)
    segundo_apellido = db.Column(db.String(255))
    documento = db.Column(db.String(30), nullable=False, unique=True)
    correo = db.Column(db.String(255), nullable=False, unique=True)
    celular = db.Column(db.String(50))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Persona {self.primer_nombre} {self.primer_apellido}>"