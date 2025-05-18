from marshmallow import fields, validate,Schema
class UserPasswordRequest(Schema):
    anterior_password = fields.Str(required=True,validate=validate.Length(min=4))
    nueva_password = fields.Str(required=True,validate=validate.Length(min=4))

class UserEditRequest(Schema):
    username= fields.Str(required=True,validate=validate.Length(min=0))
    nombre = fields.Str(required=True,validate=validate.Length(min=1))
    email = fields.Str(required=True,validate=validate.Length(min=6))
    rol_id = fields.Int(required=False)
    #podrian venir otros atributos mas que complementen con la informacion del usuario


class UserAdminPasswordRequest(Schema):
    nueva_password = fields.Str(required=True,validate=validate.Length(min=4))