from tasks.celery_app import celery_app
import time

@celery_app.task
def process_data_task(data):
    # Simula una tarea que tarda en completarse
    time.sleep(10)
    # Procesa los datos y genera un archivo, por ejemplo
    result = f"Processed data: {data}"
    return result