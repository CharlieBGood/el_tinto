from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from el_tinto.utils.scheduler import JOB_DEFAULTS, TIMEZONE, MISFIRE_GRACE_TIME, EXECUTORS

test_jobstores = {
    'default': SQLAlchemyJobStore(url='postgresql://postgres:local@postgres:5432/test_postgres')
}

test_scheduler = BackgroundScheduler(
    jobstores=test_jobstores,
    executors=EXECUTORS,
    job_defaults=JOB_DEFAULTS,
    timezone=TIMEZONE,
    misfire_grace_time=MISFIRE_GRACE_TIME
)
