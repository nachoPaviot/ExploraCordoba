from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.exceptions import abort
from app.utils import db, post_permission_required
from app.models import Posteo
from . import main

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
