import os
from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


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
    timezone=timezone('America/Bogota'),
    misfire_grace_time=60*60*2,  # 60 s * 60 m * 2h
    coalesce=True
)

scheduler.start()


def schedule_mail(instance):
    """
    schedule mail sending.

    :params:
    instance: Mail object

    :return: None
    """
    mail = instance.get_mail_class()

    scheduler.add_job(
        mail.send_several_mails,
        trigger='date',
        run_date=instance.dispatch_date,
        id=str(instance.id)
    )

    instance.programmed = True
    instance.save()
