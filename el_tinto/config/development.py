import os
from .common import Common
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


class Development(Common):
    INSTALLED_APPS = Common.INSTALLED_APPS
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    INSTALLED_APPS += ("gunicorn",)
    CORS_ALLOW_ALL_ORIGINS = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    # http://django-storages.readthedocs.org/en/latest/index.html
    INSTALLED_APPS += ('storages',)
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = False

    # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching#cache-control
    # Response can be cached by browser and any intermediary caches (i.e. it is "public") for up to 1 day
    # 86400 = (60 seconds x 60 minutes x 24 hours)
    AWS_HEADERS = {
        'Cache-Control': 'max-age=86400, s-maxage=86400, must-revalidate',
    }

    sentry_sdk.init(
        dsn="https://69ad3a71e9eb42f9ae208aef0e12041d@o1213992.ingest.sentry.io/6353621",
        integrations=[DjangoIntegration()],
        environment='development',

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.2,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )

    LA_CAFETERA_URL = 'https://www.dev.lacafetera.eltinto.xyz'
    WEB_APP_URL = 'https://www.dev.eltinto.xyz'

    # TINY MCE CONFIGURATIONS
    TINYMCE_DEFAULT_CONFIG = {
        "relative_urls": False,
        "remove_script_host": False,
        "document_base_url": 'https://dev.eltinto.xyz',
        "plugins": "link code preview quickbars emoticons image, lists",
        "toolbar": "undo redo | bold italic | alignleft aligncenter alignright | preview |",
        "theme": "silver",
        "height": 500,
        "content_style": """
            body {
              font-family: Arial;
            }
            h1 {
              font-size: 46px;
            }
            h2 {
              font-size: 20px;
            }
            h3 {
              font-size: 18px;
              line-height: 150%;
              font-weight: 400
            }
            p {
                line-height: 150%;
                font-size: 16px;
            }
            li {
                font-size: 16px;
            }
            a {
              color: #fca311;
            }
            a div {
              background-color: #5044e4; 
              border-radius: 12px; 
              height: 45px;
              color: #FFFFFF;
              font-size: 18px;
              border: none;
              cursor: pointer;
            }
            .logo-subtitle{
              text-align: center;
              font-size: 23px;
              font-family: 'Raleway'
            }
            .logo-title{
              display: block;
              margin: 20px auto;
              width: 60%
            }
            .main {
              padding: 20px 0;
            }
            @media only screen and (min-width: 768px) {
              .main {
                padding: 20px 20%;
              }
              .logo-title{
                display: block;
                margin: 40px auto 20px auto;
                width: 40%
              }
              .logo-subtitle{
                text-align: center;
                font-size: 28px;
                font-family: 'Raleway'
              }
            }
        """
    }

    # Stripe products
    COFFEE_SEED_STRIPE_CODE = 'prod_OZPWtHd1Ni7Ldv'
    COFFEE_BEEN_STRIPE_CODE = 'prod_OZQYdJJny3qbgc'
    TINTO_STRIPE_CODE = 'prod_OZQZS9HxRi5a4n'
    EXPORTATION_COFFEE_STRIPE_CODE = 'prod_OZQaXRbIbt6w80'

    # SQS
    # CELERY_TASK_DEFAULT_QUEUE = 'dev_mails'