import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1
app.conf.worker_concurrency = 1

app.autodiscover_tasks()