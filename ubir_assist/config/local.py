import os
from .common import Common, env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env.str('DBNAME'),
            'USER': env.str('DBUSER'),
            'PASSWORD': env.str('DBPASS'),
            'HOST': env.str('DBHOST'),
            'PORT': '5432'
        }
    }
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.sqlite3',
    #         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #         'OPTIONS': {
    #             'timeout': 30,
    #         }
    #     }
    # }
    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS


