
from http import HTTPStatus
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.database import db
from app.errors.errors import GenericError, InternalServerException, NotFoundException
from app.models import Curso, CursoGestion, Gestion
from app.schemas.gestion_chema import GestionGetCursosBody, GestionRequestBody, GestionUpdateBody
from app.schemas.pagination_shema import PaginatedResponseT
from app.schemas.schemas import CursoGestionSchema, GestionSchema
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
        return PaginatedResponseT.paginate(Gestion.query,GestionSchema)
    except Exception as e:
        raise InternalServerException(f"ocurrio un error inesperado ${str(e)}")
    
@gestion_bp.route('/list',methods=["GET"])  
def list_gestion():
    try:
        return GestionSchema(many=True).dump(Gestion.query.filter_by(estado=EstadoGeneral.HABILITADO.get_caracter()).all())
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
        gestion.estado = EstadoGeneral.DESHABILITADO._value_[0]

        # gestion.soft_delete()
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
            CursoGestion.estado == EstadoGeneral.HABILITADO.get_caracter()
        ).all()
        #return PaginatedResponseT.paginate(cursos,CursoGestionSchema)
        return CursoGestionSchema(many=True).dump(cursos)

    except GenericError:
        db.session.rollback()
        raise 
    except Exception as e:
        db.session.rollback()
        raise InternalServerException(f"ocurrio un error inesperado..{str(e)}")



