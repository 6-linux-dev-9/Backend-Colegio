from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.controllers.auth import obtener_ip
from app.database import db
from flask_bcrypt import Bcrypt
from http import HTTPStatus

from app.errors.errors import GenericError, InternalServerException
from app.models import BitacoraUsuario, Docente, Rol, Usuario
from app.schemas.Docente_Schema import DocenteRegisterSchema
from app.schemas.pagination_shema import PaginatedResponseT
from app.schemas.schemas import DocenteSchema
from app.utils.enums.entidad import RolesEnum
from app.utils.enums.enums import Sesion
bcrypt = Bcrypt()


docente_bp = Blueprint("docente",__name__)
@docente_bp.route('/registrar',methods=["POST"])
def registrar_docente():
    try:
        body = request.get_json()
        schema = DocenteRegisterSchema()
        if schema.validate(body): 
            raise ValidationError("Hubo un error en la validacion de datos")
        
        data = schema.load(body)
        usuario = Usuario.query.filter_by(ci=data["ci"]).first()

        if usuario:
            raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.value,"Error..el usuario ya esta registrado en el sistema")
        rol = Rol.query.filter_by(nombre = RolesEnum.DOCENTE).first()

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
        docente = Docente(
            id = nuevo_usuario.id,
        )
        db.session.add(docente)
        bitacora_usuario = BitacoraUsuario(
            ip = obtener_ip(),
            username = nuevo_usuario.username,
            tipo_accion = Sesion.REGISTRO_DE_USUARIO._value_[0],
        )
        db.session.add(bitacora_usuario)
        db.session.commit()
        return jsonify({"docente":DocenteSchema().dump(docente)})
    except GenericError:
        db.session.rollback()
        raise  # Relanza GenericError para que lo maneje @app.errorhandler
    except Exception as e:# aunque no se si esto funcione
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR.phrase, str(e))  # Solo errores inesperados
    
@docente_bp.route('/list-paginate',methods=["GET"])
def get_paginated_docentes():    
    try:
        return PaginatedResponseT.paginate(Docente.query,DocenteSchema)
    except Exception as e:
        raise InternalServerException(f"ocurrio un error inesperado ${str(e)}")