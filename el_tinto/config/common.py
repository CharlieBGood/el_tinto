import os
from os.path import join
from distutils.util import strtobool
from configurations import Configuration
from kombu.utils.url import safequote

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv

load_dotenv()


class Common(Configuration):
    INSTALLED_APPS = (
        'jazzmin',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # Third party apps
        'rest_framework',  # utilities for rest apis
        'rest_framework.authtoken',  # token authentication
        'django_filters',  # Filtering rest endpoints
        'django_user_agents',  # Allow device identification for requests
        'tinymce',  # WYSIWYG editor
        "corsheaders",  # CORS configuration
        'django_template_maths',  # Math in templates
        'django_celery_beat',  # Celery database storage

        # Your apps
        'el_tinto.users',
        'el_tinto.mails',
        'el_tinto.web_page',
        'el_tinto.ses_sns',
        'el_tinto.tintos',
        'el_tinto.advertisement'
    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        "corsheaders.middleware.CorsMiddleware",
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django_user_agents.middleware.UserAgentMiddleware'
    )

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = 'el_tinto.urls'
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    WSGI_APPLICATION = 'el_tinto.wsgi.application'
    DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

    # Email
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    ADMINS = (
        ('Author', 'carlosbueno1196@gmail.com'),
    )
    # Postgres
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': os.getenv("DATABASE_URL",
                              'postgres'),
            'NAME': os.getenv("POSTGRES_DB",
                              'postgres'),
            'USER': os.getenv("POSTGRES_USER",
                              'postgres'),
            'PASSWORD': os.getenv("POSTGRES_PASSWORD",
                                  'local'),
        }
    }

    # General
    APPEND_SLASH = False
    TIME_ZONE = 'America/Bogota'
    LANGUAGE_CODE = 'es-co'
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = '/'

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), 'static'))
    STATICFILES_DIRS = []
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), 'media')
    MEDIA_URL = '/media/'

    # AWS
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Mail
    EMAIL_BACKEND = 'django_ses.SESBackend'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            "DIRS": STATICFILES_DIRS,
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'el_tinto.utils.context_processor.global_variables'
                ],
            },
        },
    ]

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = strtobool(os.getenv('DJANGO_DEBUG', 'no'))

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'django.server': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(server_time)s] %(message)s',
            },
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'django.server': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'django.server',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            # 'mail_admins': {
            #     'level': 'ERROR',
            #     'class': 'django.utils.log.AdminEmailHandler'
            # },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'mails.log'),
                'formatter': 'simple'
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'propagate': True,
            },
            'django.server': {
                'handlers': ['django.server'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                # 'handlers': ['mail_admins', 'console'],
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'INFO'
            },
            'mails': {
                'handlers': ['file'],
                'level': 'INFO'
            },
            'notifications': {
                'handlers': ['file'],
                'level': 'INFO'
            },
        }
    }

    # Custom user app
    AUTH_USER_MODEL = 'users.User'

    # Django Rest Framework
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': int(os.getenv('DJANGO_PAGINATION_LIMIT', 10)),
        'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        )
    }

    # Cache
    # CACHES = {
    #     'default': {
    #         'BACKEND': 'django_redis.cache.RedisCache',
    #         'LOCATION': 'redis://127.0.0.1:6379/',
    #         'OPTIONS': {
    #             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    #         }
    #     }
    # }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

    # Name of cache backend to cache user agents. If it is not specified default
    # cache alias will be used. Set to `None` to disable caching.
    USER_AGENTS_CACHE = 'default'

    JAZZMIN_SETTINGS = {
        # Welcome text on the login screen
        "welcome_sign": "Bienvenido",
        "site_logo": "el_tinto_imagen_sin_espacios.png",
        "site_icon": 'favicon.ico',
        "login_logo": 'el_tinto_imagotipo_small.jpeg',
        "copyright": "El Tinto",
        "show_ui_builder": False
    }

    CELERY_accept_content = ['application/json']
    CELERY_task_serializer = 'json'
    CELERY_BROKER_URL = f"sqs://{safequote(AWS_ACCESS_KEY_ID)}:{safequote(AWS_SECRET_ACCESS_KEY)}@"
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
    CELERY_result_backend = None