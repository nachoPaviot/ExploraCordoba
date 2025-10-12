from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from .extensions import db, login_manager

# Modelo: Rol
class Rol(db.Model):
    # tabla 'rol' en la base de datos
    __tablename__ = 'rol' 
    rol_id = db.Column(db.Integer, primary_key=True)
    n_rol = db.Column(db.String(80), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    
    # Relación con Usuario
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def __repr__(self):
        return f'<Rol {self.n_rol}>'

# Modelo: Usuario
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

    # Requerido por Flask-Login para el ID
    def get_id(self):
        return str(self.usuario_id)

    def __repr__(self):
        return f'<Usuario {self.email}>'

# Modelo: Destino
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
    
# Modelo Servicio
class Servicio(db.Model):
    """Modelo para los servicios turísticos ofrecidos."""
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
    
# Modelo: Cotizacion
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
    
# Modelo: Posteo
class Posteo(db.Model):
    """Modelo para los comentarios del foro o posts."""
    __tablename__ = 'posteo'
    
    posteo_id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=True) # Opcional si solo son comentarios
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # FK al usuario que creó el posteo
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'), nullable=False)
    
    # Posteos ligados a Usuario. 
    # Asegúrate de que esta relación no interfiera con las existentes en Usuario.
    autor = db.relationship('Usuario', backref='posteos', lazy=True)
    # Posteos ligados a un destino:
    destino_id = db.Column(db.Integer, db.ForeignKey('destino.destino_id'), nullable=True)
    
    def __repr__(self):
        return f'<Posteo ID {self.posteo_id} por {self.usuario_id}>'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))