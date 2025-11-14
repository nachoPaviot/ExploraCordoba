from flask_login import UserMixin
from app.extensions import db

class Usuario(db.Model, UserMixin): 
    __tablename__ = 'usuario'
    usuario_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    dni = db.Column(db.String(20), unique=True)
    contrasena = db.Column(db.String(255), nullable=False) # el hash de Bcrypt
    status = db.Column(db.String(50), default='Activo')
    
    # FK
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.rol_id'), nullable=False)
     
    # Relaciones
    cotizaciones = db.relationship('Cotizacion', backref='solicitante', lazy=True)
    reservas = db.relationship('Reserva', backref='turista', lazy=True) 

    # Requerido por Flask-Login para el ID
    def get_id(self):
        return str(self.usuario_id)

    def __repr__(self):
        return f'<Usuario {self.email}>'
