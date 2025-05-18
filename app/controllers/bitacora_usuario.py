from flask import Blueprint, jsonify, request

from app.errors.errors import GenericError
from app.models import BitacoraUsuario
from app.schemas.schemas import BitacoraUsuarioSchema
from app.database import db
from http import HTTPStatus

bitacora_bp = Blueprint('bitacora_usuario',__name__)
@bitacora_bp.route('/list-paginate',methods=["GET"])
def list_paginate():
    try:
        # Obtener parámetros de paginación de la query
        pagina = request.args.get('page', 1, type=int)
        por_pagina = request.args.get('per_page', 10, type=int)

        # Consulta paginada
        paginacion = BitacoraUsuario.query.order_by(BitacoraUsuario.created_at.desc()).paginate(
            page=pagina, per_page=por_pagina
        )

        # Serializar los datos
        schema = BitacoraUsuarioSchema(many=True)
        datos = schema.dump(paginacion.items)
        # Armar respuesta
        return jsonify({
                "items": datos,
                "meta": {
                    "total_items": paginacion.total,
                    "total_pages": paginacion.pages,
                    "current_page": paginacion.page,
                    "page_size": paginacion.per_page
                }
        })
    except Exception as e:# aunque no se si esto funcione
        db.session.rollback()
        raise GenericError(HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR.phrase, str(e))  # Solo errores inesperados