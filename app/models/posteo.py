from app.extensions import db

class Posteo(db.Model):
    __tablename__ = 'posteo'
    
    posteo_id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=True) # Opcional si solo son comentarios
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # FK al usuario que creó el posteo
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'), nullable=False)
    
    # Posteos ligados a Usuario. 
    autor = db.relationship('Usuario', backref='posteos', lazy=True)
    # Posteos ligados a un destino:
    destino_id = db.Column(db.Integer, db.ForeignKey('destino.destino_id'), nullable=True)
    
    def __repr__(self):
        return f'<Posteo ID {self.posteo_id} por {self.usuario_id}>'