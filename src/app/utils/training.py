from datetime import datetime
from typing import Optional
from typing_extensions import Literal
from uuid import UUID
from sleap.nn.config import (
    TrainingJobConfig, 
    UNetConfig, 
    SingleInstanceConfmapsHeadConfig,
    HourglassConfig,
    ResNetConfig,
    LEAPConfig,
    PretrainedEncoderConfig,
)
from sqlalchemy import select

from app.api.models import SLEAPNeuralNetwork
from app.utils.datasets import DatasetInfo
from app.database import db

class TrainingConfig:
    test_fraction: float
    num_epochs: int
    backbone_model: Literal["unet", "leap", "hourglass", "resnet", "pretrained_encoder"]
    heads_sigma: float
    heads_output_stride: int
    pretrained_encoder: Optional[Literal[
        "vgg16", "vgg19", 
        "resnet18", "resnet34", "resnet50", "resnet101", "resnet152", 
        "resnext50", "resnext101", 
        "inceptionv3", "inceptionresnetv2", 
        "densenet121", "densenet169", "densenet201",
        "seresnet18", "seresnet34", "seresnet50", "seresnet101", "seresnet152", 
        "seresnext50", "seresnext101", 
        "senet154", 
        "mobilenet", "mobilenetv2",
        "efficientnetb0", "efficientnetb1", "efficientnetb2", "efficientnetb3", "efficientnetb4", "efficientnetb5", "efficientnetb6", "efficientnetb7"
    ]] = None
    learning_rate: float

    def __init__(self, config: dict):
        self.test_fraction          = config["test_fraction"]
        self.num_epochs             = config["num_epochs"]
        self.learning_rate          = config["learning_rate"]
        self.backbone_model         = config["backbone_model"]
        self.heads_sigma            = config["heads_sigma"]
        self.heads_output_stride    = config["heads_output_stride"]
        if self.backbone_model == "pretrained_encoder":
            if "pretrained_encoder" not in config or config["pretrained_encoder"] is None:
                raise IndexError("Can't use backbone 'pretrained_encoder' and have an empty 'pretrained_encoder' value in config.")
            self.pretrained_encoder = config["pretrained_encoder"]


class TrainingConfigurator:
    def __init__(self, 
                 training_config: TrainingConfig, 
                 sleap_labels_path: str, 
                 dataset_info: DatasetInfo,
                 model_name: str):
        self.training_config = training_config
        self.sleap_labels_path = sleap_labels_path
        self.dataset_info = dataset_info
        self.model_name = model_name
    
    def create_training_job_config(self) -> TrainingJobConfig:
        cfg = TrainingJobConfig()
        cfg.data.labels.training_labels = self.sleap_labels_path
        cfg.data.labels.validation_fraction = self.training_config.test_fraction


        # cfg.optimization.augmentation_config.rotate = True
        cfg.optimization.initial_learning_rate = self.training_config.learning_rate
        cfg.optimization.epochs = self.training_config.num_epochs


        if self.training_config.backbone_model == "unet":
            cfg.model.backbone.unet = UNetConfig()
        elif self.training_config.backbone_model == "hourglass":
            cfg.model.backbone.hourglass = HourglassConfig()
        elif self.training_config.backbone_model == "leap":
            cfg.model.backbone.leap = LEAPConfig()
        elif self.training_config.backbone_model == "resnet":
            cfg.model.backbone.resnet = ResNetConfig()
        elif self.training_config.backbone_model == "pretrained_encoder":
            cfg.model.backbone.pretrained_encoder = PretrainedEncoderConfig(
                self.training_config.pretrained_encoder # type: ignore
            )
        

        cfg.model.heads.single_instance = SingleInstanceConfmapsHeadConfig(
            sigma=self.training_config.heads_sigma,
            output_stride=self.training_config.heads_output_stride,
        )

        cfg.outputs.run_name = self.model_name

        return cfg


def notify_model_stoped_training(model_uid: UUID):
    q = select(SLEAPNeuralNetwork).where(SLEAPNeuralNetwork.uid == model_uid)
    nn = db.session.execute(q).scalar_one()
    nn.celery_training_task_id = None
    nn.currently_training = False
    nn.finished_training_at = datetime.now()
    db.session.commit()