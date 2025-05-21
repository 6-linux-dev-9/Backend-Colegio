from marshmallow import fields,validate,Schema

#para formateo de datos de entrada
#es como definir un DTO de request
class AuthRegisterSchemaBody(Schema):
    nombre = fields.Str(required=True)
    email = fields.Email(required=False)
    password = fields.Str(required=True,validate=validate.Length(min=4))
    ci = fields.Str(required=True)


class AuthLoginSchemaBody(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class AuthAdminRegisterSchema(Schema):
    username = fields.Str(required=False)
    nombre = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True,validate=validate.Length(min=4))
    rol_id = fields.Int(required=True)


class AuthAdminUpdateSchema(Schema):
    username = fields.Str(required=False)
    nombre = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True,validate=validate.Length(min=0))
    rol_id = fields.Int(required=True)