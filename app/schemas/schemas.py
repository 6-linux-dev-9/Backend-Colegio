from marshmallow import ValidationError, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import BitacoraUsuario, Usuario, Rol, Permiso
from app.database import db
from app.utils.enums.enums import  Sesion


#puros esquemas para las respuestas en formato json
#para poder tener respuestas del json y que no entre a bucle supuestamente
class UsuarioSchema(SQLAlchemyAutoSchema):
    fecha_creacion = fields.Method("format_created")
    fecha_actualizacion = fields.Method("format_updated")
    class Meta:
        model = Usuario #para poder usar el esquema hacia un tipo de dato
        include_fk = True #incluye la llave foranea,(mostraria rol_id) en la serializacion
        load_instance = True #Permite desSerealizar JSON a objetos de SQLAlchemy
        sqla_session = db.session
        exclude = ["password","created_at","updated_at"] #podrias excluir del modelo

    #RolSchema 
    #es como que el usuario Schema tiene un rol y solamente capturara de rol algunos atributos
    rol = fields.Nested("RolSchema",only=["id","nombre"]
                        )
    def format_created(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M")

    def format_updated(self, obj):
        return obj.updated_at.strftime("%d-%m-%Y %H:%M")

class RolSchema(SQLAlchemyAutoSchema):
    fecha_creacion = fields.Method("format_created")
    fecha_actualizacion = fields.Method("format_updated")
    class Meta:
        model = Rol
        load_instance = True
        sqla_session = db.session
        exclude = ["created_at","updated_at"]

    #permisos = fields.List(fields.Nested("PermisoSchema", only=["id", "nombre"]))

    def format_created(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M")

    def format_updated(self, obj):
        return obj.updated_at.strftime("%d-%m-%Y %H:%M")
    

class PermisoSchema(SQLAlchemyAutoSchema):
    fecha_creacion = fields.Method("format_created")
    fecha_actualizacion = fields.Method("format_updated")
    class Meta:
        model = Permiso
        load_instance = True
        sqla_session = db.session
        exclude = ["created_at","updated_at"]

    roles = fields.List(fields.Nested("RolSchema", only=["id", "nombre"]))  # Evita el bucle
    def format_created(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M")
    def format_updated(self, obj):
        return obj.updated_at.strftime("%d-%m-%Y %H:%M")

class BitacoraUsuarioSchema(SQLAlchemyAutoSchema):
    tipo_accion = fields.Method("get_tipo_accion")
    #para las fechas y horas
    fecha = fields.Method("get_fecha")
    hora = fields.Method("get_hora")
    class Meta:
        model = BitacoraUsuario
        load_instance = True
        sqla_session = db.session
        exclude=["created_at","updated_at"]
    #para parsear el dato de la bd a un dato entendible
    def get_tipo_accion(self,obj):
        try:
            return Sesion.get_by_char(obj.tipo_accion).get_descripcion()
        except (ValueError,AttributeError):
            raise ValidationError("Error en la conversion de datos")
        
    def get_fecha(self, obj):
        return obj.created_at.strftime("%d-%m-%Y") if obj.created_at else None

    def get_hora(self, obj):
        return obj.created_at.strftime("%H:%M") if obj.created_at else None
        
# class MarcaSchema(SQLAlchemyAutoSchema):
#     fecha_creacion = fields.Method("format_created")
#     fecha_actualizacion = fields.Method("format_updated")
#     class Meta:
#         model = Marca
#         load_instance = True
#         sqla_session = db.session
#     def format_created(self, obj):
#         return obj.created_at.strftime("%d-%m-%Y %H:%M")
#     def format_updated(self, obj):
#         return obj.updated_at.strftime("%d-%m-%Y %H:%M")
    
        


class RolWithPermissionSchema(SQLAlchemyAutoSchema):
    fecha_creacion = fields.Method("format_created")
    fecha_actualizacion = fields.Method("format_updated")
    class Meta:
        model = Rol
        load_instance = True
        sqla_session = db.session

    permisos = fields.List(fields.Nested("PermisoSchema", only=["id", "nombre"]))

    def format_created(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M")

    def format_updated(self, obj):
        return obj.updated_at.strftime("%d-%m-%Y %H:%M")
    



class UsuarioImageSchema(SQLAlchemyAutoSchema):
    fecha_creacion = fields.Method("format_created")
    fecha_actualizacion = fields.Method("format_updated")
    class Meta:
        model = Usuario #para poder usar el esquema hacia un tipo de dato
        include_fk = True #incluye la llave foranea,(mostraria rol_id) en la serializacion
        load_instance = True #Permite desSerealizar JSON a objetos de SQLAlchemy
        sqla_session = db.session
        exclude = ["password","created_at","updated_at"] #podrias excluir del modelo

    rol = fields.Nested("RolSchema",only=["id","nombre"])

    def format_created(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M")

    def format_updated(self, obj):
        return obj.updated_at.strftime("%d-%m-%Y %H:%M")





