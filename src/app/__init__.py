import os
from flask import Flask
import config

def configure_blueprints(app: Flask):
    from app import api

    app.register_blueprint(api.bp)
    pass

def create_directories(app: Flask):
    os.makedirs(app.config["VIDEOS_DIR"], exist_ok=True)
    os.makedirs(app.config["DATASETS_DIR"], exist_ok=True)

def create_app(config = config):
    app = Flask(__name__)
    app.config.from_object(config)

    create_directories(app)

    from app.database import init_db
    init_db(app)

    configure_blueprints(app)


    return app