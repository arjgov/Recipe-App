from .base import *

# Use a fast password hasher
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use a faster test runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Use an in-memory database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable debugging for tests
DEBUG = False
