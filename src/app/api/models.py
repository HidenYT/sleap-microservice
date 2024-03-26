from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from app.database import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

class SLEAPNeuralNetwork(db.Model):
    __tablename__ = "sleap_neural_network"
    uid: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    network_folder_path: Mapped[str]
    currently_training: Mapped[bool]
    celery_training_task_id: Mapped[Optional[str]]

class InferenceResults(db.Model):
    __tablename__ = "inference_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    results_json: Mapped[Optional[str]]
    network_uid: Mapped[UUID] = mapped_column(ForeignKey("sleap_neural_network.uid"))
    network: Mapped[SLEAPNeuralNetwork] = relationship()