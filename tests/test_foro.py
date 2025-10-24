import pytest
from flask import url_for, get_flashed_messages
from flask_login import current_user
from app.models import Usuario, Posteo
from conftest import login_test_user
class TestForoRoutes:
    
    # FUNCIÓN CLAVE para corregir el error de url_for
    def _setup_url_for_context(self, client):
        """
        Asegura que el contexto de la aplicación tenga la configuración 
        necesaria (SERVER_NAME) para que url_for funcione fuera de un 
        contexto de solicitud (request context).
        """
        client.application.config['SERVER_NAME'] = 'testserver.com'

    def test_foro_acceso_requiere_login(self, client):
        """Verifica que el acceso al foro sin sesión redirija al login."""
        self._setup_url_for_context(client)
        app = client.application

        with app.app_context():
            foro_url = url_for('main.foro')

        response = client.get(foro_url)

        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_foro_acceso_con_login(self, client, turista_user):
        """Verifica que un usuario Turista logueado pueda acceder a la página del foro."""
        self._setup_url_for_context(client)
        login_test_user(client, turista_user)

        app = client.application
        with app.app_context():
            foro_url = url_for('main.foro')

        response = client.get(foro_url, follow_redirects=True)

        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data 

    def test_solo_turista_puede_postear(self, client, admin_user):
        """Verifica que un usuario Admin NO pueda publicar un posteo (se espera un flash de error)."""
        self._setup_url_for_context(client)
        login_test_user(client, admin_user) 

        app = client.application
        with app.app_context():
            foro_url = url_for('main.foro')

        data = {'titulo': 'Post de prueba Admin', 'contenido': 'Este post no debería crearse.'}
        
        response = client.post(foro_url, data=data, follow_redirects=True)

        # Aserción 1: Debe ser una respuesta exitosa (200 OK)
        assert response.status_code == 200
        
        assert b'permiso para postear' in response.data.lower(), \
             f"El mensaje de error esperado ('No tenés permiso para postear') no se encontró en el HTML."
        
        with app.app_context():
            post = Posteo.query.filter_by(titulo=data['titulo']).first()
            assert post is None, "El posteo del Admin se creó indebidamente."

    def test_turista_crea_posteo_exito(self, client, turista_user, db_session):
        """Verifica que un usuario Turista pueda crear un posteo exitosamente."""
        
        # Configuración inicial de datos de prueba
        self._setup_url_for_context(client)
        login_test_user(client, turista_user) 

        app = client.application
        with app.app_context():
            foro_url = url_for('main.foro')

        data = {'titulo': 'Primer posteo', 'contenido': 'Hola mundo, soy un turista.'}

        # Ejecución de la prueba
        response = client.post(foro_url, data=data, follow_redirects=True)

        # Verificación de resultados
        assert response.status_code == 200

        expected_message_bytes = 'Comentario publicado con éxito'.encode('utf-8')
        
        assert b'Comentario publicado' in response.data, \
             f"El mensaje de éxito esperado ('Comentario publicado con éxito') no se encontró en el HTML."
        
        with app.app_context():
            post = Posteo.query.filter_by(titulo=data['titulo']).first()
            assert post is not None, "El posteo no se encontró en la base de datos."
            
            assert post.usuario_id == turista_user.usuario_id, "El autor del posteo no es el turista correcto."
