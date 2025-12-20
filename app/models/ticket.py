from app.extensions import db
from datetime import datetime

class Ticket(db.Model):
    __tablename__ = 'ticket'
    ticket_id = db.Column(db.Integer, primary_key=True)
    asunto = db.Column(db.String(256), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(50), default='Abierto', nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Clave Foránea a Usuario que crea el ticket
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'), nullable=False) 
    # Clave Foránea a Usuario asignado al ticket
    asignado_a_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'), nullable=True)

    # Relaciones
    creador = db.relationship('Usuario', foreign_keys=[usuario_id], backref=db.backref('tickets_creados', lazy='dynamic'))
    asignado_a = db.relationship('Usuario', foreign_keys=[asignado_a_id], backref=db.backref('tickets_asignados', lazy='dynamic'))
    respuestas = db.relationship('RespuestaTicket', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Ticket {self.ticket_id}: {self.asunto} ({self.estado})>'
    
class RespuestaTicket(db.Model):
    __tablename__ = 'respuesta_ticket'
    
    respuesta_id = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    # LLAVES FORÁNEAS
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.ticket_id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'), nullable=False)
    # RELACIONES
    autor = db.relationship('Usuario', backref=db.backref('respuestas_escritas', lazy='dynamic'))
    
    def __repr__(self):
        return f'<RespuestaTicket {self.respuesta_id} a Ticket {self.ticket_id}>'