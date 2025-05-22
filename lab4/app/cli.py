import click
from flask import current_app
from . import db

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    from flask import current_app as app
    with app.app_context():
        with app.open_resource('schema.sql') as f:
            connection = db.connect()
            with connection.cursor() as cursor:
                sql_commands = f.read().decode('utf8').split(';')
                for command in sql_commands:
                    if command.strip():
                        cursor.execute(command)
            connection.commit()
        click.echo('Initialized the database.')
