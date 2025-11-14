from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.utils import admin_required
from app.models import Cotizacion, Usuario, Rol, Destino, Reserva
from app.extensions import db, bcrypt
from werkzeug.exceptions import abort
from . import main

# Función auxiliar para validar el formato de coordenadas
def validar_coordenadas(coordenadas_str):
    if ',' not in coordenadas_str:
        return False

    try:
        lat_str, lon_str = coordenadas_str.split(',', 1)
        float(lat_str.strip())
        float(lon_str.strip())
        return True
    except ValueError:
        return False
    except Exception:
        return False


@main.route('/admin')
@admin_required
@login_required
def admin_panel():
    # Reservas y Destinos para mostrarlas al admin
    reservas = Reserva.query.all()
    destinos = Destino.query.all()


    return render_template('panel_admin.html', 
                           reservas=reservas,
                           destinos=destinos,
                           title='Panel de Administración')

@main.route('/admin/crear_usuario', methods=['GET', 'POST'])
@admin_required
@login_required 
def crear_usuario():
    roles_a_asignar = Rol.query.filter(Rol.nombre.in_(['Administrador', 'Moderador', 'Proveedor', 'Mesa de Ayuda'])).all()
    
    form_data = {
        'email': request.form.get('email', ''),
        'nombre': request.form.get('nombre', ''),
        'apellido': request.form.get('apellido', ''),
        'rol_id': request.form.get('rol_id', '')
    }

    if request.method == 'POST':
        # obtener la contraseña, que no se guarda en form_data.
        password = request.form.get('password')
        
        # Validamos todos los campos necesarios.
        if not all([form_data['email'], password, form_data['nombre'], form_data['apellido'], form_data['rol_id']]):
            flash('Todos los campos son obligatorios.', 'danger')
        else:
            email = form_data['email']
            rol_id = form_data['rol_id']
            nombre = form_data['nombre']
            apellido = form_data['apellido']
            
            if Usuario.query.filter_by(email=email).first():
                flash('El email ya está registrado.', 'danger')
            else:
                try:
                    nuevo_usuario = Usuario(
                        email=email,
                        nombre=nombre,
                        apellido=apellido,
                        rol_id=int(rol_id)
                    )
                    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                    nuevo_usuario.contrasena = hashed_password 
                    
                    db.session.add(nuevo_usuario)
                    db.session.commit()
                    flash(f'Usuario {nombre} ({nuevo_usuario.rol.nombre}) creado con éxito.', 'success')
                    return redirect(url_for('main.admin_panel'))
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error al crear el usuario: {e}', 'danger')

    selected_rol_id = int(form_data.get('rol_id') or 0) 
    
    rol_options_html = '<option value=""'
    if not selected_rol_id:
        rol_options_html += ' selected'
    rol_options_html += '>Selecciona un rol</option>'

    for rol in roles_a_asignar:
        selected_attr = ' selected' if rol.rol_id == selected_rol_id else ''
        rol_options_html += f'<option value="{rol.rol_id}"{selected_attr}>{rol.nombre}</option>'

    # Mostrar el formulario con los roles o si el POST falla
    return render_template('admin_crear_usuario.html', 
                            rol_options_html=rol_options_html, 
                            form_data=form_data,
                            title='Crear Usuario')

@main.route('/admin/crear_destino', methods=['GET', 'POST'])
@admin_required
@login_required 
def crear_destino():
    form_data = {
        'nombre': request.form.get('nombre', ''),
        'descripcion': request.form.get('descripcion', ''),
        'categoria': request.form.get('categoria', ''),
        'coordenadas': request.form.get('coordenadas', '')
    }

    if request.method == 'POST':
        nombre = form_data['nombre']
        descripcion = form_data['descripcion']
        categoria = form_data['categoria']
        coordenadas = form_data['coordenadas']
        # Validación
        if not all([nombre, descripcion, categoria, coordenadas]):
            flash('Todos los campos del destino son obligatorios.', 'danger')
            return render_template('admin_crear_destino.html', form_data=form_data, title='Crear Nuevo Destino')
        
        elif coordenadas and not validar_coordenadas(coordenadas):
            flash('El formato de coordenadas es incorrecto. Debe ser: latitud,longitud (ej: -32.0673,-64.8833)', 'danger')
            return render_template('admin_crear_destino.html', form_data=form_data, title='Crear Nuevo Destino')

        elif Destino.query.filter_by(nombre=nombre).first():
            flash(f'El destino "{nombre}" ya existe.', 'danger')
            return render_template('admin_crear_destino.html', form_data=form_data, title='Crear Nuevo Destino')
        
        else:
            try:
                nuevo_destino = Destino(
                    nombre=form_data['nombre'],
                    descripcion=form_data['descripcion'],
                    categoria=form_data['categoria'],
                    coordenadas=form_data['coordenadas']
                )
                
                db.session.add(nuevo_destino)
                db.session.commit()
                flash(f'Destino "{nuevo_destino.nombre}" creado con éxito.', 'success')
                return redirect(url_for('main.admin_panel'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear el destino: {e}', 'danger')

    return render_template('admin_crear_destino.html',
                           form_data=form_data,
                           title='Crear Nuevo Destino')

@main.route('/admin/editar_destino/<int:destino_id>', methods=['GET', 'POST'])
@admin_required
@login_required
def editar_destino(destino_id):
    destino = Destino.query.get_or_404(destino_id)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        categoria = request.form.get('categoria')
        coordenadas = request.form.get('coordenadas')

        form_data = {
            'nombre': nombre,
            'descripcion': descripcion,
            'categoria': categoria,
            'coordenadas': coordenadas
        }
        
        if not all([nombre, descripcion, categoria, coordenadas]):
            flash('Todos los campos obligatorios deben ser completados.', 'danger')
            return render_template('admin_editar_destino.html',
                                   form_data=form_data,
                                   title=f'Editar {destino.nombre}',
                                   destino=destino)
        elif not validar_coordenadas(coordenadas):
            flash('El formato de coordenadas es incorrecto. Debe ser: latitud,longitud (ej: -32.0673,-64.8833)', 'danger')       
            return render_template('admin_editar_destino.html',
                                   form_data=form_data,
                                   title=f'Editar {destino.nombre}',
                                   destino=destino)
        try:                
            # Actualiza los datos del destino
            destino.nombre = nombre
            destino.descripcion = descripcion
            destino.categoria = categoria
            destino.coordenadas = coordenadas

            db.session.commit()
            
            flash(f'¡Destino "{destino.nombre}" actualizado exitosamente!', 'success')
            return redirect(url_for('main.admin_panel'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el destino en la base de datos: {e}', 'danger')
            print(f"Database Rollback Error on Update: {e}")

    form_data = {
        'nombre': destino.nombre,
        'descripcion': destino.descripcion,
        'categoria': destino.categoria,
        'coordenadas': destino.coordenadas
    }

    return render_template('admin_editar_destino.html',
                           form_data=form_data,
                           title=f'Editar {destino.nombre}',
                           destino=destino,
                           )


@main.route('/admin/eliminar_destino/<int:destino_id>', methods=['POST'])
@admin_required
@login_required
def eliminar_destino(destino_id):
    destino = Destino.query.get_or_404(destino_id)

    try:
        # Eliminar el destino de la base de datos
        db.session.delete(destino)
        db.session.commit()
        flash(f'Destino "{destino.nombre}" eliminado correctamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ocurrió un error al intentar eliminar el destino: {e}', 'danger')

    return redirect(url_for('main.admin_panel'))