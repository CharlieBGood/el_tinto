import os
from .common import Common
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True

    # Testing
    CORS_ALLOW_ALL_ORIGINS = True
    INSTALLED_APPS = Common.INSTALLED_APPS

    LA_CAFETERA_URL = 'http://localhost:3000'
    WEB_APP_URL = 'http://localhost:3000'
    SERVER_URL = 'http://localhost:8000'

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

    # Stripe products
    COFFEE_BEAN_STRIPE_CODE = 'prod_OZPWtHd1Ni7Ldv'
    GROUND_COFFEE_STRIPE_CODE = 'prod_OZQYdJJny3qbgc'
    TINTO_STRIPE_CODE = 'prod_OZQZS9HxRi5a4n'
    EXPORTATION_COFFEE_STRIPE_CODE = 'prod_OZQaXRbIbt6w80'


    # CELERY_TASK_DEFAULT_QUEUE = 'dev_mails'
