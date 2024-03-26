from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

migrate = Migrate(db=db)

def init_db(app: Flask):
    db.init_app(app)
    migrate.init_app(app)