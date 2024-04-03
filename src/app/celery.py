from celery import Celery
import config

celery = Celery(__name__)
celery.config_from_object(config)
celery.conf.timezone = 'UTC'
celery.conf.beat_schedule = {
    "check-and-run-inference": {
        "task": "app.api.tasks.check_and_run_inference",
        "schedule": 10.0
    },
    "send-inference-results-back": {
        "task": "app.api.tasks.send_inference_results_back",
        "schedule": 10.0
    }
}