from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.exceptions import abort
from .utils import db, bcrypt, login_manager, admin_required, post_permission_required
from .models import Usuario, Destino, Servicio, Cotizacion, Posteo

main = Blueprint('main', __name__)

# ruta raíz
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Redirige si ya está logeado

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            email = request.form['email']
            dni = request.form['dni']
            password = request.form['password']
            
            # Para mayor seguridad, se hashea la contraseña
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Crear el nuevo usuario turista
            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=email,
                dni=dni,
                contrasena=hashed_password,
                rol_id=5 # Asignar Rol de Turista
            )
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash('Tu cuenta fue creada con éxito. ¡Ya podés iniciar sesión!', 'success')
            return redirect(url_for('main.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el usuario: {e}', 'danger')
    
    return render_template('registro.html', title='Registro')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and bcrypt.check_password_hash(usuario.contrasena, password):
            # Iniciar sesión con Flask-Login
            login_user(usuario, remember=True)
            flash('Inicio de sesión exitoso.', 'success')
            
            # Redirige al usuario a la página que busca o al índice
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Fallo el inicio de sesión. Por favor, verifica tu email y contraseña.', 'danger')

    return render_template('login.html', title='Login')

@main.route('/logout')
@login_required # Solo usuarios logeados pueden acceder
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('main.index'))

from .models import Destino # Necesario importar este modelo aca

@main.route('/mapa_destinos')
@login_required 
def mapa_destinos():
    # Obtener todos los objetos Destino
    destinos_objetos = Destino.query.all()
    
    # Serialización: Convertir la lista de objetos a una lista de diccionarios
    destinos_serializados = [d.to_dict() for d in destinos_objetos]
    
    # Pasa la lista serializada a la plantilla
    return render_template(
        'mapa_destinos.html', 
        title='Mapa de Destinos', 
        destinos=destinos_serializados
    )

@main.route('/cotizador', methods=['GET', 'POST'])
@login_required
def cotizador():
    """Ruta para el Cotizador (F4: Cotización automática)"""
    
    # Obtener datos de la DB
    destinos = Destino.query.options(db.joinedload(Destino.servicios)).all()
    servicios = Servicio.query.all()
    
    cotizacion_resultado = None
    
    if request.method == 'POST':
        # Obtener datos del formulario
        try:
            servicio_id_solicitado = int(request.form['servicio'])
            fecha_inicio_str = request.form['fecha_inicio']
            fecha_fin_str = request.form['fecha_fin']
            cantidad_personas = int(request.form['personas'])
            
            # Convertir fechas de string a objetos date/datetime
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            
            # Buscar el servicio en la BD
            servicio_seleccionado = Servicio.query.get(servicio_id_solicitado)
            
            # Validacion fechas
            if fecha_fin < fecha_inicio:
                flash('Error: La fecha de fin del viaje no puede ser anterior a la fecha de inicio.', 'danger')
                # Regresa el formulario vacío
                return render_template('cotizador.html', destinos=destinos, cotizacion_resultado=None, title='Cotizador de Servicios')

            if servicio_seleccionado:
                dias = (fecha_fin - fecha_inicio).days + 1
                
                # Calculo: Costo Base * Personas * Días
                if servicio_seleccionado.unidad == 'Noche':
                    costo = servicio_seleccionado.precio_base * cantidad_personas * dias
                elif servicio_seleccionado.unidad == 'Persona':
                    costo = servicio_seleccionado.precio_base * cantidad_personas
                else:
                    costo = servicio_seleccionado.precio_base * cantidad_personas # Por defecto

                # Guarda la cotización en la DB
                nueva_cotizacion = Cotizacion(
                    usuario_id=current_user.usuario_id,
                    servicio_id=servicio_seleccionado.servicio_id,
                    fecha_inicio_viaje=fecha_inicio,
                    fecha_fin_viaje=fecha_fin,
                    cantidad_personas=cantidad_personas,
                    precio_total=costo,
                    estado='Pendiente'
                )
                
                db.session.add(nueva_cotizacion)
                db.session.commit()
                
                # Mostrar resultado en la plantilla
                cotizacion_resultado = {
                    'destino': servicio_seleccionado.destino.nombre,
                    'servicio': servicio_seleccionado.nombre,
                    'total': costo,
                    'personas': cantidad_personas,
                    'dias': dias,
                    'costo_base': servicio_seleccionado.precio_base
                }

        except Exception as e:
            db.session.rollback()
            cotizacion_resultado = {'error': f'Ocurrió un error en la cotización: {e}'} 

    # Renderizar la plantilla
    return render_template('cotizador.html', 
                           destinos=destinos, 
                           servicios=servicios, 
                           cotizacion_resultado=cotizacion_resultado,
                           title='Cotizador de Servicios')

