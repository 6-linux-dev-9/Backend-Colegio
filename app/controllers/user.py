from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt
from marshmallow import ValidationError
from app.config import cloudinary
from cloudinary.uploader import destroy
from app.controllers.auth import obtener_ip
from app.errors.errors import GenericError
from app.models import BitacoraUsuario, Rol, Usuario
from http import HTTPStatus
from app.database import db
from app.schemas.auth_schema_body import AuthAdminRegisterSchema, AuthAdminUpdateSchema
from app.schemas.pagination_shema import PaginatedResponseT
from app.schemas.schemas import UsuarioImageSchema, UsuarioSchema
from app.schemas.user_schema_body import UserAdminPasswordRequest, UserEditRequest, UserPasswordRequest
from app.utils.enums.enums import Sesion
from app.utils.image_utils import UBICACION_PERFIL_USUARIO, comprimir_imagen, extension_permitida
from PIL import Image
#from app.schemas.schemas import UsuarioSchema



bcrypt = Bcrypt()
usuario_bp = Blueprint('usuario', __name__)


@usuario_bp.route('/test',methods = ["GET"])
def testing():
    id = autenticated_user_id()
    return jsonify({"message": "User created successfully",
                    "Persona":{
                        "id":2,
                        "nombre":f"fernando {id}"
                    }}), 201




@usuario_bp.route('/me',methods=["GET"])
@jwt_required()
#es posible usarlo el id
def autenticated_user_id():
    current_user = get_jwt_identity() #obtiene el id del usuario autenticado
    print(current_user)
    return jsonify({
        "message":"sexo"
    }),200


#solamente ingresa el password para resetear la contrasenia

@usuario_bp.route('/change-password',methods=["PUT"])
@jwt_required()
def change_password():
    try:
        idUsuarioAutenticado = get_jwt_identity()
        usuario = Usuario.query.get(idUsuarioAutenticado)
        if not usuario:
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado..")
        body = request.get_json()
        print(body)
        schema = UserPasswordRequest()
        if schema.validate(body):
            raise ValidationError("Hubo un error al momento de validar los datos...")
        
        data = schema.load(body)
        print(f"data: {data}")

        if not bcrypt.check_password_hash(usuario.password,data["anterior_password"]):
            raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.phrase,"Error..La contraseña ingresada no es su contraseña actual")
        
        #si en el caso de que no cuadren sus password,quiere decir que el usuario cambio de contra
        # if not bcrypt.check_password_hash(usuario.password,data["password_2"]):
        #actualizamos su contrasenia
        #usuario.password = bcrypt.generate_password_hash(data["nueva_password"]).decode('utf-8')

        usuario.password = genera_password(data["nueva_password"],usuario.password)
        bitacora_usuario = BitacoraUsuario(
            ip = obtener_ip(),
            username = usuario.username,
            tipo_accion = Sesion.ACTUALIZACION_PASSWORD._value_[0],
        )
        db.session.add(bitacora_usuario)
        #si no, quiere decir que no la cambio
        db.session.commit()
        return jsonify({
            "message":"Password Cambiada con Exito!"
        })
    except GenericError :
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,str(e))



@usuario_bp.route('/edit',methods=["PUT"])
@jwt_required()
def editAtributtes():
    try:
        idUsuarioAutenticado = get_jwt_identity()
        usuario = Usuario.query.get(idUsuarioAutenticado)
        if not usuario:
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado..")
        body = request.get_json()
        schema = UserEditRequest()
        if schema.validate(body):
            raise ValidationError("Error...Formato de datos no valido...")
        data = schema.load(body)

        usuario.username = data["username"]
        usuario.nombre = data["nombre"]

        validar_ci_y_email(usuario,data["email"],data["ci"])

        usuario.email = data["email"]
        usuario.ci = data["ci"]

        bitacora_usuario = BitacoraUsuario(
            ip = obtener_ip(),
            username = usuario.username,
            tipo_accion = Sesion.ACTUALIZACION_DATA._value_[0],
        )
        db.session.add(bitacora_usuario)
        db.session.commit()
        return jsonify({
            "message":"campos modificados con exito!",
            "usuario":UsuarioSchema().dump(usuario)
            })
    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,f"Error..algo salio mal..{str(e)}")

