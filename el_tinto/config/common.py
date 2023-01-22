import os
from os.path import join
from distutils.util import strtobool
from configurations import Configuration

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

        # Your apps
        'el_tinto.users',
        'el_tinto.mails',
        'el_tinto.web_page',
        'el_tinto.ses_sns',
        'el_tinto.tintos'

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
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            },
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
                'handlers': ['mail_admins', 'console'],
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

    TINYMCE_DEFAULT_CONFIG = {
        'plugins': "spellchecker, image, link, code, emoticons, imagetools, numlist, bullist, preview, wordcount, template",
        'toolbar': "undo redo | formatselect | "
                   "bold italic backcolor | alignleft aligncenter "
                   "alignright alignjustify | bullist numlist outdent indent template preview | ",
        "height": 500,
        'default_link_target': '_blank',
        'templates': [
            {
                'title': 'Noticia de ejemplo',
                'description': 'Plantilla de noticia',
                'content': """
                <h2><strong>Si solo tiene tiempo para un Tinto&hellip;</strong></h2>
                <p><strong>En una frase: </strong><span style="font-weight: 400;">el acoso y abuso sexual en el deporte colombiano no para.</span></p>
                <p><span style="font-weight: 400;"><img style="display: block; margin-left: auto; margin-right: auto;" src="https://www.agenciapi.co/sites/default/files/styles/imagen_principal_contenidos_2021/public/2022-10/ni.una_.menos_.mujeres.feminismo-2-e1559655965149.jpg?h=6377f7ce&amp;itok=CeUOoD5V" alt="" width="80%" /></span></p>
                <p style="text-align: center;"><em><span style="font-weight: 400;">Foto: LatFem</span></em></p>
                <p><strong>El acoso y abuso sexual</strong><span style="font-weight: 400;"> dentro del deporte colombiano se</span><a href="https://www.eltiempo.com/infografias/2022/11/AbusoEnElDeporte/index.html?28denovVer2"><span style="font-weight: 400;"> convirti&oacute;</span></a><span style="font-weight: 400;"> en un problema sin soluci&oacute;n ni justicia. Aunque son varios los estamentos deportivos que cuentan con l&iacute;neas telef&oacute;nicas para que los deportistas denuncien, cada vez hay m&aacute;s atletas que hablan y cuentan sus casos.</span></p>
                <ul>
                <li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">En enero de 2022 cuatro atletas </span><a href="https://larepublica.pe/deportes/2022/01/24/colombia-el-grave-panorama-del-acoso-y-abuso-sexual-en-el-deporte-colombiano-atmp/"><span style="font-weight: 400;">denunciaron </span></a><span style="font-weight: 400;">a Giovanny Vega Blanco, entrenador del Club Deportivo Marathon Sport de la liga de Santander, por presuntos casos de acoso y abuso sexual. Las deportistas tambi&eacute;n dijeron que Vega, adem&aacute;s de los comentarios sexuales que les hac&iacute;a cuando a&uacute;n eran menores de edad, las maltrataba f&iacute;sica y psicol&oacute;gicamente al denigrarlas, las obligaba a competir estando lesionadas y les inyectaba sustancias para mejorar su rendimiento.</span></li>
                <li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">En agosto, los padres y madres de las ni&ntilde;as, menores de edad, pertenecientes al Club Deportivo Besser en Bogot&aacute;, </span><a href="https://caracol.com.co/programa/2022/08/25/6am_hoy_por_hoy/1661441132_154664.html"><span style="font-weight: 400;">denunciaron</span></a><span style="font-weight: 400;"> que eran acosadas sexualmente por entrenadores y directivos. Entre las conversaciones &iacute;ntimas se destacan im&aacute;genes privadas que solicitaban con el fin de permitirles participar en los partidos.</span></li>
                </ul>
                <p><strong>Cifras del </strong><span style="font-weight: 400;">Ministerio del Deporte </span><a href="https://www.mindeporte.gov.co/sala-prensa/noticias-mindeporte/mindeporte-seguimiento-las-denuncias-acoso-abuso-sexual-futbolistas-bogota-traves-linea-ni-silencio"><span style="font-weight: 400;">aseguran</span></a><span style="font-weight: 400;"> que entre 2020 y julio de 2022, se presentaron 62 casos de denuncias en Colombia. 62 % de las v&iacute;ctimas son mujeres, 35 % menores de edad y el 91 % de los victimarios son hombres.&nbsp;</span></p>
                <p><strong>La cita:</strong><span style="font-weight: 400;"> &ldquo;Es triste, para m&iacute; esto no es nuevo, cada d&iacute;a los casos son m&aacute;s aberrantes. Tenemos en pesas, boxeo, atletismo, b&eacute;isbol, f&uacute;tbol. Nosotros como Ministerio hacemos toda la ruta, recogemos la denuncia y oficiamos, pero termina siendo carta muerta en la Fiscal&iacute;a&rdquo;, </span><a href="https://www.mindeporte.gov.co/sala-prensa/noticias-mindeporte/mindeporte-seguimiento-las-denuncias-acoso-abuso-sexual-futbolistas-bogota-traves-linea-ni-silencio"><span style="font-weight: 400;">dijo</span></a><span style="font-weight: 400;"> Mar&iacute;a Isabel Urrutia, ministra del Deporte.</span></p>
                <p><strong>En el mundo: </strong><span style="font-weight: 400;">en 2018 en Alemania se estableci&oacute; que el 38 % de los y las deportistas encuestados sufrieron alg&uacute;n tipo de violencia sexual; en Rep&uacute;blica Checa, el 55 % de las mujeres deportistas experiementaron violencias sexuales en el contexto deportivo.</span></p>
                <p><em><span style="font-weight: 400;">Si conoce alg&uacute;n deportista, hombre o mujer, que es v&iacute;ctima de acoso o abuso sexual, puede ayudarlo contact&aacute;ndose con la l&iacute;nea telef&oacute;nica 018000114060 o en el correo </span></em><a href="mailto:nisilencioniviolencia@mindeporte.gov.co"><em><span style="font-weight: 400;">nisilencioniviolencia@mindeporte.gov.co</span></em></a><em><span style="font-weight: 400;">.</span></em><strong>&nbsp;</strong></p>
                <p><strong>Conozca el especial completo en </strong><a href="https://www.eltiempo.com/infografias/2022/11/AbusoEnElDeporte/index.html?28denovVer2"><span style="font-weight: 400;">El Tiempo</span></a><span style="font-weight: 400;">, en </span><a href="https://larepublica.pe/deportes/2022/01/24/colombia-el-grave-panorama-del-acoso-y-abuso-sexual-en-el-deporte-colombiano-atmp/"><span style="font-weight: 400;">La Rep&uacute;blica</span></a><span style="font-weight: 400;"> encuentre la </span><strong>denuncia completa de las atletas santandereanas</strong><span style="font-weight: 400;"> y en </span><a href="https://caracol.com.co/programa/2022/08/25/6am_hoy_por_hoy/1661441132_154664.html"><span style="font-weight: 400;">Caracol</span></a><span style="font-weight: 400;">, la del </span><strong>club bogotano</strong><span style="font-weight: 400;">.</span></p>
                """
            },
            {
                'title': 'Recomendación de ejemplo',
                'description': 'Plantilla de recomendación',
                'content': """
                    <h2><strong>Estos son nuestros recomendados del d&iacute;a</strong></h2>
                    <p><strong>Un p&oacute;dcast: </strong><a href="https://treceporcien.com/"><span style="font-weight: 400;">13% pasi&oacute;n por el trabajo</span></a></p>
                    <p><a href="https://treceporcien.com/wp-content/uploads/2020/09/cropped-Logo_13_Editable-blanco-01-1.png"><span style="font-weight: 400;"><img style="display: block; margin-left: auto; margin-right: auto;" src="https://treceporcien.com/wp-content/uploads/2020/09/cropped-Logo_13_Editable-blanco-01-1.png" alt="" width="80%" /></span></a></p>
                    <p><span style="font-weight: 400;">A prop&oacute;sito de una de las historias de hoy, le recomendamos este p&oacute;dcast. Nicol&aacute;s Pinz&oacute;n y Andr&eacute;s Acevedo son las voces detr&aacute;s de 13%, pasi&oacute;n por el trabajo, un programa que cuenta historias de personas que aman lo que hacen. Y son una minor&iacute;a, pues apenas el 13 % de las personas en el mundo est&aacute; a gusto con su trabajo.</span></p>
                    <p><span style="font-weight: 400;">Si usted forma parte de quienes </span><strong>no </strong><span style="font-weight: 400;">est&aacute;n a gusto con lo que hacen, p&eacute;guele una escuchadita. De pronto encuentra respuestas a esas preguntas que lleva haci&eacute;ndose por un tiempo.&nbsp;</span></p>
                    <p><strong>Un libro: </strong><span style="font-weight: 400;">Ante todo no hagas da&ntilde;o, de Henry Marsh.</span></p>
                    <p><a href="https://http2.mlstatic.com/D_NQ_NP_734620-MCO52222096554_102022-O.jpg"><span style="font-weight: 400;"><img style="display: block; margin-left: auto; margin-right: auto;" src="https://http2.mlstatic.com/D_NQ_NP_734620-MCO52222096554_102022-O.jpg" alt="" width="40%" /></span></a></p>
                    <p><span style="font-weight: 400;">Este libro es conmovedor. Henry Marsh es un neurocirujano ingl&eacute;s que en este libro revela detalles in&eacute;ditos de su vida como m&eacute;dico. El t&iacute;tulo se basa en el juramento hipocr&aacute;tico y re&uacute;ne historias positivas, como cuando Marsh salva a un paciente de quedar en silla de ruedas o de perder la visi&oacute;n, y negativas, como cuando un peque&ntilde;o error le cuesta la vida a uno de sus pacientes.&nbsp;</span></p>
                    """
            }
        ],
        'content_style': 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
    }


    JAZZMIN_SETTINGS = {
        # Welcome text on the login screen
        "welcome_sign": "Bienvenido",
        "site_logo": "el-tinto_perfil.png",
        "login_logo": "el_tinto_logo.png",
        "site_icon": 'favicon.ico',
        "copyright": "El Tinto",
        # "related_modal_active": True,
        "show_ui_builder": False
    }

