


from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.database import db
from app.errors.errors import  GenericError, InternalServerException
from app.models import Materia
from app.schemas.materias_schema import MateriaRequestSchema
from app.schemas.pagination_shema import PaginatedResponseT
from app.schemas.schemas import MateriaSchema



materia_bp = Blueprint('materia',__name__)
@materia_bp.route('/registrar',methods=["POST"])
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