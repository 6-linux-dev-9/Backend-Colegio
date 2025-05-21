from app.database import db
from app.models import Curso

def seed_cursos():
    print("Cargando cursos...")
    try:
        cursos_data = [
            ("PRIMERO-A", "MAÑANA"),
            ("PRIMERO-B", "TARDE"),
            ("SEGUNDO-A", "TARDE"),
            ("SEGUNDO-B", "MAÑANA"),
            ("SEGUNDO-C", "TARDE"),
            ("TERCERO-A", "MAÑANA"),
            ("TERCERO-B", "TARDE"),
        ]

        for nombre, turno in cursos_data:
            existente = Curso.query.filter_by(nombre=nombre, turno=turno).first()
            if not existente:
                curso = Curso(
                    nombre=nombre,
                    turno=turno,
                    estado="AC"
                )
                db.session.add(curso)

        db.session.commit()
        print("✔ Cursos cargados correctamente.")
    except Exception as e:
        db.session.rollback()
        print("❌ Error al cargar cursos.")
        raise Exception(f"Error inesperado: {str(e)}")
