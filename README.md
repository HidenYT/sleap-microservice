# SLEAP microservice

Веб-приложение, предоставляющее API для доступа к функционалу библиотеки <a href="https://sleap.ai">SLEAP</a> для обучения нейронных сетей с целью определения ключевых точек на теле животного.

## Обучение нейросети
Запрос запускает обучение модели на переданном датасете с указанными настройками. В ответ возвращает JSON, содержащий UUID обучаемой модели и id задачи в Celery.
<details>
<summary>
Подробнее
</summary>

Метод: `POST`

Путь: `/api/train-network`

### Поля принимаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|training_dataset|string|Обязательный|Закодированный в формате base64 датасет формата 7z|
|training_config|JSON|Обязательный|Содержит настройки обучения нейросети (описаны далее)|

#### Поля объекта в поле training_config
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|test_fraction|number|Обязательный|Доля изображений в тестовой выборке.|
|num_epochs|number|Обязательный|Целое число - количество эпох обучения.|
|learning_rate|number|Обязательный|Скорость обучения (learning rate).|
|backbone_model|string|Обязательный|Кодировщик. Должен быть указан один из: "unet", "leap", "hourglass", "resnet", "pretrained_encoder".|
|pretrained_encoder|string|Необязательный|Параметр является обязательным для случая, когда в backbone_model был выбран "pretrained_encoder". В этом случае принимается один из вариантов: <br>"vgg16", "vgg19", <br>"resnet18", "resnet34", "resnet50", "resnet101", "resnet152", <br>"resnext50", "resnext101", <br>"inceptionv3", "inceptionresnetv2", <br>"densenet121", "densenet169", "densenet201",<br>"seresnet18", "seresnet34", "seresnet50", "seresnet101", "seresnet152", <br>"seresnext50", "seresnext101", <br>"senet154", <br>"mobilenet", "mobilenetv2",<br>"efficientnetb0", "efficientnetb1", "efficientnetb2", "efficientnetb3", "efficientnetb4", "efficientnetb5". Указывает предобученную модель, используемую в качестве кодировщика.|
|heads_sigma|number|Обязательный|Параметр sigma в `SingleInstanceConfmapsHeadConfig`, размах нормального распределения вокруг ключевой точки.|
|heads_output_stride|number|Обязательный|Целое число. Шаг в выходном слое. Чем больше шаг, тем больше сжатие и меньше точность, но выше скорость.|

### Поля возвращаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|model_uid|string|Обязательный|UUID обучаемой модели.|
|task_id|string|Обязательный|id задачи Celery.|

### Пример №1
Запрос:
```JSON
{
    "training_dataset": "N3q8ryccAAQ1zQE5HGgLAQAAAAAZAAAAAAAAAN",
    "training_config": {
        "test_fraction": 0.2,
        "num_epochs": 2,
        "learning_rate": 1e-4,
        "backbone_model": "resnet",
        "heads_sigma": 1.5,
        "heads_output_stride": 4
    }
}
```
Ответ:
```JSON
{
    "model_uid": "0c4c2c8d-c33d-48db-8090-c5ca4bd332c4",
    "task_id": "9809bbf1-7158-401d-a37d-9bb407ba9b22"
}
```
### Пример №2
Запрос:
```JSON
{
    "training_dataset": "N3q8ryccAAQ1zQE5HGgLAQAAAAAZAAAAAAAAAN",
    "training_config": {
        "test_fraction": 0.2,
        "num_epochs": 2,
        "learning_rate": 1e-4,
        "backbone_model": "pretrained_encoder",
        "pretrained_encoder": "vgg16",
        "heads_sigma": 1.5,
        "heads_output_stride": 4
    }
}
```
Ответ:
```JSON
{
    "model_uid": "0c4c2c8d-c33d-48db-8090-c5ca4bd332c4",
    "task_id": "9809bbf1-7158-401d-a37d-9bb407ba9b22"
}
```
</details>

## Получение статистики обучения
Возвращает JSON с различными данными о модели (например, изменение loss на тренировочной и тестовой выборках во время обучения).
<details>
<summary>
Подробнее
</summary>

Метод: `GET`

Путь: `/api/learning-stats`

### Параметры запроса
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|model_uid|string|Обязательный|UUID модели. Можно передавать UUID как обучаемой, так и уже обученной модели. |

