from flask import Blueprint

main = Blueprint('main', __name__) 

from . import general_routes
from . import foro_routes
from . import admin_routes
from . import destinos_routes
from . import cotizador_routes
from . import proveedor_routes