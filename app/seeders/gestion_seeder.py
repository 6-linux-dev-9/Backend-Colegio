from app.database import db
from app.models import Gestion

def seed_gestiones():
    print("Cargando gestiones...")
    try:
        gestiones_nombres = [f"{i}-2025" for i in range(1, 5)]  # ["1-2025", ..., "4-2025"]

        for nombre in gestiones_nombres:
            existente = Gestion.query.filter_by(nombre=nombre).first()
            if not existente:
                gestion = Gestion(
                    nombre=nombre,
                    estado="AC"
                )
                db.session.add(gestion)

        db.session.commit()
        print("✔ Gestiones cargadas correctamente.")
    except Exception as e:
        db.session.rollback()
        print("❌ Error al cargar gestiones.")
        raise Exception(f"Error inesperado: {str(e)}")
