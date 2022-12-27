import os
from .common import Common
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True

    # Testing
    CORS_ALLOW_ALL_ORIGINS = True
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

    AWS_ACCESS_KEY_ID = os.getenv('DJANGO_AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('DJANGO_AWS_SECRET_ACCESS_KEY')
    # Mail
    EMAIL_BACKEND = 'django_ses.SESBackend'

    LA_CAFETERA_URL = 'http://localhost:3000'
