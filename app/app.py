from flask import Flask
from .utils import register_cli_commands
from .extensions import db, bcrypt, login_manager
from .routes import main as main_blueprint

# Se crea la Aplicación
def create_app():
    app = Flask(__name__)
    
    DB_USER = 'postgres'
    DB_PASSWORD = '1234'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'exploraCordoba'

    # Construcción de la URI
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Configuración de la DB
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SECRET_KEY'] = 'PP3_2025'
    
    # Inicialización de extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main_blueprint)
    
    # Comandos CLI
    register_cli_commands(app)
        
    return app