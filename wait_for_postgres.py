import os
import logging
from time import time, sleep
import psycopg2
import boto3
from dotenv import load_dotenv # Only for local development

load_dotenv() # Only for local development

ssm = boto3.client(
    'ssm', 
    region_name='us-east-1', 
    #aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    #aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

check_timeout = os.getenv("POSTGRES_CHECK_TIMEOUT", 30)
check_interval = os.getenv("POSTGRES_CHECK_INTERVAL", 1)
interval_unit = "second" if check_interval == 1 else "seconds"
config = {
    "dbname": ssm.get_parameter(Name='POSTGRES_DB', WithDecryption=True)['Parameter']['Value'],
    "user": ssm.get_parameter(Name='POSTGRES_USER', WithDecryption=True)['Parameter']['Value'],
    "password": ssm.get_parameter(Name='POSTGRES_PASSWORD', WithDecryption=True)['Parameter']['Value'],
    "host": ssm.get_parameter(Name='DATABASE_URL', WithDecryption=True)['Parameter']['Value']
}

start_time = time()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def pg_isready(host, user, password, dbname):
    while time() - start_time < check_timeout:
        try:
            conn = psycopg2.connect(**vars())
            logger.info("Postgres is ready! ✨ 💅")
            conn.close()
            return True
        except psycopg2.OperationalError as err:
            logger.info(f"Postgres isn't ready. Waiting for {check_interval} {interval_unit}...")
            logger.info(err)
            sleep(check_interval)

    logger.error(f"We could not connect to Postgres within {check_timeout} seconds.")
    return False


pg_isready(**config)
