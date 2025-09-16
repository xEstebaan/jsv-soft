from app import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona', ondelete="CASCADE"), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)

    # Relaciones de las tablas
    persona = db.relationship("Persona", backref="usuario", uselist=False, passive_deletes=True)
    rol = db.relationship("Rol", backref="usuarios")

    def __repr__(self):
        return f"<Usuario {self.id_usuario} - Persona {self.id_persona}>"