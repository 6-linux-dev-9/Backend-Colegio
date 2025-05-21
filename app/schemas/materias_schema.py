from marshmallow import Schema,fields


class MateriaRequestSchema(Schema):
    nombre = fields.Str(required=True)