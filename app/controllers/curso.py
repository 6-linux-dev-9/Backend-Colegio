from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.database import db
from app.errors.errors import  GenericError, InternalServerException, NotFoundException
from app.models import Curso, CursoGestion, Gestion
from app.schemas.curso_schema import CursoRequestBody, CursoUpdateBody

from app.schemas.pagination_shema import PaginatedResponseT
from app.schemas.schemas import CursoGestionEditSchema, CursoSchema, CursoSimpleSchema
from app.utils.enums.enums import EstadoGeneral
from sqlalchemy.orm import joinedload


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
        return PaginatedResponseT.paginate(
            Curso.query.filter_by(
            is_deleted=False),CursoSchema
        )
    except Exception as e:
        raise InternalServerException(f"Error ocurrio un error inesperado {str(e)}")

@curso_bp.route('/list',methods=["GET"])  
def list_gestion():
    try:
        return CursoSimpleSchema(many=True).dump(Curso.query.filter_by(
            is_deleted=False,estado=EstadoGeneral.HABILITADO.get_caracter()).all())
    except Exception as e:
        raise InternalServerException(f"ocurrio un error inesperado ${str(e)}")


@curso_bp.route('/<int:id>/get', methods=["GET"])
def get_curso(id):
    try:
        curso = Curso.query.get(id).first()
        if not curso:
            raise NotFoundException("Error..curso no encontrado..")

        return jsonify({
            "curso": CursoSchema().dump(curso)
        })

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al obtener el curso: {str(e)}")


#actualizar a inhabilitado,solo si el curso se dejara de dar en cualquier lapso del tiempo
#no afecta a las otras tablas

#podria ser funcionalidad futura si quisieramos actualizar la desabilitacion de ese curso para esa gestion cosa que no lo haga manualmente

@curso_bp.route('/<int:id>/update', methods=["PUT"])
def update_curso(id):
    try:
        curso = Curso.query.get(id)
        if not curso:
            raise NotFoundException("Error..curso no encontrado..")

        body = request.get_json()

        schema = CursoUpdateBody()
        if schema.validate(body):
            raise ValidationError("Hubo un error en la validación de datos.")

        data = schema.load(body)
        curso.nombre = data["nombre"]
        curso.turno = data["turno"]
        print(data["nombre"])
        print(data["turno"])
        print(data["estado"])
        curso.estado = EstadoGeneral.get_by_description(data["estado"])

        db.session.commit()
        return jsonify({
            "message": "Curso actualizado exitosamente",
            "curso": CursoSchema().dump(curso)
        })

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al actualizar el curso: {str(e)}")


#solo para administrador
@curso_bp.route('/<int:id>/delete', methods=["DELETE"])
def delete_curso(id):
    try:
        curso = Curso.query.get(id)
        if not curso:
            raise NotFoundException("Curso no encontrado")
                
        #para desabilitar
        curso.estado = EstadoGeneral.ELIMINADO.get_caracter()
        curso.soft_delete()
        db.session.commit()
        return jsonify({
            "message": "Curso eliminado con éxito"
        })

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al eliminar el curso: {str(e)}")



#solo para administrador
@curso_bp.route('/<int:id>/revertir', methods=["PUT"])
def revertir_curso(id):
    try:
        curso = Curso.query.get(id)
        if not curso:
            raise NotFoundException("Curso no encontrado")
                
        #para desabilitar
        #curso.estado = EstadoGeneral.DESHABILITADO._value_[0]
        curso.estado = EstadoGeneral.HABILITADO.get_caracter()
        curso.is_deleted = False
        db.session.commit()
        return jsonify({
            "message": "Curso revertido correctamente"
        })

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al eliminar el curso: {str(e)}")


#para obtener el curso algo completo con su gestion, y data del curso como su imagen
#total de aprobados,etc,etc,etc
@curso_bp.route("/<int:id_curso>/gestion/<int:id_gestion>/get-edit-data",methods=["GET"])
def get_curso_con_curso_gestion(id_curso,id_gestion):
    try:
        gestion = Gestion.query.filter(Gestion.estado==EstadoGeneral.HABILITADO.get_caracter(),
                                       Gestion.id == id_gestion,
                                       Gestion.is_deleted == False).first()
        if not gestion:
            raise NotFoundException("Error la gestion no fue encontrada")
        curso = Curso.query.filter(Curso.estado==EstadoGeneral.HABILITADO.get_caracter(),
                                   Curso.id==id_curso).first()
        if not curso:
            raise NotFoundException("Error..el curso no fue encontrado en el sistema")

        curso_gestion = db.session.query(CursoGestion).join(CursoGestion.gestion).join(CursoGestion.curso).filter(CursoGestion.curso_id == id_curso,
                                        CursoGestion.gestion_id == id_gestion,
                                        CursoGestion.estado==EstadoGeneral.HABILITADO.get_caracter()).first()    
        if not curso_gestion:
            raise NotFoundException("Error..el curso o la gestion no fue encontrado en el sistema")
        
        return CursoGestionEditSchema().dump(curso_gestion)
        
    except Exception as e:
        raise InternalServerException(f"Error ocurrion un error inesperado...{str(e)}")



