from flask import render_template
from flask_login import login_required
from werkzeug.exceptions import abort
from app.utils import admin_required
from app.models import Cotizacion
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
