from flask import render_template, redirect, url_for, flash, request
from app.extensions import db 
from app.models import Destino, Servicio
from flask_login import login_required, current_user 
from . import main

@main.route('/proveedor')
@login_required 
def proveedor_panel():
    
    return render_template('panel_proveedor.html', 
                           title='Panel de Proveedor')

@main.route('/proveedor/crear/servicio', methods=['GET', 'POST'])
@login_required
def crear_servicio():

    destinos = []
    try:
        destinos = Destino.query.order_by(Destino.nombre).all()
    except Exception as e:
        flash('Error al cargar la lista de Destinos.', 'danger')
        print(f"Database Error fetching Destinations: {e}")

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio_base_str = request.form.get('precio_base')
        unidad = request.form.get('unidad')
        destino_id_str = request.form.get('destino_id')
        
        # Validación básica
        if not nombre or not precio_base_str or not destino_id_str or not unidad:
            flash('Todos los campos obligatorios deben ser completados.', 'danger')
            return redirect(url_for('main.crear_servicio'))

        try:
            precio_base = float(precio_base_str)
            destino_id = int(destino_id_str)
            
            if precio_base <= 0:
                flash('El precio base debe ser mayor a cero.', 'danger')
                return redirect(url_for('main.crear_servicio'))
                
            # Verificar si el destino ID es válido
            if not any(d.destino_id == destino_id for d in destinos):
                flash('Destino seleccionado inválido.', 'danger')
                return redirect(url_for('main.crear_servicio'))

            new_servicio = Servicio(
                nombre=nombre,
                descripcion=descripcion,
                precio_base=precio_base,
                unidad=unidad,
                status='Disponible',
                destino_id=destino_id,
                proveedor_id=current_user.usuario_id 
            )
            
            db.session.add(new_servicio)
            db.session.commit()
            
            flash(f'¡Servicio "{new_servicio.nombre}" registrado exitosamente!', 'success')
            return redirect(url_for('main.crear_servicio'))

        except ValueError:
            flash('Error: El precio base debe ser un número válido.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el servicio en la base de datos: {e}', 'danger')
            print(f"Database Rollback Error: {e}")


    servicios_proveedor = []
    try:
        servicios_proveedor = Servicio.query.filter_by(proveedor_id=current_user.usuario_id).all()
    except Exception as e:
        flash('Error al cargar la lista de tus servicios.', 'warning')
        print(f"List Fetch Error: {e}")
        
    return render_template('proveedor_crear_servicio.html', destinos=destinos, servicios=servicios_proveedor)
