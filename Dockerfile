FROM python:3.9
LABEL maintainer='eltinto.xyz'

# Prints python outputs directly to the console
ENV PYTHONUNBUFFERED 1 

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Allows docker to cache installed dependencies between builds
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Adds our application code to the image
COPY . code
WORKDIR code

EXPOSE 8000

# Run the production server
CMD newrelic-admin run-program gunicorn --bind 0.0.0.0:$PORT --access-logfile - el_tinto.wsgi:application
