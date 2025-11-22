#Constantes para los roles de usuario.
ROL_ADMIN_ID = 1
ROL_MODERADOR_ID = 2
ROL_SOPORTE_ID = 3
ROL_PROVEEDOR_ID = 4
ROL_TURISTA_ID = 5

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@host/dev_db'

class TestingConfig(Config):
    #Base de datos SQLite en memoria para tests rápidos.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False

