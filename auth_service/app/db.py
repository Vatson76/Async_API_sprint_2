from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qchat:qchat@localhost:54321/postgres'
    db.init_app(app)
