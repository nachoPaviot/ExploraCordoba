import os
from flask import Flask
from config import DevelopmentConfig, TestingConfig, Config
from .utils import register_cli_commands
from .extensions import db, bcrypt, login_manager, migrate
from .routes import main as main_blueprint

# crea la Aplicación
def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': Config
    }

    # Cargar la configuración según el entorno
    app.config.from_object(configs.get(config_name, DevelopmentConfig))
    
    # Inicialización de extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Registro de blueprints
    app.register_blueprint(main_blueprint)
    
    # Comandos CLI
    register_cli_commands(app)
        
    return app