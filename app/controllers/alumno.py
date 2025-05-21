
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from flask_bcrypt import Bcrypt
from http import HTTPStatus
from app.controllers.auth import obtener_ip
from app.errors.errors import GenericError
from app.models import Alumno, BitacoraUsuario, Rol, Usuario
from app.schemas.alumno_schema import AlumnoInscripcionSchema
from app.schemas.schemas import AlumnoSchema
from app.utils.enums.enums import Sesion
from app.database import db

bcrypt = Bcrypt()
alumno_bp = Blueprint('alumno',__name__)

#buscar por ci
#solo para registrar,ya luego se debe modificar por que el metodo debe recibir el curso donde se va registrar el muchacho
@alumno_bp.route('/inscribir',methods=['POST'])
def inscribir_alumno():
    try:
        body = request.get_json()
        schema = AlumnoInscripcionSchema()
        if schema.validate(body): 
            raise ValidationError("Hubo un error en la validacion de datos")
        data = schema.load(body)
        usuario = Usuario.query.filter_by(ci=data["ci"]).first()

        if usuario:
            raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.value,"Error..el usuario ya esta registrado en el sistema")
        rol = Rol.query.filter_by(nombre = "ALUMNO").first()

        if not rol:
            raise GenericError(HTTPStatus.NOT_FOUND,HTTPStatus.NOT_FOUND.phrase,"Error Rol no encontrado..")
        
        nuevo_usuario = Usuario(
            nombre = data["nombre"],
            username = data["nombre"].strip().split()[0].capitalize(),#del campo nombre
            email = data.get("email"),
            password = bcrypt.generate_password_hash(data["password"]).decode('utf-8'),
            rol_id = rol.id,
            ci = data["ci"]
        )
        db.session.add(nuevo_usuario)
        db.session.flush()
        alumno = Alumno(
            id = nuevo_usuario.id,
            rude = data["rude"]
        )
        db.session.add(alumno)
        bitacora_usuario = BitacoraUsuario(
            ip = obtener_ip(),
            username = nuevo_usuario.username,
            tipo_accion = Sesion.REGISTRO_DE_USUARIO._value_[0],
        )
        db.session.add(bitacora_usuario)
        db.session.commit()
        return jsonify({"alumno":AlumnoSchema().dump(alumno)})
    except GenericError:
        db.session.rollback()
        raise  # Relanza GenericError para que lo maneje @app.errorhandler
    except Exception as e:# aunque no se si esto funcione
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR.phrase, str(e))  # Solo errores inesperados

    
