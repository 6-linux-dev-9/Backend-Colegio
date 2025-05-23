
from http import HTTPStatus
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.database import db
from app.errors.errors import GenericError, InternalServerException, NotFoundException
from app.models import Curso, CursoGestion, CursoGestionMateria, Gestion
from app.schemas.gestion_chema import  GestionRequestBody, GestionUpdateBody
from app.schemas.pagination_shema import PaginatedResponseT
from app.schemas.schemas import CursoGestionMateriaSchema, CursoGestionSchema, GestionSchema
from app.utils.enums.enums import EstadoGeneral
from sqlalchemy.orm import joinedload

gestion_bp = Blueprint('gestion',__name__)

@gestion_bp.route('/create',methods=["POST"])
def registrar():
    try:
        body = request.get_json()
        schema = GestionRequestBody()
        if schema.validate(body):
            raise ValidationError("Hubo un error al validar los datos...")
        data = schema.load(body)
        nueva_gestion = Gestion(
            nombre = data["nombre"]
        )
        db.session.add(nueva_gestion)
        db.session.commit()
        return jsonify({
            "message":"Gestion creada con exito",
            "gestion":GestionSchema().dump(nueva_gestion)
        })

    except Exception as e:
        raise InternalServerException(f"ocurrio un error inesperado ${str(e)}")
    
@gestion_bp.route('/list-paginate',methods=["GET"])
def get_gestiones_paginado():
    try:
        return PaginatedResponseT.paginate(Gestion.query.filter_by(is_deleted=False),GestionSchema)
    except Exception as e:
        raise InternalServerException(f"ocurrio un error inesperado ${str(e)}")
    
#metodo usado para cuando se obtiene todos los objetos cursos
@gestion_bp.route('/list',methods=["GET"])  
def list_gestion():
    try:
        return GestionSchema(many=True).dump(Gestion.query.filter_by(
            estado=EstadoGeneral.HABILITADO.get_caracter()
            ,is_deleted=False).all())
    except Exception as e:
        raise InternalServerException(f"ocurrio un error inesperado ${str(e)}")

@gestion_bp.route("/<int:id>/get", methods=["GET"])
def obtener_gestion(id):
    try:
        gestion = Gestion.query.get(id)
        if not gestion:
            raise NotFoundException("Gestion no encontrada")

        return jsonify({
            "gestion": GestionSchema().dump(gestion)
        }), HTTPStatus.OK

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al obtener la gestion: {str(e)}")

@gestion_bp.route("/<int:id>/update", methods=["PUT"])
def actualizar_gestion(id):
    try:
        gestion = Gestion.query.get(id)
        if not gestion:
            raise NotFoundException("Gestion no encontrada")

        body = request.get_json()
        schema = GestionUpdateBody()
        if schema.validate(body):
            raise ValidationError("Hubo un error en la validación de datos.")

        data = schema.load(body)
        gestion.nombre = data["nombre"]
        gestion.estado = EstadoGeneral.get_by_description(data["estado"]) 

        db.session.commit()
        return jsonify({
            "message": "Gestion actualizada exitosamente",
            "gestion": GestionSchema().dump(gestion)
        })

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al obtener la gestion: {str(e)}")


@gestion_bp.route("/<int:id>/delete", methods=["DELETE"])
def eliminar_gestion(id):
    try:
        gestion = Gestion.query.get(id)
        if not gestion:
            raise NotFoundException("Gestion no encontrada")

        #para desabilitar
        gestion.estado = EstadoGeneral.ELIMINADO.get_caracter()
        gestion.soft_delete()
        db.session.commit()

        return jsonify({
            "message": "Gestion eliminada con exito"
        }), HTTPStatus.OK

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al eliminar la gestion: {str(e)}")
    
@gestion_bp.route("/<int:id>/revertir", methods=["PUT"])
def revertir_gestion(id):
    try:
        gestion = Gestion.query.get(id)
        if not gestion:
            raise NotFoundException("Gestion no encontrada")

        #para desabilitar
        gestion.estado = EstadoGeneral.HABILITADO.get_caracter()
        gestion.is_deleted = False
        db.session.commit()

        return jsonify({
            "message": "Gestion eliminada con exito"
        }), HTTPStatus.OK

    except GenericError:
        db.session.rollback()
        raise
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"Error inesperado al eliminar la gestion: {str(e)}")



#aplicando en curso gestion para saber los cursos de una determinada gestion

@gestion_bp.route('/<int:id>/get-cursos',methods=["GET"])
def get_cursos_por_gestion(id):
    try:
        
        gestion = Gestion.query.get(id)
        if not gestion:
            raise NotFoundException("Error..gestion no encontrada..")
        cursos = db.session.query(CursoGestion).join(Curso).join(Gestion).filter(
            CursoGestion.gestion_id == id,
            #CursoGestion.estado == EstadoGeneral.HABILITADO.get_caracter(),
            CursoGestion.is_deleted == False
        ).all()
        #return PaginatedResponseT.paginate(cursos,CursoGestionSchema)
        return CursoGestionSchema(many=True).dump(cursos)

    except GenericError:
        db.session.rollback()
        raise 
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"ocurrio un error inesperado..{str(e)}")

#metodo para obtener las materias de un determinado curso
@gestion_bp.route('/<int:id_gestion>/curso/<int:id_curso>/get-materias',methods=["GET"])
def get_materias_por_gestion_y_curso(id_gestion,id_curso):
    try:
        gestion = Gestion.query.get(id_gestion)
        if not gestion:
            raise NotFoundException("Error..gestion no encontrada..")
        
        curso = Curso.query.get(id_curso)
        if not curso:
            raise NotFoundException("Error..curso no encontrado...")
        curso_gestion = CursoGestion.query.options(
            joinedload(CursoGestion.curso_gestion_materias,
                       CursoGestionMateria.materia)).filter_by(
            curso_id=id_curso,gestion_id=id_gestion,is_deleted=False).first()
        if not curso_gestion:
            raise NotFoundException("Error..el curso o la gestion no fueron encontrados...")
        
        materias = curso_gestion.curso_gestion_materias
        return jsonify(CursoGestionMateriaSchema(many=True).dump(materias))
        
    except GenericError:
        db.session.rollback()
        raise 
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"ocurrio un error inesperado..{str(e)}")  




