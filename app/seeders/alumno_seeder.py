


from faker import Faker
from flask_bcrypt import Bcrypt
from app.database import db
from app.models import Alumno, Rol, Usuario
from app.utils.enums.entidad import RolesEnum

bcrypt = Bcrypt()
faker = Faker()
def seed_alumnos():
    print("cargando....")
    try:
        rol = Rol.query.filter_by(nombre=RolesEnum.ALUMNO).first()
        if not rol:
            rol = Rol(nombre="ALUMNO")
            db.session.add(rol)
            db.session.commit()
        for _ in range(15):
            nombre = faker.name()
            username = nombre.strip().split()[0].capitalize()
            ci = faker.passport_number()
            usuario = Usuario(
                username=username,
                nombre=nombre,
                email=f"{username}@{faker.free_email_domain()}",
                password=bcrypt.generate_password_hash("2014").decode('utf-8'),
                rol_id=rol.id,
                ci=ci,
                estado="AC"
            )
            db.session.add(usuario)
            db.session.flush()
            alumno = Alumno(
                id=usuario.id,
                rude=faker.bothify(text="RU#######")
            )
            db.session.add(alumno)
        db.session.commit()  
    except Exception as e:
        db.session.rollback()
        print("❌ Hubo un error al cargar los alumnos.")
        raise Exception(f"Error inesperado: {str(e)}")
        