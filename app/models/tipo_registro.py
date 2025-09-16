from app import db
from datetime import datetime

class TipoRegistro(db.Model):
    __tablename__ = 'tipo_registro'

    id_tipo_registro = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<TipoRegistro {self.descripcion}>"