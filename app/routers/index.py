from flask import Blueprint
from app.controllers.auth import auth_bp  # Ya vimos este
from app.controllers.user import usuario_bp  # Ejemplo de otro Blueprint
from app.controllers.rol import rol_bp
from app.controllers.permiso import permiso_bp
from app.controllers.bitacora_usuario import bitacora_bp
from app.controllers.alumno import alumno_bp
from app.controllers.docente import docente_bp
from app.controllers.gestion import gestion_bp
from app.controllers.curso import curso_bp
from app.controllers.materia import materia_bp
api_bp = Blueprint('api', __name__)

# Registrar Blueprints con prefijos

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(usuario_bp, url_prefix='/usuarios')
api_bp.register_blueprint(rol_bp, url_prefix='/rol')
api_bp.register_blueprint(permiso_bp, url_prefix='/permisos')
api_bp.register_blueprint(bitacora_bp,url_prefix='/bitacoras-usuarios')
api_bp.register_blueprint(alumno_bp,url_prefix='/alumnos')
api_bp.register_blueprint(docente_bp,url_prefix='/docentes')
api_bp.register_blueprint(gestion_bp,url_prefix='/gestiones')
api_bp.register_blueprint(curso_bp,url_prefix='/cursos')
api_bp.register_blueprint(materia_bp,url_prefix='/materias')