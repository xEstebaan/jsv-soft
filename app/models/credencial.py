from app import db
from datetime import datetime

class Credencial(db.Model):
    __tablename__ = 'credencial'

    id_credencial = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona', ondelete="CASCADE"), nullable=False)
    id_tipo_credencial = db.Column(db.Integer, db.ForeignKey('tipo_credencial.id_tipo_credencial'), nullable=False)
    valor = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Restricción de credencial única
    __table_args__ = (
        db.UniqueConstraint('id_tipo_credencial', 'valor', name='uk_credencial_tipo_valor'),
    )

    # Relaciones de las tablas
    persona = db.relationship("Persona", backref="credenciales", passive_deletes=True)
    tipo_credencial = db.relationship("TipoCredencial", backref="credenciales")

    def __repr__(self):
        return f"<Credencial {self.valor} (Tipo {self.id_tipo_credencial})>"