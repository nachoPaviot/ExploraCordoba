import pytest
from app import create_app
from app.extensions import db
from app.models import Rol, Usuario
from flask_login import current_user
from flask import url_for, get_flashed_messages

# ----------------------------------------------------
# FUNCIONES DE UTILIDAD PARA PRUEBAS (NUEVO)
# ----------------------------------------------------

def login_test_user(client, user):
    """
    Simula el inicio de sesión de un usuario de prueba de Flask-Login
    estableciendo directamente la clave '_user_id' en la sesión.
    """
    with client.session_transaction() as sess:
        # CRUCIAL: Flask-Login usa la clave '_user_id' y espera un string.
        sess['_user_id'] = str(user.usuario_id) 
        
def logout_test_user(client):
    """Simula el cierre de sesión."""
    with client.session_transaction() as sess:
        if '_user_id' in sess:
            del sess['_user_id']

# ----------------------------------------------------
# FIXTURES DE LA APLICACIÓN
# ----------------------------------------------------

@pytest.fixture(scope='session')
def app():
    """Crea y configura una instancia de la aplicación Flask para la sesión de testing."""
    app = create_app('testing') 
    
    with app.app_context():
        # Crea todas las tablas en la base de datos en memoria
        db.drop_all()
        db.create_all()
        
        # Inserta datos de prueba (SEEDING)
        # Nota: Usando 'usuario_id' para la clave primaria.
        rol_turista = Rol(rol_id=5, nombre='Turista', descripcion='Usuario estándar')
        rol_admin = Rol(rol_id=1, nombre='Administrador', descripcion='Acceso total')
        
        # Simulación de usuarios con la clave primaria 'usuario_id'
        user_turista = Usuario(
            usuario_id=1000, nombre='Test', apellido='Turista', 
            email='turista@test.com', dni='11111111', status='Activo', 
            rol_id=5, contrasena='hashed_turista_password' 
        )
        user_admin = Usuario(
            usuario_id=1100, nombre='Admin', apellido='User', 
            email='admin@test.com', dni='99999999', status='Activo', 
            rol_id=1, contrasena='hashed_admin_password' 
        )

        db.session.add_all([rol_turista, rol_admin, user_turista, user_admin])
        db.session.commit()

        yield app

        # Limpieza: Cierra la sesión y elimina todas las tablas
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Crea un cliente de testing para simular peticiones."""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Proporciona la sesión de base de datos para los tests."""
    with app.app_context():
        # Inicia una transacción para que el test pueda hacer cambios
        # y luego hacer rollback para limpiar al final.
        connection = db.engine.connect()
        transaction = connection.begin()
        db.session.begin_nested() # Inicia punto de guardado (savepoint)
        
        yield db.session
        
        # Limpieza
        db.session.remove()
        transaction.rollback() # Deshace todos los cambios realizados por el test
        connection.close()

# ----------------------------------------------------
# FIXTURES DE USUARIOS DE PRUEBA
# ----------------------------------------------------

@pytest.fixture
def turista_user(app):
    """Retorna el usuario Turista de prueba."""
    # Necesitas el contexto de la aplicación para que la consulta funcione
    with app.app_context():
        return Usuario.query.filter_by(email='turista@test.com').first()

@pytest.fixture
def admin_user(app):
    """Retorna el usuario Administrador de prueba."""
    with app.app_context():
        return Usuario.query.filter_by(email='admin@test.com').first()