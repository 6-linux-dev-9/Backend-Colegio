from datetime import timedelta
from http import HTTPStatus 
# from app import bcrypt 

from flask_bcrypt import Bcrypt
from flask import Blueprint, request, jsonify
# from flask_cors import cross_origin
from marshmallow import ValidationError #usaremos el request para acceder al request, jsonify para usar respuestas json
from app.errors.errors import GenericError
from app.models import BitacoraUsuario, Usuario #hacemos referencia al modelo usuario por a ese modelo consultaremos
from app.database import db  #usaremos la instancia a la base de datos
#from app.utils.jwt_utils import encode_auth_token #esto no es tan necesario
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.schemas.auth_schema_body import AuthLoginSchemaBody   #usamos un esquema de validacion de tipos
from app.schemas.schemas import  UsuarioSchema
from app.utils.enums.enums import Sesion
#data = request.get_json() #recojemos los datos del body
#return jsonify({"message": "User created successfully"}), 201  SE FORMA UNA RESPUESTA
bcrypt = Bcrypt()

auth_bp = Blueprint('auth', __name__) #por defecto se nombra un blueprint 

# @auth_bp.route('/registrar', methods=['POST']) #se empieza por el nombre del blueprint.route('tu ruta',methods=['GET,POST,LOQUE SEA'])
# #metodo
# def register():
#     try:
#         #agarro los datos del body
#         body = request.get_json()
#         schema = AuthRegisterSchemaBody()
#         if schema.validate(body):#si lanza errores
#             raise ValidationError("Hubo un error en la validacion de datos..")
#         #con datos ya validados
#         data = schema.load(body)
        
#         usuario = Usuario.query.filter_by(email=data["email"]).first()
#         if usuario: 
#             raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.phrase,"Error..El usuario ya esta registrado en el sistema..")
#         rol = Rol.query.filter_by(nombre = "ADMINISTRADOR").first()

#         if not rol:
#             raise GenericError(HTTPStatus.NOT_FOUND,HTTPStatus.NOT_FOUND.phrase,"Error Rol no encontrado..")
        
#         nuevo_usuario = Usuario(
#             nombre = data["nombre"],
#             username = data["nombre"].strip().split()[0].capitalize(),#del campo nombre
#             email = data["email"],
#             password = bcrypt.generate_password_hash(data["password"]).decode('utf-8'),
#             rol_id = rol.id,
#             #ci = data["ci"]
#         )
#         schema_response = UsuarioSchema()
#         db.session.add(nuevo_usuario)

#         bitacora_usuario = BitacoraUsuario(
#             ip = obtener_ip(),
#             username = nuevo_usuario.username,
#             tipo_accion = Sesion.REGISTRO_DE_USUARIO._value_[0],
#         )
#         db.session.add(bitacora_usuario)
        
#         db.session.commit()
#         response = schema_response.dump(nuevo_usuario)
#         return jsonify({"usuario": response}),HTTPStatus.CREATED
        
#     except GenericError:
#         db.session.rollback()
#         raise  # Relanza GenericError para que lo maneje @app.errorhandler
#     except Exception as e:# aunque no se si esto funcione
#         db.session.rollback()
#         raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR.phrase, str(e))  # Solo errores inesperados


@auth_bp.route("/login",methods=["POST"])
def login():
    try:
        body = request.get_json()
        schema = AuthLoginSchemaBody()
        if schema.validate(body):
            raise ValidationError("Hubo un error al validar los datos...")
        
        data = schema.load(body)
        print(data)
        #los datos son validos,por lo tanto
        #comparamos las contrasenias 
        usuario_db = buscar_usuario_por_correo_y_ci(data["email"])
        #if not bcrypt.check_password_hash(usuario_db.password,data["password"]):

        #si esta el usuario en el sistema,debemos comparar su contrasenia
        if not bcrypt.check_password_hash(usuario_db.password,data["password"]):
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error...credenciales no validas..")
        
        if usuario_db.is_deleted:
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error..Usuario no autorizado..")
        
        #si es email valido y la contrasenia es la correcta
        token = create_access_token(identity=str(usuario_db.id),expires_delta=timedelta(hours=1))        
        # bitacora_usuario = BitacoraUsuario(
        #     ip = obtener_ip(),
        #     username = usuario_db.username,
        #     tipo_accion = Sesion.LOGIN._value_[0],
        # )
        # db.session.add(bitacora_usuario)
        #para no poblar mucho la bitacora
        db.session.commit()
        # print(BitacoraUsuarioSchema().dump(bitacora_usuario))
        return jsonify({
            "message": f"Bienvenido Usuario {usuario_db.username}",
            "token":token,
            "usuario":UsuarioSchema().dump(usuario_db)
        })
    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,str(e))

def buscar_usuario_por_correo_y_ci(email):
    usuario_db = Usuario.query.filter_by(email = email).first()
    #si el usuario no lo encuentra por correo lo deberia poder encontrar por ci
    if not usuario_db:
        usuario_db = Usuario.query.filter_by(ci =email).first()
        if not usuario_db:
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error...credenciales no validas..")    
    return usuario_db


def obtener_ip():
    return request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr

#@cross_origin
@auth_bp.route('/me',methods=["GET"])
@jwt_required()
def getAuthenticated_user():
    try:
        idUsuarioAutenticado = get_jwt_identity()
        usuario = Usuario.query.get(idUsuarioAutenticado)
        if not usuario:
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado..")
        return jsonify({
            "usuario":UsuarioSchema().dump(usuario)
        })
    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,str(e))


@auth_bp.route('/logout',methods=["POST"])
@jwt_required()
def logout():
    try:
        idUsuarioAutenticado = get_jwt_identity()
        usuario = Usuario.query.get(idUsuarioAutenticado)
        if not usuario:
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado..")
        bitacora_usuario = BitacoraUsuario(
            ip = obtener_ip(),
            username = usuario.username,
            tipo_accion = Sesion.LOGOUT._value_[0],
        )      
        db.session.add(bitacora_usuario)
        db.session.commit()
        return jsonify({
            "message":"logout exitoso"
        })
    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,str(e))


