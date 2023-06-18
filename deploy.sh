#!/bin/sh
cd el_tinto
source env/bin/activate
sudo pip3 install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
celery --app=el_tinto.mails worker --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
sudo systemctl restart nginx
sudo systemctl restart gunicorn