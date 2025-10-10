from flask_sqlalchemy import SQLAlchemy
from .extensions import db, bcrypt, login_manager
from functools import wraps
from flask import abort, current_app, flash
from sqlalchemy import text
from flask_login import current_user


# Función para resetear tablas en PostgreSQL
def reset_sequence(db_instance, table_name, id_column):
    sql_command = f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"
    # Si la tabla tiene claves foráneas (como Cotizacion), TRUNCATE CASCADE es mejor.
    # Si la tabla NO tiene FKs, simplemente 'TRUNCATE TABLE {table_name} RESTART IDENTITY;'
    # Usaremos el comando más seguro y directo que funciona en muchos DBs:
    # db_instance.session.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))
    # O el que ya usamos que requiere solo DELETE y setval si la tabla no se autoincrementa
    db_instance.session.execute(text(f"SELECT setval('{table_name}_{id_column}_seq', 1, false);"))

# Decorador para roles específicos.
def roles_required(role_id):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            # Se verifica el ID del rol del usuario actual
            if not current_user.is_authenticated or current_user.rol_id != role_id:
                # Si no es el rol requerido lanza status 403 (Prohibido)
                return abort(403) 
            return func(*args, **kwargs)
        return decorated_view
    return wrapper

# Decorador de uso rápido para el administrador
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # Asume el ID 1 si no está configurado
        ROL_ADMIN_ID = current_app.config.get('ROL_ADMIN_ID', 1) 
        
        # Llama a la lógica principal de roles_required
        if not current_user.is_authenticated or current_user.rol_id != ROL_ADMIN_ID:
            return abort(403)
        return func(*args, **kwargs)
    return decorated_view

