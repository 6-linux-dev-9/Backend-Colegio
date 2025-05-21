from marshmallow import fields,Schema

class CursoRequestBody(Schema):
    nombre = fields.Str(required=True)
    turno = fields.Str(required=True)
    
class CursoUpdateBody(Schema):
    nombre = fields.Str(required=True)
    turno = fields.Str(required=True)
    estado = fields.Str(required=True)


