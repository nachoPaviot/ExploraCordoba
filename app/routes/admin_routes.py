from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from werkzeug.exceptions import abort
from app.utils import admin_required
from app.models import Cotizacion, Usuario, Rol
from app.extensions import db, bcrypt
from . import main

@main.route('/admin')
@login_required 
@admin_required
def admin_panel():
    # Conseguir las cotizaciones para mostrarlas al admin
    cotizaciones = Cotizacion.query.all()

    return render_template('panel_admin.html', 
                           cotizaciones=cotizaciones, 
                           title='Panel de Administración')

@main.route('/admin/crear_usuario', methods=['GET', 'POST'])
@login_required 
@admin_required
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