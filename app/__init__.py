# importa de app/database el metodo init_db
# se dispara el init de database
from flask_marshmallow import Marshmallow

from app.database import init_db
from flask import Flask
#from flask_bcrypt import Bcrypt
from app.config.config import Config
from flask_jwt_extended import JWTManager
from app.controllers.auth import bcrypt
#no se de donde lo importa pero yo le creo
from dotenv import load_dotenv
#importamos para hacer uso de los handler
from app.errors.errors import registrar_error_handler 
from app.errors.errors import registrar_jwt_handlers

#importa de controllers el auth, es decir todos los metodos de auth
from app.routers.index import api_bp 
from flask_cors import CORS

from app.seeders.main_seeder import seed_all_seeder_command
from commands import seed_alumnos_command, seed_curso_gestion_command, seed_curso_gestion_materia_command, seed_cursos_command, seed_docentes_command, seed_gestiones_command, seed_materias_command




#
# Cargar variables de entorno del .env al sistema parece
#o con source .env 
load_dotenv()

#se inicializa el hashing de contrasenias
# bcrypt = Bcrypt()
#se inicializa para manejar la creacion de tokens JWT
jwt = JWTManager()
ma = Marshmallow()
def create_app():

    

    app = Flask(__name__)

    # Cargar configuración desde config.py
    #con esto cargamos la configuracion que esta en app/config/config/Config 
    app.config.from_object(Config)

    # inicizamos la bd y las migraciones que estan en database/__init__
    init_db(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    

    ma.init_app(app)


    # Configuración de CORS (aquí es donde debes ponerlo)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5174", "http://127.0.0.1:5174","http://localhost:5173", "http://127.0.0.1:5173"],
            # "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True  # Descomenta si usas cookies
        }
    },supports_credentials=True)

    # Registrar Blueprints
    app.register_blueprint(api_bp, url_prefix="/api")

    registrar_jwt_handlers(jwt)
    #registrar el handler
    registrar_error_handler(app)
    
    #registrar seeders

  
    app.cli.add_command(seed_alumnos_command)
    app.cli.add_command(seed_docentes_command)
    app.cli.add_command(seed_cursos_command)
    app.cli.add_command(seed_gestiones_command)
    app.cli.add_command(seed_materias_command)
    app.cli.add_command(seed_all_seeder_command)
    app.cli.add_command(seed_curso_gestion_command)
    app.cli.add_command(seed_curso_gestion_materia_command)
    # upgrade()
    # seed_all_seeders_command()
    return app
