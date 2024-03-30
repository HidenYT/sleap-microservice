FROM python:3.7.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get install ffmpeg libsm6 libxext6 -y && \
    apt-get install -y libpq-dev python3-dev

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--debug", "--host=0.0.0.0"]