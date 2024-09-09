import os
from config.settings.base import LOGS_DIR

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'celery_worker_file': {
            'level': 'DEBUG',
            'class': 'config.settings.base.TimestampedFileHandler',
            'filename': os.path.join(LOGS_DIR, 'celery_worker.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['celery_worker_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'recipe': {
            'handlers': ['celery_worker_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
