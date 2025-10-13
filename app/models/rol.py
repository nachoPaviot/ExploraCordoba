from app.extensions import db

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