from app import create_app
from celery import Task
from app.celery import celery

flask_app = create_app()

class CeleryPatchedTask(Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            print("running in app context")
            return super().__call__(*args, **kwargs)

celery.Task = CeleryPatchedTask