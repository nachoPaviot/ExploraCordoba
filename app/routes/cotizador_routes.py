from flask import render_template, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.exceptions import abort
from app.extensions import db
from app.models import Destino, Servicio, Cotizacion
from . import main

@main.route('/cotizador', methods=['GET', 'POST'])
@login_required
def cotizador():
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
                
                # Calculo: Costo Base * Personas * días
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
