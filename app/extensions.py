from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Inicialización de objetos de extensión.
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Configuración de LoginManager
login_manager.login_view = 'main.login' 
login_manager.login_message_category = 'info' 
login_manager.login_message = 'Por favor, inicie sesión para acceder al mapa.'

@login_manager.user_loader
def load_user(user_id):
    from .models import Usuario
    return Usuario.query.get(int(user_id))