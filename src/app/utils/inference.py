import base64
import json
import os
from datetime import datetime
from typing import Iterable, Optional, Sequence

from flask import current_app
import requests
from sleap import Labels
from sqlalchemy import select
from werkzeug.exceptions import NotFound
from app.api.models import InferenceResults, SLEAPNeuralNetwork
from config import VIDEOS_DIR
from app.database import db


def save_video_from_base64(video_base64: str, file_name: str, model_uid: str) -> str:
    video_bytes = base64.b64decode(video_base64)
    _, ext = os.path.splitext(file_name)
    dt = datetime.now().strftime("%H.%M.%S.%f-%d.%m.%Y")
    result_file_name = f"{dt}-{model_uid}{ext}"
    result_path = os.path.join(VIDEOS_DIR, result_file_name)
    with open(result_path, "wb") as f:
        f.write(video_bytes)
    return result_path


def get_model_file_path(model_uid: str) -> str:
    q = select(SLEAPNeuralNetwork).where(SLEAPNeuralNetwork.uid == model_uid)
    model = db.session.scalar(q)
    if model is None:
        raise NotFound(f"Node model found with uid {model_uid}")
    return model.network_folder_path
    # return os.path.join(model.network_folder_path, "best_model.h5")


def extract_labels_dict_from_model_predictions(labels: Labels) -> "dict[int, dict[str, list[float]]]":
    result = {}
    for i, frame in enumerate(labels.labeled_frames):
        result.setdefault(frame.frame_idx, {})
        instance = frame.instances[0]
        for bodypart_node, kp in instance.nodes_points:
            result[i][bodypart_node.name] = [kp['x'], kp['y']] if kp['visible'] else [None, None]
    return result

def update_inference_results(inference_results_id: int,
                             results_dict: "dict[int, dict[str, list[float]]]"):
    q = select(InferenceResults).where(InferenceResults.id == inference_results_id)
    results = db.session.execute(q).scalar_one()
    results.results_json = json.dumps(results_dict)
    results.finished_inference_at = datetime.now()
    results.currently_running_inference = False
    db.session.commit()

def remove_inference_video(video_path: str):
    os.remove(video_path)

def find_oldest_waiting_for_inference() -> Optional[InferenceResults]:
    q = (
        select(InferenceResults)
        .where(InferenceResults.results_json == None)
        .order_by(InferenceResults.started_inference_at)
    )
    return db.session.scalar(q)

def check_any_inference_running() -> bool:
    q = select(InferenceResults).where(InferenceResults.currently_running_inference == True)
    return bool(db.session.scalars(q).all())

def find_ready_unsent_results() -> Sequence[InferenceResults]:
    q = (
        select(InferenceResults)
        .where(
            InferenceResults.results_json != None, 
            InferenceResults.sent_back == False
        )
    )
    return db.session.scalars(q).all()

def send_inference_results(results: Iterable[InferenceResults]):
    result_dict = {
        "sender": "SLEAP", 
        "results": []
    }
    for obj in results:
        result_dict["results"].append({
            "id": obj.id,
            "keypoints": json.loads(obj.results_json)
        })
    response = requests.request(
        method="POST",
        url=current_app.config["SEND_RESULTS_URL"],
        json=result_dict,
        headers={
            "Authorization": f"Bearer {current_app.config['SEND_RESULTS_TOKEN']}"
        }
    )
    if response.status_code == 200:
        for obj in results:
            obj.sent_back = True
        db.session.commit()