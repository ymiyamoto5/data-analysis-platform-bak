from celery import Celery

celery_app = Celery("worker")
celery_app.config_from_object("backend.app.worker.celeryconfig")
