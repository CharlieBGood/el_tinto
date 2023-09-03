# import os
#
# from celery import Celery
#
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "el_tinto.config")
# os.environ.setdefault("DJANGO_CONFIGURATION", "Local")
#
# from configurations import importer
# importer.install()
#
# app = Celery("mails")
# app.config_from_object("django.conf:settings", namespace="CELERY")
# app.autodiscover_tasks()