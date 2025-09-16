from app import db
from datetime import datetime

class TipoCredencial(db.Model):
    __tablename__ = 'tipo_credencial'

    id_tipo_credencial = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<TipoCredencial {self.nombre}>"