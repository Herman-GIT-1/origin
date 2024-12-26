from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db  
from app import User, Teacher, Admin, Course, Enrollment
from flask.cli import with_appcontext
import click

@click.command(name="create_migrations", help="Initialize migration repository")
@with_appcontext
def create_migrations():
    Migrate(app, db)
migrate = Migrate(app, db)
manager = Manager(app)


manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()