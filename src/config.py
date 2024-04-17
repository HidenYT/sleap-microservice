import os
from dotenv import load_dotenv

load_dotenv()

DB_ENGINE = os.getenv('DB_ENGINE')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

SQLALCHEMY_DATABASE_URI = f"{DB_ENGINE}+psycopg://{DB_USER}:{DB_PASSWORD}@"f"{DB_HOST}:{DB_PORT}/{DB_NAME}"

broker_url = os.getenv('REDIS_URL')

SLEAP_MODELS_DIR = os.path.join(os.getcwd(), "models")
UPLOADS_DIR = os.path.join(os.getcwd(), "uploads")
DATASETS_DIR = os.path.join(UPLOADS_DIR, "datasets")
VIDEOS_DIR = os.path.join(UPLOADS_DIR, "videos")