import random
from app.database import db
from app.models import CursoGestionMateria, Docente, Gestion, Materia
from sqlalchemy.orm import joinedload

def seed_curso_gestion_materia():
    try:
        gestiones = Gestion.query.options(joinedload(Gestion.cursos)).all()
        materias = Materia.query.all()
        docentes = Docente.query.all()

        for gestion in gestiones:
            cursos = gestion.cursos
            for curso_gestion in cursos:
                for materia in materias:

                    existente = CursoGestionMateria.query.filter_by(
                        curso_gestion_id=curso_gestion.id,
                        materia_id=materia.id
                    ).first()
                    if not existente:
                        docente = random.choice(docentes)
                        curso_gestion_materia = CursoGestionMateria(
                            curso_gestion_id = curso_gestion.id,
                            materia_id = materia.id,
                            docente_id = docente.id,
                            estado = "AC",
                            horario = "LUN MIE VIERNES 08:09 SAB 10:00-13:00"
                        )
                        db.session.add(curso_gestion_materia)
        db.session.commit()

        print("✅ Curso-Gestion-Materia asignado correctamente.")

    except Exception as e:
        db.session.rollback()
        raise Exception(f"ocurrio un error inesperado...{str(e)}")
    
