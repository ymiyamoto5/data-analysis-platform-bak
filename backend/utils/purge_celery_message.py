from backend.app.worker.celery import celery_app

celery_app.control.purge()
