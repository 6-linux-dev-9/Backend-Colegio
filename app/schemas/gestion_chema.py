from marshmallow import fields,validate,Schema

class GestionRequestBody(Schema):
    nombre = fields.Str(required=True)
