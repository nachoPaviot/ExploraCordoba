from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    #Constantes para los roles de usuario.
    ROL_ADMIN_ID = 1
    ROL_MODERADOR_ID = 2
    ROL_SOPORTE_ID = 3
    ROL_PROVEEDOR_ID = 4
    ROL_TURISTA_ID = 5
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Construcción de la URL de forma centralizada
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
class DevelopmentConfig(Config):
    DEBUG = True
class TestingConfig(Config):
    #Base de datos SQLite en memoria para tests rápidos.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False

