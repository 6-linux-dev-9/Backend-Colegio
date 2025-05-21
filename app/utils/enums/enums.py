from enum import Enum

from app.errors.errors import GenericError
from http import HTTPStatus


class BaseEnum(Enum):
    @classmethod
    def get_by_char(cls, db_char):
        for action in cls:
            if action.value[0] == db_char:
                return action
        raise GenericError(
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.BAD_REQUEST.phrase,
            f"Error..Caracter de accion no valido {db_char}"
        )

    def get_descripcion(self):
        return self.value[1]

    def get_caracter(self):
        return self.value[0]


class Sesion(BaseEnum):

    LOGIN = ('I',"INICIO DE SESION")
    LOGOUT = ('C',"CIERRE DE SESION")
    REGISTRO_DE_USUARIO = ('R',"REGISTRO DE USUARIO")
    ACTUALIZACION_PASSWORD = ('P',"ACTUALIZACION DE PASSWORD")
    ACTUALIZACION_PERFIL = ('K',"ACTUALIZACION DE IMAGEN DE PERFIL")
    ACTUALIZACION_DATA = ('U',"ACTUALIZACION DE DATOS")
    DELETE_ACCOUNT = ('D',"ELIMINACION DE CUENTA")
    BLOCK_ACCOUNT = ('B',"BLOCKEO DE CUENTA")
    INICIO_TRANSACCION = ('A','INICIO TRANSACCION STRIPE')
    FIN_EXITO_TRANSACCION = ('E','TRANSACCION CON EXITO')
    CANCELACION_TRANSACCION = ('F','TRANSACCION CANCELADA')
    ERROR_TRANSACCION = ('G','ERROR EN STRIPE')
    
class Estado(BaseEnum):
    DISPONIBLE = ('D',"DISPONIBLE")
    NO_DISPONIBLE = ('N',"NO DISPONIBLE")
    PENDIENTE = ('P','PENDIENTE')
    PAGADO = ('G','PAGADO')

class Pasarela(BaseEnum):
    INICIO_TRANSACCION = ('I','INICIO TRANSACCION STRIPE')
    FIN_EXITO_TRANSACCION = ('F','TRANSACCION CON EXITO')
    CANCELACION_TRANSACCION = ('C','TRANSACCION CANCELADA')
    ERROR_TRANSACCION = ('E','ERROR EN STRIPE')

