from flask import render_template
from flask_login import login_required
from app.models import Destino
from . import main

@main.route('/mapa_destinos')
@login_required 
def mapa_destinos():
    # Obtener todos los objetos Destino
    destinos_objetos = Destino.query.all()
    
    # Serialización: Convertir la lista de objetos a una lista de diccionarios
    destinos_serializados = [d.to_dict() for d in destinos_objetos]
    
    # Pasa la lista serializada a la plantilla
    return render_template(
        'mapa_destinos.html', 
        title='Mapa de Destinos', 
        destinos=destinos_serializados
    )