def validar_ci_y_email(usuario,email,ci):
    if usuario.email != email :
        email_user = Usuario.query.filter_by(email=email).first() 
        if email_user : 
            raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.phrase,"Error.. ya existe un usuario con esta direccion de correo..")
    if usuario.ci != ci :
        ci_user = Usuario.query.filter_by(ci=ci).first() 
        if ci_user : 
            raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.phrase,"Error.. ya existe un usuario con este CI..")
    



@usuario_bp.route("/list-paginate",methods=["GET","OPTIONS"])
def get_list_usuario():
    rol = Rol.query.filter_by(nombre = "ADMINISTRADOR").first()
    query = Usuario.query.order_by(Usuario.rol_id) if not rol else Usuario.query.filter(Usuario.rol_id != rol.id).order_by(Usuario.rol_id) 
    return PaginatedResponseT.paginate(query,UsuarioSchema)


@usuario_bp.route("/debug-usuarios")
def debug_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([u.username for u in usuarios])


#faltaria el de editar perfil

def comparacion_peso():
    if 'imagen' not in request.files:
        raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.phrase,"Error.. Hubo un error en el tipo de imagen..")
    imagen = request.files["imagen"]

    if not extension_permitida(imagen.filename):
        raise GenericError(...)
    #test de peso

    # Leer imagen original con PIL
    imagen_original = Image.open(imagen)
    imagen.seek(0)  # Resetear puntero porque fue leído por PIL

    peso_original = len(imagen.read())
    ancho_original, alto_original = imagen_original.size
    formato_original = imagen_original.format
    modo_original = imagen_original.mode

    imagen.seek(0)  # Volver a colocar puntero al inicio antes de comprimir

    # Comprimir imagen
    imagen_comprimida = comprimir_imagen(imagen, calidad=80, max_ancho=800)


     # Leer imagen comprimida para comparación
    imagen_comp = Image.open(imagen_comprimida)
    peso_comprimido = imagen_comprimida.getbuffer().nbytes
    ancho_comp, alto_comp = imagen_comp.size
    formato_comp = imagen_comp.format  # Probablemente sea None si no se guarda con formato
    modo_comp = imagen_comp.mode
    # Debug: comparación antes de subir
    print("📷 Comparación imagen:")
    print(f"Peso original:     {peso_original / 1024:.2f} KB")
    print(f"Peso comprimido:   {peso_comprimido / 1024:.2f} KB")
    print(f"Dimensiones:       {ancho_original}x{alto_original} → {ancho_comp}x{alto_comp}")
    print(f"Formato:           {formato_original} → {formato_comp}")
    print(f"Modo de color:     {modo_original} → {modo_comp}")
    return jsonify({
        "message":"Ok"
    })

    # try:
    #     resultado = cloudinary.upload(
    #         imagen_comprimida,
    #         folders="usuario/perfil",
    #         use_filename=True,
    #         #overwrite=False ni idea pa que
    #         #unique_filename=True ni idea pa que
    #     )
    #     return jsonify({
    #         "url": resultado["secure_url"],
    #         "public_id": resultado["public_id"]
    #     }), 200
    # except GenericError:
    #     db.session.rollback()
    #     raise
    # except Exception as e:
    #     db.session.rollback()
    #     raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,f"Error..algo salio mal..{str(e)}")




