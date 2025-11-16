from flask import render_template, flash, redirect, url_for
from flask_login import login_required
from app.models import Destino, Servicio
from sqlalchemy.orm import joinedload
from . import main

@main.route('/mapa_destinos')
@login_required 
def mapa_destinos():
    try:
        # Obtener todos los objetos Destino
        destinos_objetos = Destino.query.all()
    
        # Serialización: Convertir la lista de objetos a una lista de diccionarios
        destinos_serializados = [
            {
                'destino_id': d.destino_id, 
                'nombre': d.nombre,
                'descripcion': d.descripcion,
                'coordenadas': d.coordenadas # Las coordenadas son necesarias para el mapa
            } 
            for d in destinos_objetos
        ]
    except Exception as e:
        flash('Error al cargar los destinos.', 'danger')
        print(f"Database Error: {e}")
        destinos_serializados = []
    
    return render_template(
        'mapa_destinos.html', 
        title='Mapa de Destinos', 
        destinos=destinos_serializados)

@main.route('/destino/<int:destino_id>')
@login_required
def destino_detalle(destino_id):
    try:
        destino = Destino.query.get_or_404(destino_id)
        # Carga los servicios DISPONIBLES para ese destino
        servicios = Servicio.query.filter(
            Servicio.destino_id == destino_id,
            Servicio.status == 'Disponible'
        ).options(
            joinedload(Servicio.proveedor)
        ).order_by(Servicio.nombre).all()

    except Exception as e:
        flash('Error al cargar la información del destino y sus servicios.', 'danger')
        print(f"Database Error: {e}")

        return redirect(url_for('main.mapa_destinos'))

    return render_template('destino_detalle_servicios.html',
                           title=f'Servicios en {destino.nombre}',
                           destino=destino,
                           servicios=servicios)