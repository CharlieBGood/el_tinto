import os
from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

def get_scheduler():
    jobstores = {
        'default': SQLAlchemyJobStore(url=os.getenv('DATABASE_FULL_URL'))
    }
    executors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    scheduler = BackgroundScheduler(
        jobstores=jobstores, 
        executors=executors, 
        job_defaults=job_defaults, 
        timezone=timezone('America/Bogota')
    )
    
    return scheduler
