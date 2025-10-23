import pytest
from flask import url_for, get_flashed_messages
from flask_login import current_user
from app.models import Usuario, Posteo # Se asume que estos son tus modelos reales
from conftest import login_test_user # Importamos la función login definida en conftest

# La función login_test_user debe estar definida en conftest.py para ser importada.

class TestForoRoutes:
    
    # FUNCIÓN CLAVE para corregir el error de url_for
    def _setup_url_for_context(self, client):
        """
        Asegura que el contexto de la aplicación tenga la configuración 
        necesaria (SERVER_NAME) para que url_for funcione fuera de un 
        contexto de solicitud (request context).
        """
        client.application.config['SERVER_NAME'] = 'testserver.com'

    # 1. PASÓ
    def test_foro_acceso_requiere_login(self, client):
        """Verifica que el acceso al foro sin sesión redirija al login (403 o 302)."""
        self._setup_url_for_context(client)
        app = client.application

        with app.app_context():
            foro_url = url_for('main.foro')

        response = client.get(foro_url)

        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    # 2. PASÓ
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

    # 3. CORREGIDO: Verificación de Flash con encode()
    def test_foro_post_solo_turista_puede_postear(self, client, admin_user):
        """Verifica que un usuario Admin NO pueda publicar un posteo (se espera un flash de error)."""
        self._setup_url_for_context(client)
        # Login con el usuario Admin
        login_test_user(client, admin_user) 

        app = client.application
        with app.app_context():
            foro_url = url_for('main.foro')

        # Datos para el posteo
        data = {'titulo': 'Post de prueba Admin', 'contenido': 'Este post no debería crearse.'}
        
        # Realizar el POST con redirección automática
        response = client.post(foro_url, data=data, follow_redirects=True)

        # Aserción 1: Debe ser la página de foro (200 OK)
        assert response.status_code == 200, f"El Admin fue redirigido a un error inesperado. Status: {response.status_code}"
        
        # Aserción 2 (FLASH CORREGIDO): El mensaje de error debe estar en el HTML renderizado.
        # Usamos .encode('utf-8') para garantizar la codificación correcta, y simplificamos la cadena.
        expected_message_bytes = 'No tenés permiso para postear'.encode('utf-8')
        
        # Buscamos solo una parte de la cadena por si hay caracteres ocultos o formato extra.
        # Buscamos 'permiso para postear'
        assert b'permiso para postear' in response.data.lower(), \
             f"El mensaje de error esperado ('No tenés permiso para postear') no se encontró en el HTML."
        
        # Aserción 3 (DB CHECK): Verificar que NO se creó el posteo en la DB
        with app.app_context():
            post = Posteo.query.filter_by(titulo=data['titulo']).first()
            assert post is None, "El posteo del Admin se creó indebidamente."


    # 4. CORREGIDO: AttributeError 'autor_id' -> cambiado a 'usuario_id'
    def test_foro_post_turista_crea_posteo_exito(self, client, turista_user, db_session):
        """Verifica que un usuario Turista pueda crear un posteo exitosamente."""
        self._setup_url_for_context(client)
        # Login con el usuario Turista
        login_test_user(client, turista_user) 

        app = client.application
        with app.app_context():
            foro_url = url_for('main.foro')

        # Datos para el posteo
        data = {'titulo': 'Mi primer posteo', 'contenido': 'Hola mundo, soy un turista.'}

        # Realizar el POST con redirección automática
        response = client.post(foro_url, data=data, follow_redirects=True)

        # Aserción 1: Verificar el éxito (200 OK de la página de foro)
        assert response.status_code == 200

        # Aserción 2 (FLASH CORREGIDO): El mensaje de éxito debe estar en el HTML renderizado.
        expected_message_bytes = 'Comentario publicado con éxito'.encode('utf-8')
        
        # Buscamos solo una parte de la cadena
        assert b'Comentario publicado' in response.data, \
             f"El mensaje de éxito esperado ('Comentario publicado con éxito') no se encontró en el HTML."
        
        # Aserción 3 (DB CHECK): Verificar que el posteo SÍ se creó en la DB
        with app.app_context():
            post = Posteo.query.filter_by(titulo=data['titulo']).first()
            assert post is not None, "El posteo no se encontró en la base de datos."
            
            # CORRECCIÓN: Asumimos que la clave foránea en Posteo se llama 'usuario_id'
            # Si el nombre es diferente (ej: autor_id), debes usar el nombre real de tu modelo.
            assert post.usuario_id == turista_user.usuario_id, "El autor del posteo no es el turista correcto."
