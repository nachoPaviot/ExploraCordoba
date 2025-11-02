from app.extensions import db

class Posteo(db.Model):
    __tablename__ = 'posteo'
    
    posteo_id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=True)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # FK al usuario que creó el posteo
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.usuario_id'), nullable=False)
    # Posteos ligados a Usuario. 
    autor = db.relationship('Usuario', backref='posteos', lazy=True)
    # Posteos ligados a un destino:
    destino_id = db.Column(db.Integer, db.ForeignKey('destino.destino_id'), nullable=True)
    # Posteos anidados para respuestas a otros posteos
    # Almacena el ID del posteo al que se está respondiendo
    posteo_padre_id = db.Column(db.Integer, db.ForeignKey('posteo.posteo_id'), nullable=True)
    # Define la relación con el comentario padre
    # remote_side=[id] es crucial para las relaciones recursivas
    posteo_padre = db.relationship(
        'Posteo', 
        remote_side=[posteo_id], 
        backref=db.backref('replies', lazy='dynamic', cascade='all, delete-orphan')
    )
    # El backref 'replies' permite hacer comentario_padre.replies para obtener todas sus respuestas.

    def __repr__(self):
        return f'<Posteo ID {self.posteo_id} por {self.usuario_id}>'