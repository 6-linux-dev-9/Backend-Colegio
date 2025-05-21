import click

from app.seeders.alumno_seeder import seed_alumnos
from app.seeders.docente_seeder import seed_docentes


@click.command("seed-all")
def seed_all_seeder_command():
    try:
        click.echo("🚀 Ejecutando seeders en orden...")
        click.echo("🚀 Ejecutando Seeder de alumnos...")
        seed_alumnos()
        click.echo("🚀 Ejecutando Seeder de docentes...")
        seed_docentes()




        click.echo("✅ Todos los datos han sido insertados correctamente.")
    except Exception as e:
        click.echo(f"❌ Error general en el seeder: {str(e)}")