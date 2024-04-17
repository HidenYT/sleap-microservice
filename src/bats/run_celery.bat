REM Активация виртуальной среды Python
cd ..\..\
call venv\Scripts\activate

REM Запуск брокера задач celery
cd .\src\
celery -A app.run_celery:celery worker --loglevel=info -P threads
