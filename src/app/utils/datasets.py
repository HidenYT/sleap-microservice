from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
import base64
from typing import Optional
from uuid import UUID, uuid4
import py7zr
import os
from sleap.io.format.filehandle import FileHandle
from app.utils.labels_adapter import ACDCsvAdaptor
from sleap import Labels

from config import DATASETS_DIR

@dataclass
class DatasetInfo:
    path: str
    labels_csv_path: str

def generate_model_folder_name(model_uuid: UUID) -> str:
    return "{dt}-{uuid}".format(
        dt=datetime.now().strftime("%H.%M.%S.%f-%d.%m.%Y"),
        uuid=model_uuid,
    )

def extract_dataset_from_base64(dataset_base64: str, path: Optional[str] = None) -> DatasetInfo:
    """Распаковывает датасет из base64 строки и возвращает `DatasetInfo` - пару путей:
    - Путь к папке с датасетом;
    - Путь к файлу `labels.csv`"""
    training_dataset = base64.b64decode(dataset_base64)
    buf = BytesIO(training_dataset)
    if path is None:
        path = os.path.join(DATASETS_DIR, generate_model_folder_name(uuid4()))
    with py7zr.SevenZipFile(buf) as archive:
        archive.extract(path)
    return DatasetInfo(path, os.path.join(path, "labels.csv"))


def create_sleap_labels_from_csv(labels_csv_path: str) -> Labels:
    """Создаёт объект `Labels` для SLEAP из файла `labels.csv`"""
    fh = FileHandle(labels_csv_path)
    adapter = ACDCsvAdaptor()
    return adapter.read(fh)