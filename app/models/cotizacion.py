from app.extensions import db

class Cotizacion(db.Model):
    __tablename__ = 'cotizacion'
    cotizacion_id = db.Column(db.Integer, primary_key=True)
    fecha_solicitud = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    cantidad_personas = db.Column(db.Integer, nullable=False)
    precio_total = db.Column(db.Float, nullable=False)
    # Foreign Keys
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.servicio_id'), nullable=False)

    # Relación con Reserva (uno a uno)
    reserva = db.relationship('Reserva', backref='cotizacion', uselist=False, lazy=True)


    def __repr__(self):
        return f'<Cotizacion ID {self.cotizacion_id}>'