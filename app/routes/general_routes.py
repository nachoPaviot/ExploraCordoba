from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.exceptions import abort
from app.extensions import db, bcrypt
from app.models import Usuario
from . import main

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
            flash(f'Error en el registro. Ya existe el usuario', 'danger')
    
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