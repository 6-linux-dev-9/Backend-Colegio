from flask import Blueprint, jsonify
from app.database import db
from app.errors.errors import NotFoundException
from app.models import CursoGestion
from sqlalchemy.orm import joinedload

from app.schemas.schemas import CursoGestionEditSchema
curso_gestion_bp = Blueprint('curso_gestion',__name__)

#para obtener los datos del objeto curso gestion
@curso_gestion_bp.route('/<int:id>/get',methods=["GET"])
def get_curso_gestion(id):
    curso_gestion = CursoGestion.query.options(
        joinedload(CursoGestion.gestion),
        joinedload(CursoGestion.curso)).filter_by(id=id).first()
    if not curso_gestion:
        raise NotFoundException("Error curso gestion no encontrada...")
    return jsonify(CursoGestionEditSchema().dump(curso_gestion))


    
# @curso_gestion_bp.route('/<int:id>/update',methods=["PUT"])
# def update_simple_data(id):
