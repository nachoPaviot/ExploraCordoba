from flask import render_template, redirect, url_for, flash, request
from app.utils import proveedor_required
from app.extensions import db 
from app.models import Destino, Servicio
from flask_login import login_required, current_user 
from . import main

UNIDADES_DISPONIBLES = ['Día', 'Persona', 'Unidad']

@main.route('/proveedor')
@proveedor_required
@login_required
def proveedor_panel():
    servicios_propios = []
    try:        
        servicios_propios = Servicio.query.filter_by(proveedor_id=current_user.usuario_id).all()
    except Exception as e:
        flash('Error al cargar la lista de tus servicios.', 'danger')
        print(f"Database Error fetching Provider Services: {e}")

    return render_template('panel_proveedor.html', 
                           title='Panel de Proveedor',
                           servicios_propios=servicios_propios)

@main.route('/proveedor/crear/servicio', methods=['GET', 'POST'])
@proveedor_required
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
        if not nombre or not descripcion or not precio_base_str or not destino_id_str or not unidad:
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
        
    return render_template('proveedor_crear_servicio.html', 
                           destinos=destinos, 
                           servicios=servicios_proveedor,
                           unidades=UNIDADES_DISPONIBLES
                           )

@main.route('/proveedor/editar/servicio/<int:servicio_id>', methods=['GET', 'POST'])
@proveedor_required
@login_required
def editar_servicio(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)
    
    if servicio.proveedor_id != current_user.usuario_id:
        flash('No tienes permiso para editar este servicio.', 'danger')
        return redirect(url_for('main.proveedor_panel'))

    destinos = Destino.query.order_by(Destino.nombre).all()

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio_base_str = request.form.get('precio_base')
        unidad = request.form.get('unidad')
        destino_id_str = request.form.get('destino_id')
        status = request.form.get('status')
        
        if not nombre or not descripcion or not precio_base_str or not destino_id_str or not unidad:
            flash('Todos los campos obligatorios deben ser completados.', 'danger')
            return redirect(url_for('main.editar_servicio', servicio_id=servicio.servicio_id))
            
        try:
            precio_base = float(precio_base_str)
            destino_id = int(destino_id_str)
            
            if precio_base <= 0:
                flash('El precio base debe ser mayor a cero.', 'danger')
                return redirect(url_for('main.editar_servicio', servicio_id=servicio.servicio_id))
                
            # Actualiza los datos del servicio
            servicio.nombre = nombre
            servicio.descripcion = descripcion
            servicio.precio_base = precio_base
            servicio.unidad = unidad
            servicio.destino_id = destino_id
            servicio.status = status
            
            db.session.commit()
            
            flash(f'¡Servicio "{servicio.nombre}" actualizado exitosamente!', 'success')
            return redirect(url_for('main.proveedor_panel'))

        except ValueError:
            flash('Error: El precio base debe ser un número válido.', 'danger')
            db.session.rollback()
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el servicio en la base de datos: {e}', 'danger')
            print(f"Database Rollback Error on Update: {e}")
            
    return render_template('proveedor_editar_servicio.html', 
                           title=f'Editar {servicio.nombre}',
                           servicio=servicio,
                           destinos=destinos,
                           unidades=UNIDADES_DISPONIBLES
                           )


@main.route('/proveedor/eliminar/servicios/<int:servicio_id>', methods=['POST'])
@proveedor_required
@login_required
def eliminar_servicio(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)

    try:
        # Eliminar el servicio de la base de datos
        db.session.delete(servicio)
        db.session.commit()
        flash(f'Servicio "{servicio.nombre}" eliminado correctamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ocurrió un error al intentar eliminar el servicio: {e}', 'danger')

    return redirect(url_for('main.proveedor_panel'))