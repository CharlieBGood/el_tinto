#!/bin/sh
cd el_tinto
source env/bin/activate
sudo pip3 install -r requirements.txt
#python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
sudo systemctl restart nginx
sudo systemctl restart gunicorn