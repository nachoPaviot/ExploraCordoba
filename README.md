#Requisitos
1.Python 3.8+ instalado en tu sistema.
2-Postresql también instalado en el sistema.
3.Git para clonar el repositorio desde GitHub.

#Crear entorno virtual de Flask
	**python -m venv venv**

#Activar el entorno virtual de Flask.
	en Windows: *'directorio raíz'\venv\Scripts\activate*
	en Linux/macOS: *source venv/bin/activate*

#Clonar la aplicacion desde GitHub.
	*git clone* [(https://github.com/nachoPaviot/ExploraCordoba.git)]

#Instalar dependecias desde el directorio raíz.
	*pip install -r requirements.txt*

#Setear la variable desde donde se debe iniciar la aplicación. Hay que estar en #el directorio raíz y lanzar el comando.
	en Windows: *set FLASK_APP=app.app*
	en Linux/macOS: *export FLASK_APP=app.app*
    
#Se implementaron comandos CLI de Flask en la aplicación para crear las tablas en la base de datos y datos de prueba.

##Crear la base de datos: 
	*flask crear_db*

##Crear datos de prueba en la Base de Datos:
	*flask sembrar_db*

##Correr el servidor.
La aplicación estará disponible en http://127.0.0.1:5000/
	*flask run*