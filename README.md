# Descripción
Aplicación que permite a los usuarios compartir, descubrir y debatir sobre destinos turísticos en la provincia de Córdoba. Orientada a un público avido por descubrir nuevos destinos deslumbrantes.

# Requisitos 
1. **Python 3.8+** instalado en tu sistema
2. **Postresql** también instalado en el sistema.
3. **Git** para clonar el repositorio desde GitHub.

# Configuración inicial
### Clonar la aplicacion desde GitHub
	git clone https://github.com/nachoPaviot/ExploraCordoba.git

### Crear entorno virtual de Flask 
    python -m venv venv

### Activar el entorno virtual de Flask
- **En Windows:** 
	tu directorio raíz\venv\Scripts\activate
- **En Linux/macOS:** 
	source venv/bin/activate

### Instalar dependecias
	pip install -r requerimientos.txt

## Configuración para correr la aplicación
### Setear la variable de inicio
- **En Windows:** 
	set FLASK_APP=app
- **En Linux/macOS:** 
	export FLASK_APP=app

### Correr el servidor
	flask run
La aplicación estará disponible [aquí](http://127.0.0.1:5000/)
    
# Comandos CLI
**Nota:** *estos comandos sirve para crear las tablas en la base de datos y datos de prueba. Funcionan únicamente cuando se configuran las credenciales en el propio entorno local para acceder a la BD.*

### Crear la base de datos
	flask crear_db 

### Crear datos de prueba en la Base de Datos
	flask sembrar_db

### Usuarios de prueba
1. Usuario: **turista@prueba.com** Contraseña: **turista**
2. Usuario: **admin@prueba.com** Contraseña: **admin**