from celery import Celery
import config

celery = Celery(__name__)
celery.config_from_object(config)