@usuario_bp.route('/upload-profile-photo',methods=["POST"])
@jwt_required()
def subir_foto_perfil():
    id_authenticated_user = get_jwt_identity()
    usuario = Usuario.query.get(id_authenticated_user)
    if not usuario:
        raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado..")   
    if 'imagen' not in request.files:
        raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.phrase,"Error.. Hubo un error en el tipo de imagen..")
    imagen = request.files["imagen"] #extraigo la imagen del request
    
    #si el usuario ya tiene una foto de perfil asignada, la elimino
    if usuario.url_profile:
        eliminar_imagen_fisica(usuario.url_profile) #borra a nivel cloudinary


    #POR DEFECTO EL REQUEST.FILES DEBE SER COMO IMAGEN
    resultado = crear_imagen_cloudinary(imagen,UBICACION_PERFIL_USUARIO)
    try:  
        usuario.url_profile = resultado["public_id"]
        bitacora_usuario = BitacoraUsuario(
                ip = obtener_ip(),
                username = usuario.username,
                tipo_accion = Sesion.ACTUALIZACION_PERFIL._value_[0],
        )
        db.session.add(bitacora_usuario)
        db.session.commit()
        print("commit de imagen con exito")
        return jsonify({
            "usuario":UsuarioImageSchema().dump(usuario),
            "message":"Foto de Perfil cambiada con exito!"
        })
       
    except GenericError:
        print("Error generic")
        db.session.rollback()
        raise
    except Exception as e:
        print("Error Exception")
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,f"Error..algo salio mal..{str(e)}")


def crear_imagen_cloudinary(imagen,folder_a_guardar):

    if not extension_permitida(imagen.filename):
        raise GenericError(...)
    
    # Comprimir imagen
    imagen_comprimida = comprimir_imagen(imagen, calidad=80, max_ancho=800)

    try:
        #agrega la nueva imagen de perfil
        resultado = cloudinary.upload(
             imagen_comprimida,
            folder=folder_a_guardar,
            use_filename=True,
            #overwrite=False ni idea pa que
            unique_filename=True #ni idea pa que
        )
        return resultado
    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,f"Error..algo salio mal..{str(e)}")

#eliminar la imagen a nivel fisico 
def eliminar_imagen_fisica(public_id):
    destroy(public_id)







#metodos para usuario administrativo
@usuario_bp.route('/create',methods=["POST"])
def create_user():

    #antes de hacer toda esta macana y de cualquier otro metodo podria hacer la pregunta de 
    #obtener al usuario autenticado y preguntar si es administrador y ver si tiene permisos

    try:
    #agarro los datos del body

        body = request.get_json()
        schema = AuthAdminRegisterSchema()
        if schema.validate(body):#si lanza errores
            raise ValidationError("Hubo un error en la validacion de datos..")
        #con datos ya validados
        data = schema.load(body)


        rol = Rol.query.get(data["rol_id"])

        usuario = Usuario.query.filter_by(email=data["email"]).first()
        if usuario: 
            raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.phrase,"Error..El usuario ya esta registrado en el sistema..")
        
        if not rol:
            raise GenericError(HTTPStatus.NOT_FOUND,HTTPStatus.NOT_FOUND.phrase,"Error Rol no encontrado..")
        
        nuevo_usuario = Usuario(
            nombre = data["nombre"],
            username = data["nombre"].strip().split()[0].capitalize(),#del campo nombre
            email = data["email"],
            password = bcrypt.generate_password_hash(data["password"]).decode('utf-8'),
            rol_id = rol.id
        )
        schema_response = UsuarioSchema()
        db.session.add(nuevo_usuario)

        bitacora_usuario = BitacoraUsuario(
            ip = obtener_ip(),         
            username = nuevo_usuario.username,
            tipo_accion = Sesion.LOGIN._value_[0],
        )
        db.session.add(bitacora_usuario)
        
        db.session.commit()
        response = schema_response.dump(nuevo_usuario)
        return jsonify({"usuario": response, "message":"usuario creado con exito!"}),HTTPStatus.CREATED
        
    except GenericError:
        db.session.rollback()
        raise  # Relanza GenericError para que lo maneje @app.errorhandler
    except Exception as e:# aunque no se si esto funcione
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR.phrase, str(e))  # Solo errores inesperados

