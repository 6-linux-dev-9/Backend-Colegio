from marshmallow import Schema,validate,fields

class DocenteRegisterSchema(Schema):
    nombre = fields.Str(required=True)
    email = fields.Email(required=False)
    password = fields.Str(required=True,validate=validate.Length(min=4))
    ci = fields.Str(required=True) 
