from app.extensions import db

class Cotizacion(db.Model):
    __tablename__ = 'cotizacion'
    cotizacion_id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.servicio_id'), nullable=False)
    
    
    fecha_solicitud = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_inicio_viaje = db.Column(db.Date, nullable=False)
    fecha_fin_viaje = db.Column(db.Date, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False)
    
    precio_total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente')

    def __repr__(self):
        return f'<Cotizacion ID {self.cotizacion_id}>'