import pytest
from flask import url_for, get_flashed_messages
from app.models import Cotizacion, Servicio, Destino
from datetime import date, timedelta
import math

class TestCotizadorRoutes:

    @staticmethod
    def _setup_url_for_context(client):
        """Configura el SERVER_NAME para url_for."""
        client.application.config['SERVER_NAME'] = 'testserver.com'

    def test_cotizador_acceso_requiere_login(self, client):
        """Verifica que la página de cotizador requiera que el usuario esté logueado."""
        TestCotizadorRoutes._setup_url_for_context(client)
        app = client.application
        with app.app_context():
            cotizador_url = url_for('main.cotizador')

        response = client.get(cotizador_url)
        
        # Debe redirigir al login (302)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_cotizador_get_acceso_con_login(self, client, turista_user, login_user):
        """Verifica que un Turista logueado pueda acceder a la página GET."""
        TestCotizadorRoutes._setup_url_for_context(client)
        login_user(turista_user)
        app = client.application

        with app.app_context():
            cotizador_url = url_for('main.cotizador')

        response = client.get(cotizador_url, follow_redirects=True)

        assert response.status_code == 200
        assert b'Cotizador de Servicios' in response.data
        
    def test_cotizacion_error_fecha_invalida(self, client, turista_user, login_user):
        """Verifica que se produzca un error flash si la fecha de fin es anterior a la de inicio."""
        TestCotizadorRoutes._setup_url_for_context(client)
        login_user(turista_user)
        app = client.application

        fecha_inicio = date.today() + timedelta(days=5)
        fecha_fin = date.today() # Fecha de fin anterior a la de inicio

        data = {
            'servicio': '5000', 
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'personas': '1'
        }
        
        with app.app_context():
            cotizador_url = url_for('main.cotizador')
            
        response = client.post(cotizador_url, data=data, follow_redirects=True)

        # Aserción de Estado: debe volver a la misma página
        assert response.status_code == 200

        # Aserción de Mensaje Flash 
        expected_message = b'La fecha de fin del viaje no puede ser anterior a la fecha de inicio.'
        assert expected_message in response.data, "El mensaje de error por fecha inválida no se encontró en el HTML."

        # Aserción de DB: Verificar que NO se guardó la cotización
        with app.app_context():
            # Buscamos por la cantidad de personas y el estado inicial, esperando NO encontrarla
            cotizacion = Cotizacion.query.filter_by(cantidad_personas=1, estado='Pendiente').first()
            assert cotizacion is None, "Se guardó una cotización a pesar de la fecha inválida."


# Tests de Funcionalidad y DB (Fuera de la clase)
def test_cotizacion_se_realiza_con_exito_alojamiento(client, turista_user, login_user, db_session, alojamiento_servicio):
    """
    Verifica la creación exitosa de una Cotización de ALOJAMIENTO (Unidad: Noche).
    Cálculo: Precio Base ($100) * Personas (2) * Días (3) = $600.
    """
    TestCotizadorRoutes._setup_url_for_context(client)
    login_user(turista_user)
    app = client.application
    
    # Fechas de la cotización: 3 días de viaje
    fecha_inicio = date.today()
    fecha_fin = fecha_inicio + timedelta(days=2) 

    # Datos para el formulario POST
    data = {
        'servicio': str(alojamiento_servicio.servicio_id), # ID 5000
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
        'personas': '2'
    }

    with app.app_context():
        cotizador_url = url_for('main.cotizador')
        
    # Realizar el POST
    response = client.post(cotizador_url, data=data, follow_redirects=True)

    # 1. Aserción de Estado: Debe cargar la página (200 OK)
    assert response.status_code == 200

    # 2. Verificación del Cálculo (debe ser: 100 * 2 personas * 3 días = 600)
    expected_cost = alojamiento_servicio.precio_base * 2 * 3
    
    # 3. Aserción de DB: Verificar que la Cotización se guardó correctamente
    with app.app_context():
        # Buscar la cotización más reciente del usuario
        cotizacion = Cotizacion.query.filter_by(usuario_id=turista_user.usuario_id).order_by(Cotizacion.cotizacion_id.desc()).first()
        
        assert cotizacion is not None, "La cotización no se guardó en la base de datos."
        
        # Verificar el cálculo del precio total 
        assert math.isclose(cotizacion.precio_total, expected_cost), \
            f"Cálculo incorrecto. Esperado: {expected_cost}, Obtenido: {cotizacion.precio_total}"
        
        assert cotizacion.cantidad_personas == 2
        assert cotizacion.servicio_id == alojamiento_servicio.servicio_id


def test_servicios_existen_en_db(app):
    """
    Verifica que los servicios de prueba (creados en conftest.py) existen 
    en la base de datos in-memory.
    """
    with app.app_context():
        servicios = Servicio.query.all()
        
        # Verificamos que se hayan cargado al menos los 2 servicios del seeder
        assert servicios, "La lista de servicios está vacía. El seeder no funcionó."
        assert len(servicios) >= 2, f"Se esperaban al menos 2 servicios, se encontraron {len(servicios)}."
