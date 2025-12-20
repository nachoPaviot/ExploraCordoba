from datetime import datetime
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Ticket, RespuestaTicket, Usuario
from app.extensions import db
from app.utils import validar_datos_ticket
from config import ROL_ADMIN_ID, ROL_SOPORTE_ID
from sqlalchemy.orm import joinedload
from . import main

@main.route('/soporte', methods=['GET'])
@main.route('/soporte/mis_tickets', methods=['GET'])
@login_required
def mis_tickets():    
    tickets = current_user.tickets_creados.order_by(Ticket.fecha_creacion.desc()).all()

    return render_template('tickets.html', 
                            tickets=tickets, 
                            title='Mis Tickets de Soporte')

@main.route('/soporte/crear', methods=['GET', 'POST'])
@login_required
def crear_ticket():    
    errores = {}
    form_data = {}

    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        _errores, data = validar_datos_ticket(form_data)
        
        errores = _errores if _errores is not None else {}
        
        if errores:
            flash('Por favor, corrige los errores en el formulario.', 'danger')
        else:
            try:
                nuevo_ticket = Ticket(
                    usuario_id=current_user.usuario_id,
                    asunto=data['asunto'],
                    mensaje=data['mensaje'],
                    estado='Abierto'
                )
                
                db.session.add(nuevo_ticket)
                db.session.commit()
                flash('Tu ticket de soporte ha sido creado exitosamente. Pronto nos pondremos en contacto.', 'success')
                return redirect(url_for('main.mis_tickets'))
            
            except Exception as e:
                db.session.rollback()
                flash(f'Ocurrió un error al crear el ticket: {e}', 'danger')
                
    return render_template('crear_ticket.html', 
                            form_data=form_data, 
                            errores=errores,
                            title='Crear Ticket de Soporte')

@main.route("/soporte/gestion", methods=['GET'])
@login_required
def soporte_panel():
    if current_user.rol_id not in [ROL_ADMIN_ID, ROL_SOPORTE_ID]:
        flash('Acceso denegado. Se requiere rol de Soporte o Administrador.', 'danger')
        return redirect(url_for('main.tickets'))

    tickets_activos = Ticket.query.options(
        joinedload(Ticket.creador),
        joinedload(Ticket.asignado_a)
    ).filter(
        Ticket.estado.in_(['Abierto', 'En Progreso', 'Pendiente de Usuario'])
    ).order_by(
        Ticket.fecha_actualizacion.desc()
    ).all()

    tickets_cerrados = Ticket.query.options(
        joinedload(Ticket.creador),
        joinedload(Ticket.asignado_a)
    ).filter(
        Ticket.estado == 'Cerrado'
    ).order_by(
        Ticket.fecha_actualizacion.desc()
    ).limit(50).all() 

    return render_template('soporte.html',
                           tickets_activos=tickets_activos,
                           tickets_cerrados=tickets_cerrados,
                           title='Gestión de Tickets de Soporte')

@main.route("/soporte/ticket/<int:ticket_id>", methods=['GET', 'POST'])
@login_required
def detalle_ticket_soporte(ticket_id):
    if current_user.rol_id not in [ROL_ADMIN_ID, ROL_SOPORTE_ID]:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('main.mis_tickets'))
        
    # Cargar el ticket, su creador y todas sus respuestas asociadas
    ticket = Ticket.query.options(
        joinedload(Ticket.creador)
    ).filter(Ticket.ticket_id == ticket_id).first_or_404()

    # Si es POST, es para enviar una respuesta o cambiar el estado
    if request.method == 'POST':
        mensaje = request.form.get('mensaje_respuesta')
        nuevo_estado = request.form.get('nuevo_estado')
        
        try:
            #Guardar Nueva Respuesta
            if mensaje:
                nueva_respuesta = RespuestaTicket(
                    mensaje=mensaje,
                    ticket_id=ticket.ticket_id,
                    usuario_id=current_user.usuario_id)
                db.session.add(nueva_respuesta)
                
                # Actualizar el estado del ticket a 'En Progreso' si está 'Abierto' 
                if ticket.estado == 'Abierto' and ticket.asignado_a_id == current_user.usuario_id:
                    ticket.estado = 'En Progreso'
                    flash('Respuesta enviada. El ticket fue puesto En Progreso.', 'success')
                else:
                    flash('Respuesta enviada.', 'success')
            # Cambiar el Estado del Ticket (si se envió un nuevo estado)
            if nuevo_estado and nuevo_estado != ticket.estado:
                # Log de la acción de cambio de estado
                estado_log = RespuestaTicket(
                    mensaje=f"[LOG] Estado cambiado de '{ticket.estado}' a '{nuevo_estado}' por {current_user.nombre}.",
                    ticket_id=ticket.ticket_id,
                    usuario_id=current_user.usuario_id,
                    fecha_creacion=datetime.utcnow())
                db.session.add(estado_log)
                ticket.estado = nuevo_estado
            flash(f'Estado del ticket cambiado a {nuevo_estado}.', 'info')

            # Actualizar la fecha de actualización si hubo cambios
            ticket.fecha_actualizacion = datetime.utcnow()
            db.session.commit()
            # Redirigir para evitar reenvío del formulario
            return redirect(url_for('main.detalle_ticket_soporte', ticket_id=ticket.ticket_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al procesar la gestión: {e}', 'danger')


    # Asegurarse de que el ticket esté asignado al usuario actual si no lo está
    if ticket.asignado_a_id is None:
        # Aquí se podría poner la lógica de asignación automática, pero lo dejaremos manual (Tomar Ticket)
        pass 
        
    respuestas_lista = ticket.respuestas.options(
        joinedload(RespuestaTicket.autor)
    ).order_by(RespuestaTicket.fecha_creacion.asc()).all()

    return render_template('soporte_gestion.html', 
                            ticket=ticket, 
                            respuestas=respuestas_lista, 
                            estados_disponibles=['Abierto', 'En Progreso', 'Pendiente de Usuario', 'Cerrado'],
                            title=f'Gestionar Ticket #{ticket.ticket_id}')

@main.route("/soporte/asignar_a_mi/<int:ticket_id>", methods=['POST'])
@login_required
def asignar_a_mi(ticket_id):
    if current_user.rol_id not in [ROL_ADMIN_ID, ROL_SOPORTE_ID]:
        flash('Acceso denegado. Se requiere rol de Soporte o Administrador.', 'danger')
        return redirect(url_for('main.soporte_panel'))

    ticket = Ticket.query.get_or_404(ticket_id)

    # Solo se puede tomar si está sin asignar o asignado a otro
    if ticket.asignado_a_id is not None and ticket.asignado_a_id == current_user.usuario_id:
        flash('El ticket ya está asignado a ti.', 'info')
        return redirect(url_for('main.soporte_panel'))
        
    try:
        # Asignar el ticket al usuario actual
        ticket.asignado_a_id = current_user.usuario_id
        ticket.estado = 'En Progreso'
        ticket.fecha_actualizacion = datetime.utcnow()
        
        # Registrar la acción en el historial
        respuesta_log = RespuestaTicket(
            mensaje=f"[LOG] Ticket asignado a {current_user.nombre} {current_user.apellido} y cambiado a En Progreso.",
            ticket_id=ticket.ticket_id,
            usuario_id=current_user.usuario_id,
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(respuesta_log)

        db.session.commit()
        flash(f'Ticket #{ticket.ticket_id} asignado a ti y puesto En Progreso.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ocurrió un error al intentar asignar el ticket: {e}', 'danger')
        
    return redirect(url_for('main.soporte_panel'))