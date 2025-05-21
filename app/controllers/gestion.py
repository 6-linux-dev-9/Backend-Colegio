
from http import HTTPStatus
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.database import db
from app.errors.errors import BadRequestException, GenericError, InternalServerException
from app.models import Gestion
from app.schemas.gestion_chema import GestionRequestBody
from app.schemas.pagination_shema import PaginatedResponseT
from app.schemas.schemas import GestionSchema


gestion_bp = Blueprint('gestion',__name__)

@gestion_bp.route('/registrar',methods=["POST"])
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