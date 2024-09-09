import os
from celery import Celery
from celery.signals import setup_logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig
    from config.celery_config import LOGGING
    dictConfig(LOGGING)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
