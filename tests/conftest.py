import pytest
from app import create_app
from app.extensions import db
from app.models import Usuario, Destino, Servicio
from datetime import datetime
from flask_login import FlaskLoginClient

# ----------------------------------------------
# Fixtures de Aplicación y DB
# ----------------------------------------------

@pytest.fixture(scope='session')
def app():
    """Crea una instancia de la aplicación Flask para las pruebas."""
    app = create_app('testing')
    
    # Usar FlaskLoginClient para manejar sesiones de login en tests
    app.test_client_class = FlaskLoginClient

    with app.app_context():
        # Crear todas las tablas en la base de datos in-memory
        db.create_all()
        
        # --- SEEDING (Datos Iniciales) ---
        
        # 1. Crear Usuarios de Prueba
        admin_user = Usuario(nombre='Admin', apellido='User', email='admin@test.com', 
                             rol='Administrador', username='admin')
        admin_user.set_password('adminpass')
        
        turista_user = Usuario(nombre='Turista', apellido='User', email='turista@test.com', 
                               rol='Turista', username='turista')
        turista_user.set_password('turistapass')
        
        # 2. Crear Destinos y Servicios de Prueba para Cotizador
        destino_cordoba = Destino(nombre='Ciudad de Córdoba', descripcion='Capital vibrante')
        
        servicio_alojamiento = Servicio(
            nombre='Hotel Centro', 
            descripcion='Alojamiento 3 noches', 
            precio_base=100.00, 
            unidad='Noche', 
            destino=destino_cordoba,
            fecha_creacion=datetime.now()
        )
        
        servicio_tour = Servicio(
            nombre='Walking Tour', 
            descripcion='Recorrido guiado por el centro', 
            precio_base=50.00, 
            unidad='Persona', 
            destino=destino_cordoba,
            fecha_creacion=datetime.now()
        )
        
        # 3. Añadir y hacer commit de todos los datos
        db.session.add_all([admin_user, turista_user, destino_cordoba, servicio_alojamiento, servicio_tour])
        db.session.commit()
        
        # Los IDs de los servicios se generan después del commit
        # Los almacenamos para que otros fixtures puedan referenciarlos
        
        yield app

        # Limpiar después de las pruebas
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(app):
    """Proporciona una sesión de DB para transacciones en tests individuales."""
    with app.app_context():
        connection = db.engine.connect()
        # Iniciar una transacción anidada para aislar los cambios del test
        transaction = connection.begin()
        db.session.begin_nested() 
        
        # Reemplazar la sesión para que use la conexión transaccional
        db.session.connection = connection
        
        yield db.session

        # Limpiar la sesión al finalizar el test
        db.session.remove()
        # Hacer rollback de toda la transacción para deshacer los cambios
        transaction.rollback()
        connection.close()


# ----------------------------------------------
# Fixtures de Datos de Prueba
# ----------------------------------------------

@pytest.fixture(scope='function')
def admin_user(app):
    """Recupera el objeto Usuario Administrador."""
    with app.app_context():
        return Usuario.query.filter_by(rol='Administrador').first()

@pytest.fixture(scope='function')
def turista_user(app):
    """Recupera el objeto Usuario Turista."""
    with app.app_context():
        return Usuario.query.filter_by(rol='Turista').first()

@pytest.fixture(scope='function')
def alojamiento_servicio(app):
    """Recupera el objeto Servicio de Alojamiento."""
    with app.app_context():
        return Servicio.query.filter_by(nombre='Hotel Centro').first()
        
# ----------------------------------------------
# Fixtures de Utilidad
# ----------------------------------------------

@pytest.fixture(scope='function')
def login_user(client):
    """
    Fixture que devuelve una función para iniciar sesión con un usuario.
    Se utiliza en los tests: login_user(turista_user)
    """
    def _login(user_object):
        """Inicia sesión usando FlaskLoginClient y el objeto Usuario."""
        # El FlaskLoginClient (establecido en el fixture 'app') permite 
        # iniciar sesión pasando el objeto de usuario.
        return client.login(user=user_object)
    
    return _login
