from app.extensions import db

class Reserva(db.Model):
    __tablename__ = 'reserva'
    reserva_id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.servicio_id'), nullable=False)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizacion.cotizacion_id'), unique=True, nullable=False)
    
    # Datos de la reserva
    fecha_reserva = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_servicio_inicio = db.Column(db.Date, nullable=False)
    fecha_servicio_fin = db.Column(db.Date, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False)
    costo_total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente')

    def __repr__(self):
        return f'<Reserva ID {self.reserva_id} para Cotización ID {self.cotizacion_id}>'