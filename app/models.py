from datetime import datetime
from datetime import timezone





#muy importante importar correctamente la base de datos definida en database

from app.database import db
from sqlalchemy import Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.enums.enums import Sesion

# Mixin para funcionalidad común
#clase para que hereden los demas 
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), 
                                               onupdate=datetime.now(timezone.utc))

class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    def soft_delete(self):
        """Realiza eliminación lógica"""
        self.is_deleted = True
        db.session.flush()

    """para obtener usuarios activos o usuarios que no an sido eliminados fisicamente"""
    @classmethod
    def get_active(cls):
        """Filtra solo registros no eliminados"""
        return cls.query.filter_by(is_deleted=False)

# modelo de Usuario
class Usuario(db.Model, TimestampMixin,SoftDeleteMixin):
    __tablename__ = 'usuarios'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), nullable=False)
    nombre: Mapped[str] = mapped_column(String(80),nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    rol_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('roles.id'), nullable=False)
    # Relación con el modelo Rol
    #esto hace que la clase Rol tenga un atributo usuarios
    rol: Mapped["Rol"] = relationship('Rol', back_populates='usuarios')
    #para el perfil
    url_profile: Mapped[str] = mapped_column(String(50),nullable=True)
    ci: Mapped[str] = mapped_column(String(50),nullable=True)
    def __repr__(self):
        return f'<Usuario {self.username}>'

# modelo de Rol
class Rol(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'roles'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Relaciones
    #back_populates cuadra con rol refinido en Usuario
    usuarios: Mapped[list["Usuario"]] = relationship('Usuario', back_populates='rol')
    permisos: Mapped[list["Permiso"]] = relationship(
        'Permiso', 
        secondary='rol_permiso',
        back_populates='roles'
    )

    def __repr__(self):
        return f'<Rol {self.nombre}>'

# modelo de Permiso
class Permiso(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'permisos'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Relación con roles
    roles: Mapped[list["Rol"]] = relationship(
        'Rol', 
        secondary='rol_permiso',
        back_populates='permisos'
    )

    def __repr__(self):
        return f'<Permiso {self.nombre}>'

# Tabla intermedia para relación muchos-a-muchos
class RolPermiso(db.Model, TimestampMixin):
    __tablename__ = 'rol_permiso'
    rol_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('roles.id'), primary_key=True)
    permiso_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('permisos.id'), primary_key=True)

class BitacoraUsuario(db.Model,TimestampMixin):
    __tablename__ = 'bitacora_usuarios'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ip : Mapped[str] = mapped_column(String,nullable=False)
    username : Mapped[str] = mapped_column(String(40))
    tipo_accion : Mapped[str] = mapped_column(String(1))
    def __repr__(self):
        return f"<Bitacora_usuario> ip: {self.ip}\n username: {self.username}\ntipo_accion: {Sesion.get_by_char(self.tipo_accion).get_descripcion()}"
    
