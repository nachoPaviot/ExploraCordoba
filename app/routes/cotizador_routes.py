from datetime import datetime
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Destino, Servicio, Cotizacion, Reserva
from app.extensions import db
from sqlalchemy.orm import joinedload
from . import main

@main.route('/cotizador', methods=['GET', 'POST'])
@login_required
def cotizador():
    # Cargar todos los destinos con sus servicios relacionados
    destinos = Destino.query.options(joinedload(Destino.servicios)).all()
    cotizacion_resultado = None

    if request.method == 'POST':
        try:
            servicio_id = request.form.get('servicio')
            fecha_inicio_str = request.form.get('fecha_inicio')
            fecha_fin_str = request.form.get('fecha_fin')
            personas = int(request.form.get('personas'))

            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date() if fecha_fin_str else fecha_inicio

            if fecha_inicio > fecha_fin:
                flash('La fecha de fin no puede ser anterior a la fecha de inicio.', 'danger')
                return render_template('cotizador.html', 
                                       destinos=destinos, 
                                       cotizacion_resultado=cotizacion_resultado,
                                       title='Cotizador')
            
            servicio = Servicio.query.get(servicio_id)
            if not servicio:
                flash('Servicio no encontrado.', 'danger')
                return render_template('cotizador.html', 
                                       destinos=destinos, 
                                       cotizacion_resultado=cotizacion_resultado,
                                       title='Cotizador')
            
            dias = (fecha_fin - fecha_inicio).days + 1

            total = servicio.precio_base * personas

            if servicio.unidad.lower() in ['día', 'dias']:
                total = total * dias

            cotizacion = Cotizacion.query.filter_by(
                usuario_id=current_user.usuario_id,
                servicio_id=servicio_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                cantidad_personas=personas,
            ).first()

            if not cotizacion:
                cotizacion = Cotizacion(
                    usuario_id=current_user.usuario_id,
                    servicio_id=servicio_id,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    cantidad_personas=personas,
                    precio_total=total,
                )
                db.session.add(cotizacion)
                db.session.commit()
                flash('Cotización calculada y guardada correctamente.', 'success')
            else:
                cotizacion.precio_total = total
                db.session.commit() 
                flash('Ya existe una cotización con estos parámetros.', 'info')
                        
            reserva_asociada = Reserva.query.filter_by(cotizacion_id=cotizacion.cotizacion_id).first()
                    
            estado_reserva = reserva_asociada.estado if reserva_asociada else 'Pendiente'
            es_reservable = reserva_asociada is None

            cotizacion_resultado = {
                'cotizacion_id': cotizacion.cotizacion_id,
                'destino': servicio.destino.nombre,
                'servicio': servicio.nombre,
                'precio_base': servicio.precio_base,
                'dias': dias,
                'personas': personas,
                'total': total,
                'es_reservable': es_reservable,
                'estado': estado_reserva
            }

        except ValueError:
            flash('Error: Verifica que todos los campos numéricos y de fecha sean válidos.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al procesar la cotización: {e}', 'danger')


    return render_template('cotizador.html', 
                           destinos=destinos, 
                           cotizacion_resultado=cotizacion_resultado,
                           title='Cotizador')


@main.route('/reservar_cotizacion/<int:cotizacion_id>', methods=['POST'])
@login_required
def reservar_cotizacion(cotizacion_id):
    cotizacion = Cotizacion.query.get_or_404(cotizacion_id)
    
    reserva_existente = Reserva.query.filter_by(cotizacion_id=cotizacion_id).first()
    
    if reserva_existente:
        flash(f'Esta cotización ya tiene una reserva con estado "{reserva_existente.estado}".', 'warning')
        return redirect(url_for('main.cotizador'))

    try:
        nueva_reserva = Reserva(
            usuario_id=cotizacion.usuario_id,
            servicio_id=cotizacion.servicio_id,
            cotizacion_id=cotizacion.cotizacion_id,
            fecha_servicio_inicio=cotizacion.fecha_inicio,
            fecha_servicio_fin=cotizacion.fecha_fin,
            cantidad_personas=cotizacion.cantidad_personas,
            costo_total=cotizacion.precio_total,
            estado='Pendiente',
            fecha_reserva=datetime.utcnow()
        )
        db.session.add(nueva_reserva)
        db.session.commit()
        
        flash('Reserva solicitada exitosamente. Un prestador del servicio revisará tu solicitud.', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la reserva: {e}', 'danger')

    return redirect(url_for('main.cotizador'))