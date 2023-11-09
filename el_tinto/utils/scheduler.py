from django.conf import settings
from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

MISFIRE_GRACE_TIME = 60*60*2  # 60 s * 60 m * 2h

JOBSTORES = {
    'default': SQLAlchemyJobStore(url=settings.DATABASE_FULL_URL)
}
EXECUTORS = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': MISFIRE_GRACE_TIME
}

TIMEZONE = timezone('America/Bogota')

MISFIRE_GRACE_TIME = 60*60*2,  # 60 s * 60 m * 2h

scheduler = BackgroundScheduler(
    jobstores=JOBSTORES,
    executors=EXECUTORS,
    job_defaults=JOB_DEFAULTS,
    timezone=TIMEZONE
)

scheduler.start()
