from datetime import datetime
from datetime import timezone






#muy importante importar correctamente la base de datos definida en database

from app.database import db
from sqlalchemy import Boolean, ForeignKey, Integer, String, DateTime
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
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    rol_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('roles.id'), nullable=False)
    # Relación con el modelo Rol
    #esto hace que la clase Rol tenga un atributo usuarios
    rol: Mapped["Rol"] = relationship('Rol', back_populates='usuarios')
    #para el perfil
    url_profile: Mapped[str] = mapped_column(String(50),nullable=True)
    ci: Mapped[str] = mapped_column(String(50),unique=True,nullable=False)
    estado: Mapped[str] = mapped_column(String(3),nullable=False,default="AC")#inicialmente activo

    #para alumno
    #cascada momentanea
    alumno:Mapped["Alumno"] = relationship('Alumno',back_populates='usuario',uselist=False,cascade="all, delete-orphan")
    #lo mismo para docente
    docente:Mapped["Docente"] = relationship('Docente',back_populates='usuario',uselist=False,cascade="all, delete-orphan")
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
    
class Alumno(db.Model,TimestampMixin):
    __tablename__ = 'alumnos'
    #cascada momentanea
    id:Mapped[int] = mapped_column(Integer,ForeignKey("usuarios.id", ondelete="CASCADE"),primary_key=True)
    rude:Mapped[str] = mapped_column(String(100),nullable=False)
    usuario: Mapped["Usuario"] = relationship("Usuario",back_populates="alumno")
    def __repr__(self):
        return f"<Alumno> id: {self.id}"

class Docente(db.Model,TimestampMixin):
    __tablename__ = 'docentes'
    id:Mapped[int] = mapped_column(Integer,ForeignKey("usuarios.id", ondelete="CASCADE"),primary_key=True)
    usuario: Mapped["Usuario"] = relationship("Usuario",back_populates="docente")
    materias: Mapped[list["CursoGestionMateria"]] = relationship("CursoGestionMateria",back_populates='docente')
    def __repr__(self):
        return f"<Docente> id: {self.id}"

class Materia(db.Model,TimestampMixin):
    __tablename__ = "materias"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre:Mapped[str] = mapped_column(String(70),nullable=False)
    estado: Mapped[str] = mapped_column(String(3),nullable=False,default="AC")#inicialmente activo
    docentes: Mapped[list["CursoGestionMateria"]] = relationship("CursoGestionMateria",back_populates='materia')
    def __repr__(self):
        return f"<Materia> id: {self.id}, nombre: {self.nombre}"

class Gestion(db.Model,TimestampMixin):
    __tablename__ = "gestiones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre:Mapped[str] = mapped_column(String(40),nullable=False)
    estado: Mapped[str] = mapped_column(String(3),nullable=False,default="AC")#inicialmente activo

    cursos:Mapped[list["CursoGestion"]] = relationship('CursoGestion',back_populates='gestion')

    periodos:Mapped[list["Periodo"]] = relationship('Periodo',back_populates='gestion')
    def __repr__(self):
        return f"<Gestion> id: {self.id}, nombre: {self.nombre}"

class Curso(db.Model,TimestampMixin):
    __tablename__ = "cursos"
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    nombre:Mapped[str] = mapped_column(String(40),nullable=False)
    turno:Mapped[str] = mapped_column(String(20),nullable=False)
    estado: Mapped[str] = mapped_column(String(3),nullable=False,default="AC")#inicialmente activo
    gestiones: Mapped[list["CursoGestion"]] = relationship('CursoGestion',back_populates='curso')

    def __repr__(self):
        return f"<Curso> id: {self.id}, nombre: {self.nombre}"

class CursoGestion(db.Model,TimestampMixin):
    __tablename__ = "curso_gestion"
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    total_aprobados:Mapped[int] = mapped_column(Integer,nullable=True)
    total_reprobados:Mapped[int] = mapped_column(Integer,nullable=True)
    total_abandono:Mapped[int] = mapped_column(Integer,nullable=True)
    url_image : Mapped[str] = mapped_column(String,nullable=True)
    estado: Mapped[str] = mapped_column(String(3),nullable=False,default="AC")#inicialmente activo

    #relacion con curso
    curso_id:Mapped[int] = mapped_column(Integer,ForeignKey("cursos.id"))
    gestion_id:Mapped[int] = mapped_column(Integer,ForeignKey("gestiones.id"))

    curso:Mapped["Curso"] = relationship('Curso',back_populates="gestiones")
    gestion:Mapped["Gestion"] = relationship('Gestion',back_populates="cursos")

    curso_gestion_materias:Mapped[list["CursoGestionMateria"]] = relationship('CursoGestionMateria',back_populates='curso_gestion')


    def __repr__(self):
        return f"<CursoGestion> id: {self.id}"

class CursoGestionMateria(db.Model,TimestampMixin):
    __tablename__ = "curso_gestion_materia"
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    horario:Mapped[str] = mapped_column(String,nullable=False)
    cantidad_aprobados:Mapped[int] = mapped_column(Integer,nullable=True)
    cantidad_reprobados:Mapped[int] = mapped_column(Integer,nullable=True)
    cantidad_abandono:Mapped[int] = mapped_column(Integer,nullable=True)
    url_image : Mapped[str] = mapped_column(String,nullable=True)
    estado: Mapped[str] = mapped_column(String(3),nullable=False,default="AC")#inicialmente activo
    #para docente
    docente_id: Mapped[int] = mapped_column(Integer,ForeignKey("docentes.id"))
    docente: Mapped["Docente"] = relationship("Docente",back_populates='materias')

    #para materias
    materia_id:Mapped[int] = mapped_column(Integer,ForeignKey("materias.id"))
    materia: Mapped["Materia"] = relationship("Materia",back_populates='docentes')

    #para curso gestion
    curso_gestion_id:Mapped[int] = mapped_column(Integer,ForeignKey("curso_gestion.id"))
    curso_gestion: Mapped["CursoGestion"] = relationship("CursoGestion",back_populates='curso_gestion_materias')

    def __repr__(self):
        return f"<CursoGestionMateria> id: {self.id}"

class Periodo(db.Model, TimestampMixin):
    __tablename__ = "periodos"
    id:Mapped[int] = mapped_column(Integer,primary_key=True)
    nombre:Mapped[str] = mapped_column(String(40),nullable=False)
    grado:Mapped[int] = mapped_column(Integer,nullable=False)
    estado: Mapped[str] = mapped_column(String(3),nullable=False,default="AC")#inicialmente activo
    gestion_id:Mapped[int] = mapped_column(Integer,ForeignKey("gestiones.id"),nullable=False)
    gestion:Mapped["Gestion"] = relationship("Gestion",back_populates="periodos")
    def __repr__(self):
        return f"<Periodo> id: {self.id}"

