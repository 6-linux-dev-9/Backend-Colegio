from marshmallow import fields,Schema

class GestionRequestBody(Schema):
    nombre = fields.Str(required=True)

class GestionUpdateBody(Schema):
    nombre = fields.Str(required=True)
    estado = fields.Str(required=True)

class GestionGetCursosBody(Schema):
    gestion_id = fields.Int(required=True)