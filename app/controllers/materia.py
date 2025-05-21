


from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.database import db
from app.errors.errors import  GenericError, InternalServerException, NotFoundException
from app.models import Materia
from app.schemas.materias_schema import MateriaRequestSchema, MateriaUpdateSchema
from app.schemas.pagination_shema import PaginatedResponseT
from app.schemas.schemas import MateriaSchema
from app.utils.enums.enums import EstadoGeneral



materia_bp = Blueprint('materia',__name__)
@materia_bp.route('/create',methods=["POST"])
def registrar_materia():
    try:
        #recibimos los datos
        body = request.get_json()
        print(f"body = {body}")
        schema = MateriaRequestSchema()
        if schema.validate(body): #si hay errores
            raise ValidationError("Hubo un error en la validacion de datos..")
        #ya validado los datos
        data = schema.load(body) #ya es JSON
        print(f"data: {data}")
        nueva_materia = Materia(
            nombre = data["nombre"],
        )    
        #insertamos en la bd
        db.session.add(nueva_materia)
        db.session.commit()
        #para serializar la respuesta
        schema_response = MateriaSchema()
        response = schema_response.dump(nueva_materia)
        #agregamos un mensaje,solamente para probar
        return jsonify({
            "message": "materia creada exitosamente",  # Mensaje adicional
            "materia": response  # Los datos del rol creado
        })
    #tira un 200 aunque no lo definamos
        
    except GenericError:
        db.session.rollback()
        raise  # Relanza GenericError para que lo maneje @app.errorhandler
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error ocurrio un error inesperado..{str(e)}")

@materia_bp.route('/list-paginate',methods = ["GET"])
def list_paginate_materias():
    try:
        return PaginatedResponseT.paginate(Materia.query,MateriaSchema)        

    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error ocurrio un error inesperado..{str(e)}")




@materia_bp.route('/<int:id>/get', methods=["GET"])
def get_materia(id):
    try:
        materia = Materia.query.get(id)
        if not materia:
            raise NotFoundException("Error..materia no encontrada..")

        return jsonify({
            "materia": MateriaSchema().dump(materia)
        })

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al obtener la materia: {str(e)}")


#actualizar a inhabilitado,solo si el materia se dejara de dar en cualquier lapso del tiempo
#no afecta a las otras tablas

#podria ser funcionalidad futura si quisieramos actualizar la desabilitacion de ese materia para esa gestion cosa que no lo haga manualmente

@materia_bp.route('/<int:id>/update', methods=["PUT"])
def update_materia(id):
    try:
        materia = Materia.query.get(id)
        if not materia:
            raise NotFoundException("Error..materia no encontrado..")

        body = request.get_json()

        schema = MateriaUpdateSchema()
        if schema.validate(body):
            raise ValidationError("Hubo un error en la validación de datos.")

        data = schema.load(body)
        materia.nombre = data["nombre"]
        materia.estado = EstadoGeneral.get_by_description(data["estado"])

        db.session.commit()
        return jsonify({
            "message": "materia actualizada exitosamente",
            "materia": MateriaSchema().dump(materia)
        })

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al actualizar la materia: {str(e)}")


#solo para administrador
@materia_bp.route('/<int:id>/delete', methods=["DELETE"])
def delete_materia(id):
    try:
        materia = Materia.query.get(id)
        if not materia:
            raise NotFoundException("Materia no encontrada")
                
        #para desabilitar
        materia.estado = EstadoGeneral.DESHABILITADO._value_[0]

        # materia.soft_delete()
        db.session.commit()
        return jsonify({
            "message": "materia eliminado con éxito"
        })

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al eliminar el materia: {str(e)}")
