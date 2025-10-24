import pytest
from datetime import date, timedelta
from flask import url_for
from app.models import Usuario, Cotizacion, Servicio
from conftest import login_test_user


def test_cotizacion_alojamiento_se_realiza_con_exito(self, client, turista_user, login_user, db_session, alojamiento_servicio):
        """
        Verifica la creación exitosa de una Cotización (alojamiento)
        """
        # Configuración inicial de datos de prueba
        self._setup_url_for_context(client)
        login_user(turista_user)
        app = client.application
        
        fecha_inicio = date.today()
        fecha_fin = fecha_inicio + timedelta(days=2)

        data = {
            'servicio': str(alojamiento_servicio.servicio_id),
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'personas': '2'
        }

        with app.app_context():
            cotizador_url = url_for('main.cotizador')
            
        # Ejecución de la prueba
        response = client.post(cotizador_url, data=data, follow_redirects=True)

        # Aserción 1: Respuesta exitosa
        assert response.status_code == 200

def test_servicios_existen_en_db(self, app):
        """
        Verificar si hay servicios creados en la base de datos (in-memory) 
        para las pruebas.
        """
        
        with app.app_context():
            # Obtener todos los servicios
            servicios = Servicio.query.all()
            
            # Aserción 1: Debe haber al menos un servicio
            assert servicios, "La lista de servicios está vacía"
