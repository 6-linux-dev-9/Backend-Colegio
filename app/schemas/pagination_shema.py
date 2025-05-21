from flask import request
from marshmallow import Schema


class PaginatedResponse:
    PAGINA_POR_DEFECTO = 1
    CANTIDAD_ITEMS_DEFECTO = 5

    #PARA CANTIDADES GRANDES
    DEFAULT_ITEM_PAGE = 10
    MAX_ITEM_PAGE=20

    @classmethod
    def paginate(cls, query, schema):
        pagina = request.args.get('pagina', cls.PAGINA_POR_DEFECTO, type=int)

        #funcion para validar que el valor que le demos de la cantida de items no sobrepase el maximo
        item_page = min(
            request.args.get('items', cls.CANTIDAD_ITEMS_DEFECTO, type=int),
            cls.MAX_ITEM_PAGE)

        paginated = query.paginate(page=pagina, per_page=item_page, error_out=False)
        
        return {
            'data': schema().dump(paginated.items, many=True),
            'pagination': {
                'total': paginated.total,#total de marcas existentes
                'pages': paginated.pages,#total de paginas existentes
                'current_page': paginated.page,#pagina actual
                'per_page': paginated.per_page,#item por pagina
                'next': paginated.next_num if paginated.has_next else None,
                'prev': paginated.prev_num if paginated.has_prev else None
            }
        }





class PaginatedResponseT:
    PAGINA_POR_DEFECTO = 1
    CANTIDAD_ITEMS_DEFECTO = 5
    MAX_ITEM_PAGE = 100

    @classmethod
    def paginate(cls, query, schema: Schema):
        """
        Pagina cualquier consulta SQLAlchemy con cualquier esquema Marshmallow.
        """
        pagina = request.args.get('page', cls.PAGINA_POR_DEFECTO, type=int)
        items = min(
            request.args.get('per_page', cls.CANTIDAD_ITEMS_DEFECTO, type=int),
            cls.MAX_ITEM_PAGE
        )

        paginated = query.paginate(page=pagina, per_page=items, error_out=False)

        return {
            'items': schema().dump(paginated.items, many=True),
            'meta': {
                'total_items': paginated.total,
                'total_pages': paginated.pages,
                'current_page': paginated.page,
                "page_size": paginated.per_page
            }
        }
