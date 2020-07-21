"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import get_default_application

if os.getenv('DJANGO_ENV') == 'production':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ubir_assist.config")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Production")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ubir_assist.config")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

import configurations
configurations.setup()

django.setup()
application = get_default_application()
