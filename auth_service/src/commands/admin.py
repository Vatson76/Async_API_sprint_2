import click as click
from flask import Blueprint

from db import db
from models.users import User
from services.helpers import hash_password

commands = Blueprint('commands', __name__)


@commands.cli.command('createsuperuser')
@click.argument('name')
@click.argument('password')
def create_superuser(name, password):
    hash = hash_password(password)
    superuser = User(login=name, password=hash, is_admin=True)
    db.session.add(superuser)
    db.session.commit()
    return 'Superuser created'
