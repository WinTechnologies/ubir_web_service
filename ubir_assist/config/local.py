import os
from .common import Common

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True
    # DATABASES = {
    #     'default': {
    #         'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.postgresql_psycopg2'),
    #         'NAME': os.environ.get('POSTGRES_DATABASE', 'ubirassist'),
    #         'USER': os.environ.get('POSTGRES_USER', 'ubirassist'),
    #         'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'ubirassist'),
    #         'HOST': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
    #         'PORT': '5432',
    #     }
    # }
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS


