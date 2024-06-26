from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from app.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

class SLEAPNeuralNetwork(db.Model):
    __tablename__ = "sleap_neural_network"
    uid: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    started_training_at: Mapped[Optional[datetime]]
    finished_training_at: Mapped[Optional[datetime]]
    training_config: Mapped[str]
    network_folder_path: Mapped[str]
    currently_training: Mapped[bool]
    celery_training_task_id: Mapped[Optional[str]]

class InferenceResults(db.Model):
    __tablename__ = "inference_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    results_json: Mapped[Optional[str]]
    started_inference_at: Mapped[Optional[datetime]]
    finished_inference_at: Mapped[Optional[datetime]]
    currently_running_inference: Mapped[bool]
    video_base64: Mapped[str]
    file_name: Mapped[str]
    network_uid: Mapped[UUID] = mapped_column(ForeignKey("sleap_neural_network.uid"))
    network: Mapped[SLEAPNeuralNetwork] = relationship()