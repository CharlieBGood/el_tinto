import datetime
import os
from pytz import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from el_tinto.utils.send_mail import send_several_mails, send_warning_mail


def get_scheduler():
    """
    Get Scheduler instance

    return:
    scheduler: Scheduler object
    """
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


def schedule_mail(mail, users):
    """
    schedule mail sending.

    :params:
    mail: Mail object
    users: User queryset

    :return: None
    """
    scheduler = get_scheduler()
    scheduler.add_job(
        send_several_mails,
        trigger='date',
        run_date=mail.dispatch_date,
        args=[mail, users],
        id=str(mail.id)
    )
    scheduler.start()
    mail.programmed = True
    mail.save()


def schedule_mail_checking(mail):
    """
    schedule mail notification to admins in case mail has not been sent.

    :params:
    mail: Mail object

    :return: None
    """
    scheduler = get_scheduler()
    scheduler.add_job(
        send_warning_mail,
        trigger='date',
        run_date=mail.dispatch_date + datetime.timedelta(minutes=10),
        args=[mail],
        id=f'{str(mail.id)}_check'
    )
    scheduler.start()
