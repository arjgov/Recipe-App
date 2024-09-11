from .base import *


DEBUG = True
ALLOWED_HOSTS = ['.onrender.com','127.0.0.1', 'localhost']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
