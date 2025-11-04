from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
from app.utils import db, posteo_permisos_required
from app.models import Posteo
from . import main

# Ruta para ver el foro y el formulario de posteo
@main.route('/foro', methods=['GET', 'POST'])
@login_required 
def foro():
    posteos = Posteo.query.order_by(Posteo.fecha_creacion.desc()).all()
    
    if request.method == 'POST':
        # Verificar el rol (solo Turistas pueden postear)
        turista_rol_id = current_app.config.get('ROL_TURISTA_ID', 5)
        if current_user.rol_id != turista_rol_id:
            flash('No tenés permiso para postear', 'danger')
            return redirect(url_for('main.foro'))
            
        # Recibir datos del formulario
        titulo = request.form.get('titulo')
        contenido = request.form.get('contenido')
        posteo_padre_id_str = request.form.get('parent_id')
        posteo_padre_id = int(posteo_padre_id_str) if posteo_padre_id_str and posteo_padre_id_str.isdigit() else None

        
        if not contenido or len(contenido.strip()) < 5:
            flash('El comentario debe ser de al menos 5 carácteres.', 'danger')
        else:
            try:
                # Crea el nuevo posteo
                nuevo_posteo = Posteo(
                    titulo=titulo,
                    contenido=contenido,
                    usuario_id=current_user.usuario_id,
                    posteo_padre_id=posteo_padre_id
                )
                db.session.add(nuevo_posteo)
                db.session.commit()
                
                flash('Comentario publicado con éxito', 'success')
                # Redirige para que al refrescar no se duplique el comentario
                return redirect(url_for('main.foro'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error al publicar el comentario: {e}', 'danger')

    posteos = Posteo.query.filter_by(posteo_padre_id=None).order_by(Posteo.fecha_creacion.desc()).all()
    return render_template('foro.html', title='Foro de Viajeros', posteos=posteos)

# Ruta para eliminar posteo
@main.route('/posteo/eliminar/<int:posteo_id>', methods=['POST'])
@posteo_permisos_required
@login_required
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
@posteo_permisos_required
@login_required
def editar_posteo(posteo_id, posteo):
    
    if request.method == 'POST':
        nuevo_contenido = request.form.get('contenido')
        nuevo_titulo = request.form.get('titulo')
        
        if not nuevo_contenido or len(nuevo_contenido.strip()) < 5:
            flash('El comentario debe ser de al menos 5 carácteres.', 'danger')
            # renderiza de nuevo para que no pierda los datos por algún error
            return render_template('editar_posteo.html', posteo=posteo, title='Editar Comentario')
            
        try:
            # Actualiza el posteo con los nuevos datos
            posteo.contenido = nuevo_contenido
            posteo.titulo = nuevo_titulo
            posteo.fecha_edicion = datetime.utcnow()
            
            db.session.commit()
            flash('Comentario actualizado con éxito.', 'success')
            return redirect(url_for('main.foro'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el comentario: {e}', 'danger')
            
    return render_template('editar_posteo.html', 
                            title='Editar Comentario', 
                            posteo=posteo)
