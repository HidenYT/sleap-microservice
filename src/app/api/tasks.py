from uuid import UUID
import sleap
from app.celery import celery
import os
from sleap.nn.training import Trainer
from sleap import Labels
from app.utils.datasets import create_sleap_labels_from_csv, extract_dataset_from_base64
from app.utils.inference import extract_labels_dict_from_model_predictions, get_model_file_path, remove_inference_video, save_video_from_base64, update_inference_results
from app.utils.training import TrainingConfig, TrainingConfigurator, notify_model_stoped_training
from config import DATASETS_DIR


@celery.task
def train_network_task(training_dataset_base64: str, 
                       training_config: dict, 
                       model_uid: UUID,
                       model_directory_name: str):
    dataset_info = extract_dataset_from_base64(training_dataset_base64, 
                                               path=os.path.join(
                                                   DATASETS_DIR, 
                                                   model_directory_name
                                                ))

    sleap_labels = create_sleap_labels_from_csv(dataset_info.labels_csv_path)

    sleap_labels_path = os.path.join(dataset_info.path, "sleap_labels.slp")
    sleap_labels.save(sleap_labels_path)

    training_config_obj = TrainingConfig(training_config)

    sleap_job_config = TrainingConfigurator(training_config_obj, sleap_labels_path, dataset_info, str(model_uid))

    trainer = Trainer.from_config(sleap_job_config.create_training_job_config())

    trainer.train()

    notify_model_stoped_training(model_uid)


@celery.task
def run_video_inference(video_base64: str,
                        file_name: str,
                        model_uid: UUID,
                        inference_results_id: int):
    
    video_file_path = save_video_from_base64(video_base64, file_name, str(model_uid))

    video = sleap.load_video(video_file_path)
    model_file_path = get_model_file_path(str(model_uid))
    print(model_file_path)
    predictor = sleap.load_model(model_file_path)

    print(f"Started inference #{inference_results_id}")

    predictions: Labels = predictor.predict(video) # type: ignore
    
    predictions_dict = extract_labels_dict_from_model_predictions(predictions)

    update_inference_results(inference_results_id, predictions_dict)
    video.backend._reader_.release()
    remove_inference_video(video_file_path)

    print(f"Finished inference #{inference_results_id}")
