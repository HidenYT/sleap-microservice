REM Активация виртуальной среды Python
cd ..\..\
call venv\Scripts\activate

REM Запуск брокера задач celery
cd .\src\
flask run --debug
