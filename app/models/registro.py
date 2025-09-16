from app import db
from datetime import datetime

class Registro(db.Model):
    __tablename__ = 'registro'

    registro_id = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona', ondelete="CASCADE"), nullable=False)
    id_credencial = db.Column(db.Integer, db.ForeignKey('credencial.id_credencial', ondelete="SET NULL"), nullable=False)
    id_tipo_registro = db.Column(db.Integer, db.ForeignKey('tipo_registro.id_tipo_registro'), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    observacion = db.Column(db.String(200))

    # Relaciones de las tablas
    persona = db.relationship("Persona", backref="registros", passive_deletes=True)
    credencial = db.relationship("Credencial", backref="registros", passive_deletes=True)
    tipo_registro = db.relationship("TipoRegistro", backref="registros")

    def __repr__(self):
        return f"<Registro {self.registro_id} - Persona {self.id_persona}>"