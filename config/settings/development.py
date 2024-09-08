from .base import *


DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
