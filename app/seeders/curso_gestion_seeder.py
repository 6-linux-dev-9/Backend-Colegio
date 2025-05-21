from app.models import Curso, CursoGestion, Gestion
from app.database import db

#seeder para poblar todas las gestiones con todos los cursos
def seed_curso_gestion():
    try:
        cursos = Curso.query.all()
        gestiones = Gestion.query.all()

        print("empezando a poblar....")
        for gestion in gestiones:
            print(f"ID: {gestion.id}, Nombre: {gestion.nombre}, Estado: {gestion.estado}")
            for curso in cursos:
                print(f"ID: {curso.id}, Nombre: {curso.nombre}, Estado: {curso.estado}")
                curso_gestion = CursoGestion.query.filter_by(curso_id = curso.id, gestion_id = gestion.id).first()

                if(not curso_gestion):    
                    curso_gestion = CursoGestion(
                        curso_id=curso.id,
                        gestion_id = gestion.id
                    )
                    db.session.add(curso_gestion)
                else:
                    print("curso y gestion ya esta asignada")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("❌ Error al cargar cursos.")
        raise Exception(f"Error inesperado: {str(e)}")


