from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.database import db
from app.errors.errors import  GenericError, InternalServerException
from app.models import Curso
from app.schemas.curso_schema import CursoRequestBody

from app.schemas.pagination_shema import PaginatedResponseT
from app.schemas.schemas import CursoSchema



curso_bp = Blueprint('cursos',__name__)
@curso_bp.route('/create',methods = ["POST"])
def crear_cursos():
    try:
        #recibimos los datos
        body = request.get_json()
        print(f"body = {body}")
        schema = CursoRequestBody()
        if schema.validate(body): #si hay errores
            raise ValidationError("Hubo un error en la validacion de datos..")
        #ya validado los datos
        data = schema.load(body) #ya es JSON
        print(f"data: {data}")
        nuevo_curso = Curso(
            nombre = data["nombre"],
            turno = data["turno"]
        )    
        #insertamos en la bd
        db.session.add(nuevo_curso)
        db.session.commit()
        #para serializar la respuesta
        schema_response = CursoSchema()
        response = schema_response.dump(nuevo_curso)
        #agregamos un mensaje,solamente para probar
        return jsonify({
            "message": "curso creado exitosamente",  # Mensaje adicional
            "curso": response  # Los datos del rol creado
        })
    #tira un 200 aunque no lo definamos
        
    except GenericError:
        db.session.rollback()
        raise  # Relanza GenericError para que lo maneje @app.errorhandler
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error ocurrio un error inesperado..{str(e)}")
    
@curso_bp.route('/list-paginate',methods=["GET"])
def listar_paginados():
    try:
        return PaginatedResponseT.paginate(Curso.query,CursoSchema)
    except Exception as e:
        raise InternalServerException(f"Error ocurrio un error inesperado {str(e)}")
