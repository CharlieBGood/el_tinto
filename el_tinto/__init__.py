import os

from configurations import importer

os.environ.setdefault("DJANGO_CONFIGURATION", os.getenv("DJANGO_CONFIGURATION", "Local"))
importer.install(check_options=True)