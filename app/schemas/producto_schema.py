from marshmallow import Schema,fields,validate



class ProductoRegisterRequest(Schema):
    stock = fields.Int(required=True, validate=validate.Range(min=1))
    precio = fields.Decimal(required=True, validate=validate.Range(min=0))
    tiempo_garantia = fields.Str(required=True)
    modelo_id = fields.Int(required=False, allow_none=True)
    descripcion = fields.Str(required=True)

    # Características opcionales
    ram = fields.Str(required=False, allow_none=True)
    almacenamiento = fields.Str(required=False, allow_none=True)
    sistema_operativo = fields.Str(required=False, allow_none=True)
    conectividad = fields.Str(required=False, allow_none=True)
    puertos = fields.Str(required=False, allow_none=True)
    camara = fields.Str(required=False, allow_none=True)
    procesador = fields.Str(required=False, allow_none=True)
    bateria = fields.Str(required=False, allow_none=True)
    tarjeta_grafica = fields.Str(required=False, allow_none=True)
    microfono_integrado = fields.Bool(required=False, allow_none=True)
    modelo = fields.Str(required=False, allow_none=True)
    dimension = fields.Str(required=False, allow_none=True)
    peso = fields.Str(required=False, allow_none=True)
    pantalla = fields.Str(required=False, allow_none=True)
    resolucion = fields.Str(required=False, allow_none=True)
    color = fields.Str(required=False,allow_none=True)

class ProductoUpdateRequest(ProductoRegisterRequest):
    estado = fields.Str(required=False, allow_none=True)