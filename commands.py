# import click
# from flask.cli import with_appcontext
# from app.seeders.categoria_seeder import seed_categorias
# from app.seeders.marca_seeder import seed_marcas
# from app.seeders.modelos_seeder import seed_modelos
# from app.seeders.producto_seeder import seed_productos
# from app.seeders.rol_seeder import seed_roles
# from app.seeders.usuario_seeder import seed_usuarios

# @click.command("seed-marcas")
# @with_appcontext
# def seed_marcas_command():
#     click.echo("⏳ Insertando marcas...")
#     seed_marcas()
#     click.echo("✅ marcas insertadas.")


# @click.command("seed-categorias")
# @with_appcontext
# def seed_categorias_command():
#     click.echo("⏳ Insertando categorias...")
#     seed_categorias()
#     click.echo("✅ categorias insertadas.")

# @click.command("seed-roles")
# @with_appcontext
# def seed_roles_command():
#     click.echo("⏳ Insertando roles...")
#     seed_roles()
#     click.echo("✅ roles insertados.")

# @click.command("seed-usuarios")
# @with_appcontext
# def seed_usuarios_command():
#     click.echo("⏳ Insertando usuarios...")
#     seed_usuarios()
#     click.echo("✅ usuarios insertados.")

# @click.command("seed-modelos")
# @with_appcontext
# def seed_modelos_command():
#     seed_modelos()

# @click.command("seed-productos")
# @with_appcontext
# def seed_productos_command():
#     seed_productos()