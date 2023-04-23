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

    # TINY MCE CONFIGURATIONS
    TINYMCE_DEFAULT_CONFIG = {
        "relative_urls": False,
        "remove_script_host": False,
        "document_base_url": 'http://localhost:8000',
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
