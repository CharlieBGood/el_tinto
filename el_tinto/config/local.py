import os
from .common import Common
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True

    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS
    INSTALLED_APPS += ('django_nose',)
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = [
        BASE_DIR,
        '-s',
        '--nologcapture',
        '--with-coverage',
        #'--with-progressive',
        '--cover-package=el_tinto'
    ]

    # Mail
    #EMAIL_HOST = 'localhost'
    #EMAIL_PORT = 1025
    #EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = 'smtp.googlemail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = os.getenv('GMAIL_USER_MAIL')
    EMAIL_HOST_PASSWORD = os.getenv('GMAIL_USER_MAIL_PASSWORD')
    EMAIL_USE_TLS = True