# Ruta para el Panel de Control del Admin.
@main.route('/admin')
@login_required 
@admin_required
def admin_panel():
    """Ruta del Panel de Control - Solo para Admin."""
    # Conseguir las cotizaciones para mostrarlas al admin
    cotizaciones = Cotizacion.query.all()

    return render_template('panel_admin.html', 
                           cotizaciones=cotizaciones, 
                           title='Panel de Administración')

# Ruta para ver el foro y el formulario de posteo
@main.route('/foro', methods=['GET', 'POST'])
@login_required 
def foro():
    # Obtener todos los posteos ordenados por fecha de creación descendente
    posteos = Posteo.query.order_by(Posteo.fecha_creacion.desc()).all()
    
    if request.method == 'POST':
        # Verificar el rol (solo Turistas pueden postear)
        turista_rol_id = current_app.config.get('ROL_TURISTA_ID', 5)
        if current_user.rol_id != turista_rol_id:
            flash('Solo los usuarios turistas pueden publicar en el foro.', 'danger')
            return redirect(url_for('main.foro'))
            
        # Recibir datos del formulario
        titulo = request.form.get('titulo')
        contenido = request.form.get('contenido')
        
        if not contenido or len(contenido.strip()) < 25:
            flash('El comentario debe ser de al menos 25 carácteres.', 'danger')
        else:
            try:
                # Crea el nuevo posteo
                nuevo_posteo = Posteo(
                    titulo=titulo,
                    contenido=contenido,
                    usuario_id=current_user.usuario_id 
                )
                db.session.add(nuevo_posteo)
                db.session.commit()
                
                flash('Comentario publicado con éxito.', 'success')
                # Redirige para que al refrescar no se duplique el comentario
                return redirect(url_for('main.foro'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error al publicar el comentario: {e}', 'danger')

    return render_template('foro.html', title='Foro de Viajeros', posteos=posteos)

# Ruta para eliminar posteo
@main.route('/posteo/eliminar/<int:posteo_id>', methods=['POST'])
@login_required
@post_permission_required
def eliminar_posteo(posteo_id, posteo):
    
    try:
        db.session.delete(posteo)
        db.session.commit()
        flash('El comentario ha sido eliminado.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el comentario: {e}', 'danger')

    return redirect(url_for('main.foro'))

# Ruta para editar posteos
@main.route('/posteo/editar/<int:posteo_id>', methods=['GET', 'POST'])
@login_required
@post_permission_required
def editar_posteo(posteo_id, posteo):
    
    if request.method == 'POST':
        nuevo_contenido = request.form.get('contenido')
        nuevo_titulo = request.form.get('titulo')
        
        if not nuevo_contenido or len(nuevo_contenido.strip()) < 25:
            flash('El comentario debe ser de al menos 25 carácteres.', 'danger')
            # renderiza de nuevo para que no pierda los datos por algún error
            return render_template('editar_posteo.html', posteo=posteo, title='Editar Comentario')
            
        try:
            # Actualiza el posteo con los nuevos datos
            posteo.contenido = nuevo_contenido
            posteo.titulo = nuevo_titulo
            posteo.fecha_edicion = datetime.utcnow() # O datetime.now() dependiendo de tu DB
            
            db.session.commit()
            flash('Comentario actualizado con éxito.', 'success')
            return redirect(url_for('main.foro'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el comentario: {e}', 'danger')
            
    # el GET
    return render_template('editar_posteo.html', 
                            title='Editar Comentario', 
                            posteo=posteo)

