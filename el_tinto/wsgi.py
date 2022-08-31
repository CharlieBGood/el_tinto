"""
WSGI config for el_tinto project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/gunicorn/
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "el_tinto.config")
os.environ.setdefault("DJANGO_CONFIGURATION", os.getenv("DJANGO_CONFIGURATION", "Production"))

from configurations.wsgi import get_wsgi_application  # noqa
application = get_wsgi_application()
