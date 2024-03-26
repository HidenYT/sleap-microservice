from uuid import UUID

from sqlalchemy import select

from app.api.models import SLEAPNeuralNetwork

from app.database import db

import os

import pandas as pd

from werkzeug.exceptions import BadRequest

def get_model_learning_stats(model_uid: UUID) -> "dict[str, dict[str, float]]":
    q = select(SLEAPNeuralNetwork).where(SLEAPNeuralNetwork.uid == model_uid)
    model = db.session.scalar(q)
    if model is None:
        raise BadRequest(f"A model with uid {model_uid} does not exist.")
    stats_file = os.path.join(model.network_folder_path, "training_log.csv")
    print(stats_file)
    if not os.path.exists(stats_file):
        return {}
    df = pd.read_csv(stats_file, header=[0])
    epoch_nums = list(map(int, df["epoch"]))
    bodyparts = df.columns[1:]
    bp_name_format = "{bp} loss" if "loss" not in bodyparts else "{bp}"
    result = {}
    for bp in bodyparts:
        result[bp_name_format.format(bp=bp)] = dict(zip(epoch_nums, df[bp]))
    return result


