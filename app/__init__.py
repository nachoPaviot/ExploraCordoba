from flask import Flask
from config import DevelopmentConfig, TestingConfig, Config
from .utils import register_cli_commands
from .extensions import db, bcrypt, login_manager, migrate
from .routes import main as main_blueprint

# crea la Aplicación
def create_app(config_name='development'):
    app = Flask(__name__)
    
    if config_name == 'testing':
        # Carga la configuración especial para pruebas (SQLite en memoria)
        app.config.from_object(TestingConfig) 
    elif config_name == 'production':
        app.config.from_object(Config)
    else: # 'development' o cualquier otro valor
        app.config.from_object(DevelopmentConfig)

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
    migrate.init_app(app, db)

    app.register_blueprint(main_blueprint)
    
    # Comandos CLI
    register_cli_commands(app)
        
    return app