# comandos CLI para crear y sembrar la base de datos
def register_cli_commands(app):
    """Registra los comandos 'crear_db' y 'sembrar_db' en la aplicación."""
    from .models import Rol, Usuario, Destino, Servicio, Cotizacion
    
    #Crea la base de datos y las tablas
    @app.cli.command("crear_db")
    def crear_db():
        with app.app_context():
            db.drop_all()  # limpiar todo antes de crear
            db.create_all()
            print("¡Base de datos y tablas creadas!")

    # Inserta datos de prueba en la base de datos
    @app.cli.command("sembrar_db")
    def sembrar_db():
        with app.app_context():
            # Limpieza
            db.session.query(Cotizacion).delete()
            db.session.query(Servicio).delete()
            db.session.query(Destino).delete()
            db.session.query(Usuario).delete()
            db.session.query(Rol).delete() 
            db.session.commit()
                        
            try:
                # Datos de Ejemplo
                # 1. Roles 
                rol_admin = Rol(rol_id=1, n_rol='Administrador', descripcion='Acceso total a la administración.')
                rol_moderador = Rol(rol_id=2, n_rol='Moderador', descripcion='Puede gestionar contenidos y usuarios.')
                rol_mesa_ayuda = Rol(rol_id=3, n_rol='Mesa de Ayuda', descripcion='Atiende consultas y soporte.')
                rol_proveedor = Rol(rol_id=4, n_rol='Proveedor de Servicios', descripcion='Gestiona sus propios servicios y destinos.')
                rol_turista = Rol(rol_id=5, n_rol='Usuario Turista', descripcion='...')
                
                # 2. Usuarios
                #Admin
                hashed_password_admin = bcrypt.generate_password_hash('admin').decode('utf-8') 
                user_admin = Usuario(
                    usuario_id=1, nombre='Geralt', apellido='De Rivia', email='admin@prueba.com', 
                    dni='00000000', status='Activo', rol_id=1, contrasena=hashed_password_admin
                )                
                #Turista
                hashed_password_turista = bcrypt.generate_password_hash('turista').decode('utf-8') 
                user_turista = Usuario(
                    usuario_id=100, nombre='Juan', apellido='Pérez', email='turista@prueba.com', 
                    dni='12345678', status='Activo', rol_id=5, contrasena=hashed_password_turista
                )

                # 3. Destinos
                destino_carbon = Destino(
                    destino_id=1,
                    nombre='Montaña Carbón', 
                    descripcion='Montañas para trekking.',
                    categoria='Aventura',
                    endpoint='-31.3200,-64.5500'
                )
                destino_overlook = Destino(
                    destino_id=2,
                    nombre='Hotel Overlook',
                    descripcion='Hotel donde ocurren extrañas situaciones.',
                    categoria='Alojamiento',
                    endpoint='-31.4167,-64.1833'
                )

                # 4. Servicios
                servicio_excursion = Servicio(
                    servicio_id=1,
                    nombre='Excursión a Montaña Carbon',
                    descripcion='Recorrida completa de 3 días.',
                    precio_base=15000.00,
                    unidad = 'Persona',
                    destino_id=1
                )

                servicio_alojamiento = Servicio(
                    servicio_id=2,
                    nombre='Alojamiento en Hotel Overlook',
                    descripcion='Una estadía muy particular',
                    precio_base=20000.00,
                    unidad = 'Noche',
                    destino_id=2
                )

                # 5. Cotizaciones
                
                db.session.add_all([rol_admin, 
                                    rol_turista, 
                                    user_admin,
                                    user_turista, 
                                    destino_carbon, 
                                    destino_overlook, 
                                    servicio_excursion, 
                                    servicio_alojamiento]) 
                db.session.commit()

                # Reseteo de secuencias en la base de datos
                # necesario cuando se insertan IDs manualmente para pruebas.
                # Para tabla Usuario
                max_user_id = db.session.query(db.func.max(Usuario.usuario_id)).scalar()
                if max_user_id:
                    db.session.execute(text(f"SELECT setval('usuario_usuario_id_seq', {max_user_id});")) 
                    
                # Para  tabla Destino
                max_destino_id = db.session.query(db.func.max(Destino.destino_id)).scalar()
                if max_destino_id:
                    db.session.execute(text(f"SELECT setval('destino_destino_id_seq', {max_destino_id});")) 

                # Para la tabla Servicio
                max_servicio_id = db.session.query(db.func.max(Servicio.servicio_id)).scalar()
                if max_servicio_id:
                    db.session.execute(text(f"SELECT setval('servicio_servicio_id_seq', {max_servicio_id});")) 

                #Para la tabla Rol
                max_rol_id = db.session.query(db.func.max(Rol.rol_id)).scalar()
                if max_rol_id:
                    db.session.execute(text(f"SELECT setval('rol_rol_id_seq', {max_rol_id});")) 

                db.session.commit()
                print("¡Datos iniciales y secuencias insertadas correctamente!")

                print("¡Datos iniciales insertados correctamente!")

            except Exception as e:
                db.session.rollback()
                print(f"Error al insertar datos iniciales: {e}")

# Decorador de la librería wraps para verificar permisos sobre un posteo
def post_permission_required(f):
    """
    Decorador que verifica si el usuario es el autor, admin o moderador.
    Debe pasarse el posteo como argumento 'posteo'.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from .models import Posteo
        # La función de vista debe pasar el objeto Posteo como argumento
        posteo_id = kwargs.get('posteo_id')
        if posteo_id is None:
            raise Exception("Ruta mal configurada. El decorador requiere 'posteo_id' en la URL.")
        
        posteo = Posteo.query.get_or_404(posteo_id)
        # 1. Leer los IDs de la configuración
        admin_rol_id = current_app.config.get('ROL_ADMIN_ID', 1) 
        moderador_rol_id = current_app.config.get('ROL_MODERADOR_ID', 2)
        
        # 2. Lógica de Permisos
        autor = current_user.usuario_id == posteo.usuario_id
        admin_o_moderador = current_user.rol_id in [admin_rol_id, moderador_rol_id]

        if not (autor or admin_o_moderador):
            flash('No tenés permiso para eliminar ni editar este comentario.', 'danger')
            abort(403)
        kwargs['posteo'] = posteo  # Pasa el posteo para la función decorada   

        return f(*args, **kwargs)
    return decorated_function