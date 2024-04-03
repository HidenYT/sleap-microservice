from datetime import datetime
import json
from uuid import UUID, uuid4

from sqlalchemy import select
from app.api.models import InferenceResults, SLEAPNeuralNetwork
from app.api.tasks import train_network_task
from app.utils.datasets import generate_model_folder_name
from app.utils.model_info import get_model_info, get_model_learning_stats
from app.utils.training import notify_model_stoped_training
from config import SLEAP_MODELS_DIR
from . import bp
from flask import request
import os
from app.database import db
from werkzeug.exceptions import NotFound, Conflict
from celery.result import AsyncResult

@bp.post("/train-network")
def train_network():

    data: dict = request.json

    # Base64 датасета в формате 7z
    training_dataset_base64 = data["training_dataset"]

    # Параметры обучения
    training_config = data["training_config"]

    model_uid = uuid4()
    folder_name = generate_model_folder_name(model_uid)
    model_folder_path = os.path.join(SLEAP_MODELS_DIR, str(model_uid))
    sleap_nn = SLEAPNeuralNetwork()
    sleap_nn.started_training_at = datetime.now()
    sleap_nn.uid = model_uid
    sleap_nn.network_folder_path = model_folder_path
    sleap_nn.currently_training = True
    sleap_nn.training_config = json.dumps(training_config)
    
    process: AsyncResult = train_network_task.delay(training_dataset_base64, training_config, model_uid, folder_name)
    sleap_nn.celery_training_task_id = process.id
    
    db.session.add(sleap_nn)
    db.session.commit()

    return {"model_uid": model_uid, "task_id": process.id}

@bp.post("/video-inference")
def video_inference():
    data: dict = request.json

    video_base64 = data["video_base64"]

    file_name = data["file_name"]

    model_uid = data["model_uid"]
    
    q_model = select(SLEAPNeuralNetwork).where(SLEAPNeuralNetwork.uid == model_uid)
    nn = db.session.scalar(q_model)
    if nn is None:
        raise NotFound(f"No model with uid {model_uid}")
    if nn.currently_training:
        raise Conflict(f"Model with uid {model_uid} is currently being trained so it can not run inference")
    inference_results = InferenceResults()
    inference_results.network_uid = model_uid
    inference_results.started_inference_at = datetime.now()
    inference_results.currently_running_inference = False
    inference_results.video_base64 = video_base64
    inference_results.file_name = file_name
    db.session.add(inference_results)
    db.session.commit()
    return {"results_id": inference_results.id}

@bp.get("/learning-stats")
def get_learning_stats():
    uid = request.args.get("model_uid")
    if uid is None:
        raise NotFound("You should provide model_uid in order to retrieve leraning stats of a model")
    return get_model_learning_stats(UUID(uid))

@bp.get("/model-info")
def model_info():
    model_uid = request.args.get("model_uid")
    if model_uid is None:
        raise NotFound("You should provide model_uid in order to retrieve information about a model.")
    return get_model_info(UUID(model_uid))

@bp.post("/stop-training")
def stop_training():
    model_uid = request.json.get("model_uid")
    if model_uid is None:
        raise NotFound("You should provide model_uid in order to revoke model learning")
    model_uid = UUID(model_uid)
    q = select(SLEAPNeuralNetwork).where(SLEAPNeuralNetwork.uid == model_uid)
    try:
        model = db.session.execute(q).scalar_one()
        if not model.currently_training:
            raise NotFound(f"No learning processes with model uid {model_uid}")
        from app.celery import celery
        celery.control.revoke(model.celery_training_task_id)
        notify_model_stoped_training(model_uid)
    except:
        raise NotFound(f"No learning processes with model uid {model_uid}")
    return {"success": f"Successfully terminated learning process of model with uid {model_uid}"}