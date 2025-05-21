import click
from flask.cli import with_appcontext
from app.seeders.alumno_seeder import seed_alumnos
from app.seeders.curso_gestion_materia import seed_curso_gestion_materia
from app.seeders.curso_gestion_seeder import seed_curso_gestion
from app.seeders.curso_seeder import seed_cursos
from app.seeders.docente_seeder import seed_docentes
from app.seeders.gestion_seeder import seed_gestiones
from app.seeders.materia_seeder import seed_materias

@click.command("seed-alumnos")
@with_appcontext
def seed_alumnos_command():
    click.echo("⏳ Insertando alumnos...")
    seed_alumnos()
    click.echo("✅ Alumnos Insertadas.")

@click.command("seed-docentes")
@with_appcontext
def seed_docentes_command():
    click.echo("⏳ Insertando alumnos...")
    seed_docentes()
    click.echo("✅ Docentes Insertados.")


@click.command("seed-cursos")
@with_appcontext
def seed_cursos_command():
    click.echo("⏳ Insertando Cursos...")
    seed_cursos()
    click.echo("✅ Cursos Insertados.")


@click.command("seed-gestiones")
@with_appcontext
def seed_gestiones_command():
    click.echo("⏳ Insertando Gestiones...")
    seed_gestiones()
    click.echo("✅ Gestiones Insertadas.")

@click.command("seed-materias")
@with_appcontext
def seed_materias_command():
    click.echo("⏳ Insertando materias...")
    seed_materias()
    click.echo("✅ materias Insertadas.")

@click.command("seed-curso-gestion")
@with_appcontext
def seed_curso_gestion_command():
    click.echo("⏳ Insertando cursos gestion...")
    seed_curso_gestion()
    click.echo("✅ curso gestion Insertados.")

@click.command("seed-curso-gestion-materia")
@with_appcontext
def seed_curso_gestion_materia_command():
    click.echo("⏳ Insertando cursos gestion...")
    seed_curso_gestion_materia()
    click.echo("✅ curso gestion Insertados.")