### Поля возвращаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|loss|JSON|Обязательный|JSON объект, содержащий номера эпох в качестве ключей и соответствующие им значения функции потерь на тренировочной выборке в качестве значений.|
|lr|JSON|Обязательный|JSON объект, содержащий номера эпох в качестве ключей и соответствующие им значения learning rate в качестве значений.|
|val_loss|JSON|Обязательный|JSON объект, содержащий номера эпох в качестве ключей и соответствующие им значения функции на тестовой выборке потерь в качестве значений.|

### Пример №1 (модель обучалась 2 эпохи)
Запрос:

`http://127.0.0.1:5000/api/learning-stats?model_uid=0c4c2c8d-c33d-48db-8090-c5ca4bd332c4`

Ответ:
```JSON
{
    "loss": {
        "0": 4.385681629180908,
        "1": 1.4176582098007202
    },
    "lr": {
        "0": 0.0001,
        "1": 0.0001
    },
    "val_loss": {
        "0": 2.272915363311768,
        "1": 0.8621147871017456
    }
}
```
### Пример №2 (модель начала обучение, но не завершила ещё ни одной эпохи)
Запрос:

`http://127.0.0.1:5000/api/learning-stats?model_uid=0c4c2c8d-c33d-48db-8090-c5ca4bd332c4`

Ответ:
```JSON
{
}
```
</details>

## Запуск нейросети на видео
Запускает выбранную обученную нейросеть на передаваемом видео. Возвращает JSON с id результата, который можно будет получить позднее, а также id задачи Celery.
<details>
<summary>
Подробнее
</summary>

Метод: `POST`

Путь: `/api/video-inference`

### Поля принимаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|video_base64|string|Обязательный|Закодированное в формате base64 видео.|
|file_name|string|Обязательный|Название видео с расширением файла.|
|model_uid|string|Обязательный| Строка с UUID обученной модели.|

### Поля возвращаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|results_id|number|Обязательный|Целое число - id результата запуска, по которому необходимо запросить результат.|

### Пример
Запрос:
```JSON
{
    "file_name": "rabbit.mp4",
    "model_uid": "0c4c2c8d-c33d-48db-8090-c5ca4bd332c4",
    "video_base64": "N3q8ryccAAQ1zQE5HGgLAQAAAAAZAAAAAAAAAN"
}
```
Ответ:
```JSON
{
    "results_id": 2
}
```
</details>

## Получение информации о нейросети
Принимает uid нейросети и возвращает информацию о ней: настройки обучения, обучается ли она в данный момент, даты и время начала и окончания обучения.
<details>
<summary>
Подробнее
</summary>

Метод: `GET`

Путь: `/api/model-info`

### Параметры запроса
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|model_uid|string|Обязательный|UUID модели. |

### Поля возвращаемого JSON
| Название | Тип | Обязательный | Описание |
|--|--|--|--|
|backbone_model|string|Обязательный|Смотреть описание в разделе "Обучение нейросети".|
|heads_output_stride|number|Обязательный|Смотреть описание в разделе "Обучение нейросети".|
|heads_sigma|number|Обязательный|Смотреть описание в разделе "Обучение нейросети".|
|learning_rate|number|Обязательный|Смотреть описание в разделе "Обучение нейросети".|
|num_epochs|string|Обязательный|Смотреть описание в разделе "Обучение нейросети".|
|pretrained_encoder|string|Необязательный|Смотреть описание в разделе "Обучение нейросети".|
|test_fraction|number|Обязательный|Смотреть описание в разделе "Обучение нейросети".|
|currently_training|boolean|Обязательный|true, если в данный момент модель обучается. false - если нет.|
|started_training_at|string|Обязательный|Строка с датой и временем начала последнего обучения нейросети. Может быть null.|
|finished_training_at|string|Обязательный|Строка с датой и временем окончания последнего обучения нейросети. Может быть null, если модель в данный момент обучается.|

### Пример
Запрос:

`http://127.0.0.1:5000/api/model-info?model_uid=0c4c2c8d-c33d-48db-8090-c5ca4bd332c4`

Ответ:
```JSON
{
    "backbone_model": "pretrained_encoder",
    "currently_training": true,
    "finished_training_at": null,
    "heads_output_stride": 4,
    "heads_sigma": 1.5,
    "learning_rate": 0.0001,
    "num_epochs": 2,
    "pretrained_encoder": "vgg19",
    "started_training_at": "Sun, 31 Mar 2024 12:58:33 GMT",
    "test_fraction": 0.2
}
```

</details>