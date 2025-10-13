from app.extensions import db

class Destino(db.Model):
    __tablename__ = 'destino'
    destino_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(50))
    endpoint = db.Column(db.String(50), nullable=True) # Para datos de geolocalización

    # Método de serialización a diccionario
    def to_dict(self):
        """Convierte el objeto Destino a un diccionario serializable para JSON."""
        return {
            'id': self.destino_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'endpoint': self.endpoint, # Para las coordenadas
            'categoria': self.categoria 
        }

    # Relación con Servicio
    servicios = db.relationship('Servicio', backref='destino', lazy=True) 

    def __repr__(self):
        return f'<Destino {self.nombre}>'