@usuario_bp.route('/<int:id>/update',methods=["PUT"])
def edit_user_for_admin(id):
    try:
        usuario = Usuario.query.get(id)
        if not usuario:
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado..")
        body = request.get_json()
        schema = AuthAdminUpdateSchema()
        if schema.validate(body):
            raise ValidationError("Error...Formato de datos no valido...")
        data = schema.load(body)

        usuario.username = data.get("username")
        usuario.nombre = data["nombre"]
        usuario.email = data["email"]
        usuario.rol_id = data["rol_id"]
        #si la contrasenia no es vacio
        if data.get("password") != "":
            usuario.password = genera_password(data["password"],usuario.password)    
        

        bitacora_usuario = BitacoraUsuario(
            ip = obtener_ip(),
            username = usuario.username,
            tipo_accion = Sesion.ACTUALIZACION_DATA._value_[0],
        )
        db.session.add(bitacora_usuario)
        db.session.commit()
        return jsonify({
            "message":"campos modificados con exito!",
            "usuario":UsuarioSchema().dump(usuario)
            })
    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,f"Error..algo salio mal..{str(e)}")




#generame una nueva contrasenia si la contrasenia cambio
#pero si la contrasenia se mantiene constante no generes una nueva,solo usa la contrasenia que ya estaba en la db
def genera_password(password_request,password_db):
    return bcrypt.generate_password_hash(password_request).decode('utf-8') if not bcrypt.check_password_hash(password_db,password_request) else password_db 



@usuario_bp.route('/<int:id>/get',methods=["GET"])
def get_user_for_admin(id):
    try:
        usuario = Usuario.query.get(id)
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
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,f"Error..algo salio mal..{str(e)}")

@usuario_bp.route('/<int:id>/delete',methods=["DELETE"])
def delete_user_for_admin(id):
    try:
        #quizas hacer el borrado logico y ya
        usuario = Usuario.query.get(id)
        if not usuario:
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado..")
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({
            "message":"usuario eliminado con exito!"
            })
    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,f"Error..algo salio mal..{str(e)}")

@usuario_bp.route('/<int:id>/change-password',methods=["PUT"])
def admin_change_password(id):
    try:

        body = request.get_json()
        schema = UserAdminPasswordRequest()
        if schema.validate(body):
            raise GenericError(GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado.."))
        data = schema.load(body)
        usuario = Usuario.query.get(id)
        if not usuario:
            raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado..")
        usuario.password = genera_password(data["nueva_password"],usuario.password)

        bitacora_usuario = BitacoraUsuario(
                ip = obtener_ip(),
                username = usuario.username,
                tipo_accion = Sesion.ACTUALIZACION_PASSWORD._value_[0],
        )
        db.session.add(bitacora_usuario)
        db.session.commit()
        return jsonify({
            "message":"contrasenia cambiada con exito!"
            })
    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,f"Error..algo salio mal..{str(e)}")


@usuario_bp.route('/<int:id>/update-profile',methods=["PUT"])
def admin_change_profile(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        raise GenericError(HTTPStatus.UNAUTHORIZED,HTTPStatus.UNAUTHORIZED.phrase,"Error.. usuario no autenticado..")   
    if 'imagen' not in request.files:
        raise GenericError(HTTPStatus.BAD_REQUEST,HTTPStatus.BAD_REQUEST.phrase,"Error.. Hubo un error en el tipo de imagen..")
    imagen = request.files["imagen"] #extraigo la imagen del request
    
    #si el usuario ya tiene una foto de perfil asignada, la elimino
    if usuario.url_profile:
        eliminar_imagen_fisica(usuario.url_profile) #borra a nivel cloudinary


    #POR DEFECTO EL REQUEST.FILES DEBE SER COMO IMAGEN
    resultado = crear_imagen_cloudinary(imagen,UBICACION_PERFIL_USUARIO)
    try:  
        usuario.url_profile = resultado["public_id"]
        bitacora_usuario = BitacoraUsuario(
                ip = obtener_ip(),
                username = usuario.username,
                tipo_accion = Sesion.ACTUALIZACION_PERFIL._value_[0],
        )
        db.session.add(bitacora_usuario)
        db.session.commit()
        return jsonify({
           "usuario":UsuarioImageSchema().dump(usuario),
            "message":"Foto de Perfil cambiada con exito!"
        })
       
    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR,HTTPStatus.INTERNAL_SERVER_ERROR.phrase,f"Error..algo salio mal..{str(e)}")