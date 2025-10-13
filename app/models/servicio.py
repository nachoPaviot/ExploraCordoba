from app.extensions import db

class Servicio(db.Model):
    __tablename__ = 'servicio'
    
    servicio_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    precio_base = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(50)) # Puede ser Persona, Días.
    status = db.Column(db.String(50), default='Disponible')
    
    # Clave Foránea a Destino
    destino_id = db.Column(db.Integer, db.ForeignKey('destino.destino_id'), nullable=False)
    
    # backref 'destino' se define en la clase Destino
    # 'Cotizacion' para evitar errores de forward-reference
    cotizaciones = db.relationship('Cotizacion', backref='servicio_cotizado', lazy=True)
    
    def __repr__(self):
        return f'<Servicio {self.nombre} en Destino ID: {self.destino_id}>'