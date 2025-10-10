from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Inicialización de objetos de extensión.
# NOTA: Los objetos se crean aquí, pero NO se asocian a la app (init_app) todavía.
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
# Configuración de LoginManager
login_manager.login_view = 'main.login' 
login_manager.login_message_category = 'info' 
login_manager.login_message = 'Por favor, inicie sesión para acceder al mapa.'