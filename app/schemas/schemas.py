from marshmallow import Schema, ValidationError, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema, auto_field
from app.models import Alumno, BitacoraUsuario, Curso, CursoGestion, CursoGestionMateria, Docente, Gestion, Materia, Usuario, Rol, Permiso
from app.database import db
from app.utils.enums.enums import  EstadoGeneral, EstadoUsuario, Sesion

class BaseFechaHoraSeparadoSchema(SQLAlchemyAutoSchema):
    fecha = fields.Method("get_fecha")
    hora = fields.Method("get_hora")

    def get_fecha(self,obj):
        return obj.created_at.strftime("%d-%-m-%Y") if obj.created_at else None
    
    def get_hora(self,obj):
        return obj.created_at.strftime("%H:%M") if obj.created_at else None

class BaseFechaCompletaSchema(SQLAlchemyAutoSchema):
    fecha_creacion = fields.Method("format_created")
    fecha_actualizacion = fields.Method("format_updated")

    def format_created(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %H:%M") if obj.created_at else None

    def format_updated(self, obj):
        return obj.updated_at.strftime("%d-%m-%Y %H:%M") if obj.updated_at else None

class BaseEstadoGeneralSchema(SQLAlchemyAutoSchema):
    estado = fields.Method("get_estado")
    def get_estado(self,obj):
        try:
            return EstadoGeneral.get_by_char(obj.estado).get_descripcion()
        except (ValueError,AttributeError):
            raise ValidationError("Error en la conversion de datos")


class BaseEstadoUsuarioSchema(SQLAlchemyAutoSchema):
    estado = fields.Method("get_estado")
    def get_estado(self,obj):
        try:
            estado_char = obj.estado if hasattr(obj, 'estado') else obj.usuario.estado
            return EstadoUsuario.get_by_char(estado_char).get_descripcion()
        except (ValueError,AttributeError):
            raise ValidationError("Error en la conversion de datos")
        
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

#usar primero el baseSchema para que use el metodo de formateo de esa clase
class RolSchema(BaseFechaCompletaSchema,SQLAlchemyAutoSchema):
    
    class Meta:
        model = Rol
        load_instance = True
        sqla_session = db.session
        exclude = ["created_at","updated_at"]

    #permisos = fields.List(fields.Nested("PermisoSchema", only=["id", "nombre"]))

    

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

class AlumnoSchema(BaseFechaCompletaSchema,BaseEstadoUsuarioSchema,SQLAlchemySchema):
    class Meta:
        model = Alumno
        load_instance = True
        exclude = ["created_at","updated_at"]
    #atributos propio del esquema Alumno
    id = auto_field()
    rude = auto_field()

    nombre = fields.Function(lambda obj: obj.usuario.nombre)
    correo = fields.Function(lambda obj: obj.usuario.email)
    ci = fields.Function(lambda obj: obj.usuario.ci)
    url_profile = fields.Function(lambda obj: obj.usuario.url_profile)


class DocenteSchema(BaseFechaCompletaSchema,BaseEstadoUsuarioSchema,SQLAlchemySchema):
    class Meta:
        model = Docente
        load_instance = True
        exclude = ["created_at","updated_at"]
    #atributos propio del esquema Alumno
    id = auto_field()
    nombre = fields.Function(lambda obj: obj.usuario.nombre)
    correo = fields.Function(lambda obj: obj.usuario.email)

    ci = fields.Function(lambda obj: obj.usuario.ci)
    url_profile = fields.Function(lambda obj: obj.usuario.url_profile)

class GestionSchema(BaseFechaCompletaSchema,BaseEstadoGeneralSchema,SQLAlchemyAutoSchema):
    class Meta:
        model = Gestion
        load_instance = True
        sqla_session = db.session
        exclude = ["created_at","updated_at"]

class MateriaSchema(BaseFechaCompletaSchema,BaseEstadoGeneralSchema,SQLAlchemyAutoSchema):
    class Meta:
        model = Materia
        load_instance = True
        sqla_session = db.session
        exclude = ["created_at","updated_at"]

class CursoSchema(BaseFechaCompletaSchema,BaseEstadoGeneralSchema,
                  SQLAlchemyAutoSchema):
    class Meta:
        model = Curso
        load_instance = True
        sqla_session = db.session
        exclude = ["created_at","updated_at"]


class CursoSimpleSchema(Schema):
    id = fields.Int()
    nombre = fields.Method("get_nombre_completo")

    def get_nombre_completo(self, obj):
        return f"{obj.nombre} - {obj.turno}"

class MateriaSimpleSchema(Schema):
    id = fields.Int()
    nombre = fields.Method("get_nombre")
    #creo que sel ya esta poblado y obj es el objeto que entra al llamarse
    def get_nombre(self,obj):
        return f"{obj.nombre}"


class CursoGestionMateriaSchema(BaseEstadoGeneralSchema,SQLAlchemyAutoSchema):
    class Meta:
        model =CursoGestionMateria
        load_instance = True
        sqla_session = db.session
        
        exclude = ["created_at","updated_at","cantidad_abandono","cantidad_aprobados","cantidad_reprobados","url_image"]
    materia = fields.Nested("MateriaSimpleSchema",only=["id","nombre"])

class CursoGestionSchema(BaseEstadoGeneralSchema,SQLAlchemyAutoSchema):
    # total_aprobados = fields.Method("get_total_aprobados")
    # total_reprobados = fields.Method("get_total_reprobados")
    # total_abandono = fields.Method("get_total_abandono")

    class Meta:
        model = CursoGestion
        load_instance = True
        sqla_session = db.session
        exclude = ["created_at","updated_at","total_abandono","total_aprobados","total_reprobados","url_image"]
        

    curso = fields.Nested("CursoSimpleSchema",only=["id","nombre"])
    # def get_total_aprobados(self, obj):
    #     return 0 if obj.total_aprobados is None else obj.total_aprobados

    # def get_total_reprobados(self, obj):
    #     return 0 if obj.total_aprobados is None else obj.total_reprobados
    
    # def get_total_abandono(self, obj):
    #     return 0 if obj.total_abandono is None else obj.total_abandono

class CursoGestionEditSchema(BaseEstadoGeneralSchema,SQLAlchemyAutoSchema):
    total_aprobados = fields.Method("get_total_aprobados")
    total_reprobados = fields.Method("get_total_reprobados")
    total_abandono = fields.Method("get_total_abandono")

    class Meta:
        model = CursoGestion
        load_instance = True
        sqla_session = db.session
        exclude = ["created_at","updated_at","is_deleted"]
        

    curso = fields.Nested("CursoSimpleSchema",only=["id","nombre"])
    gestion = fields.Nested("GestionSchema",only=["id","nombre"])
    #docente asignado proximamente
    
    def get_total_aprobados(self, obj):
        return 0 if obj.total_aprobados is None else obj.total_aprobados

    def get_total_reprobados(self, obj):
        return 0 if obj.total_aprobados is None else obj.total_reprobados
    
    def get_total_abandono(self, obj):
        return 0 if obj.total_abandono is None else obj.total_abandono
        
    