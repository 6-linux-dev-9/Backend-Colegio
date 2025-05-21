from app.database import db
from app.models import Materia

def seed_materias():
    print("Cargando materias...")
    try:
        materias_nombres = [
            "MATEMÁTICAS",
            "LENGUAJE",
            "CIENCIAS NATURALES",
            "CIENCIAS SOCIALES",
            "FÍSICA",
            "QUÍMICA",
            "BIOLOGÍA",
            "EDUCACIÓN FÍSICA",
            "MÚSICA",
            "ARTE",
            "TECNOLOGÍA",
            "INFORMÁTICA",
            "INGLÉS",
            "VALORES"
        ]

        for nombre in materias_nombres:
            existente = Materia.query.filter_by(nombre=nombre).first()
            if not existente:
                materia = Materia(
                    nombre=nombre,
                    estado="AC"
                )
                db.session.add(materia)

        db.session.commit()
        print("✔ Materias cargadas correctamente.")
    except Exception as e:
        db.session.rollback()
        print("❌ Error al cargar materias.")
        raise Exception(f"Error inesperado: {str(e)}")
