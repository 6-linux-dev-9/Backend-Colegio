from marshmallow import Schema,fields


class MateriaRequestSchema(Schema):
    nombre = fields.Str(required=True)

class MateriaUpdateSchema(Schema):
    nombre = fields.Str(required=True)
    estado = fields.Str(required=True)