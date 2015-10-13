#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#
import os
import djcelery
from kombu import Queue

djcelery.setup_loader()

# Django settings for project.
DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = (
    ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

SERVER_EMAIL = 'newfies@localhost.com'

APPLICATION_DIR = os.path.dirname(globals()['__file__']) + '/../'

DATABASES = {
    'default': {
        # 'postgresql_psycopg2','postgresql','sqlite3','oracle', 'django.db.backends.mysql'
        'ENGINE': 'django.db.backends.sqlite3',
        # Database name or path to database file if using sqlite3.
        'NAME': APPLICATION_DIR + '/database/newfies-dialer.db',
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Not used with sqlite3.
        'PORT': '',                      # Not used with sqlite3.
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# set use of timezone true or false
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

DATETIME_FORMAT = 'Y-m-d H:i:s'

DATE_FORMAT = 'Y-m-d'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(APPLICATION_DIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(APPLICATION_DIR, 'usermedia')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/usermedia/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # os.path.join(APPLICATION_DIR, "resources"),
    ("newfies", os.path.join(APPLICATION_DIR, "resources")),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'dajaxice.finders.DajaxiceFinder',
    'djangobower.finders.BowerFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ujau$^uei_ak=@-v8va(&@q_sc0^1nn*qpwyc-776n&qoam@+v'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)


MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'linaro_django_pagination.middleware.PaginationMiddleware',
    'django_lets_go.filter_persist_middleware.FilterPersistMiddleware',
    'audiofield.middleware.threadlocals.ThreadLocals',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.csrf",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    # newfies custom context_processors
    "context_processors.newfies_version",
    "context_processors.newfies_common_template_variable",
    # django-notification
    "notification.context_processors.notification",
    # needed by Sentry
    "django.core.context_processors.request",
)

WSGI_APPLICATION = 'newfies_dialer.wsgi.application'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

ROOT_URLCONF = 'newfies_dialer.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(APPLICATION_DIR, 'templates'),
)

INTERNAL_IPS = ('127.0.0.1',)

ALLOWED_HOSTS = ['127.0.0.1']

DAJAXICE_MEDIA_PREFIX = "dajaxice"
# DAJAXICE_MEDIA_PREFIX = "dajax"  # http://domain.com/dajax/
# DAJAXICE_CACHE_CONTROL = 10 * 24 * 60 * 60

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sites',
    'registration',
    # admin tool apps
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_countries',
    'admin_tools_stats',
    'genericadmin',
    'mailer',
    # 'south',
    'djcelery',
    'audiofield',
    # Tagging broken with Django 1.7
    # 'tagging',
    'adminsortable',
    'dajaxice',
    'dajax',
    'dateutil',
    'linaro_django_pagination',
    # 'pagination',
    # 'memcache_status',
    'country_dialcode',
    'django_lets_go',
    'sms',
    'mod_sms',
    'dialer_contact',
    'dialer_audio',
    'dialer_campaign',
    'dialer_cdr',
    'dialer_gateway',
    'dialer_settings',
    'user_profile',
    'notification',
    'survey',
    'dnc',
    'frontend',
    'maintenance',
    # 'agent',
    # 'callcenter',
    'calendar_settings',
    'appointment',
    'mod_mailer',
    'mod_utils',
    'frontend_notification',
    'django_nvd3',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'djangobower',
    'activelink',
    'bootstrap3_datetime',
    'crispy_forms',
    'bootstrapform',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# gunicorn
try:
    import gunicorn
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('gunicorn',)

# Redisboard
try:
    import redisboard
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('redisboard',)

# Debug Toolbar
try:
    import debug_toolbar
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar', )
    # INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar', 'template_timings_panel',)
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + \
        ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        # StaticFilesPanel broken https://github.com/django-debug-toolbar/django-debug-toolbar/issues/503
        # 'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        # 'template_timings_panel.panels.TemplateTimings.TemplateTimings',
    ]
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'HIDE_DJANGO_SQL': False,
        'ENABLE_STACKTRACES': True,
        'SQL_WARNING_THRESHOLD': 100,   # milliseconds
    }
    DEBUG_TOOLBAR_PATCH_SETTINGS = False

# Django extensions
try:
    import django_extensions
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('django_extensions',)

# Default Test Runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Nose
# TODO: Re-Enable Nose as it s actually broken
# try:
#     import nose
#     INSTALLED_APPS = INSTALLED_APPS + ('django_nose',)
#     TEST_RUNNER = 'utils.test_runner.MyRunner'
# except ImportError:
#     pass

# No of records per page
# =======================
PAGE_SIZE = 10

# AUTH MODULE SETTINGS
AUTH_PROFILE_MODULE = 'user_profile.UserProfile'
# AUTH_USER_MODEL = 'user_profile.UserProfile'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# MEMCACHE
# ========
# CACHES = {
#  'default': {
#    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#    'LOCATION': '127.0.0.1:11211',
#    'KEY_PREFIX': 'newfies_',
#  }
# }


# REST FRAMEWORK
# ==============
REST_FRAMEWORK = {
    # 'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGINATE_BY': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # 'DEFAULT_THROTTLE_CLASSES': (
    #    'rest_framework.throttling.SimpleRateThrottle',
    # ),
    # 'DEFAULT_THROTTLE_RATES': {
    #    'anon': '100/day',
    #    'user': '1000/day'
    # }
}

# REDIS-CACHE
# ===========
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
    },
}

# CELERY SETTINGS
# ===============
# Broker settings Redis
BROKER_URL = "redis://localhost:6379/0"
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
# REDIS_CONNECT_RETRY = True
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# BROKER_URL = 'amqp://newfiesdialer:mypassword@localhost:5672//newfiesdialer'
# CELERY_RESULT_BACKEND = "amqp://newfiesdialer:mypassword@localhost:5672//newfiesdialer"

# Using the database to store task state and results.
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.

# CELERY_REDIS_CONNECT_RETRY = True
CELERY_TIMEZONE = 'Europe/Madrid'
CELERY_ENABLE_UTC = True
CELERY_ACCEPT_CONTENT = ['json', 'pickle']

REDIS_DB = 0
# REDIS_CONNECT_RETRY = True

CELERY_DEFAULT_QUEUE = 'newfies'
CELERY_DEFAULT_EXCHANGE = "newfies_tasks"
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"
CELERY_DEFAULT_ROUTING_KEY = "task.newfies"
CELERY_QUEUES = {
    'newfies': {
        'binding_key': '#',
    },
}

CELERY_DEFAULT_QUEUE = 'default'
# Define list of Queues and their routing keys
CELERY_QUEUES = (
    Queue('default', routing_key='task.#'),
    Queue('sms_tasks', routing_key='mod_sms.#'),
    Queue('appointment', routing_key='appointment.#'),
)
CELERY_DEFAULT_EXCHANGE = 'tasks'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_DEFAULT_ROUTING_KEY = 'task.default'

# python manage.py celeryd -EB -l info --purge --queue=sms_tasks
# Define tasks and which queue they will use with their routing key
CELERY_ROUTES = {
    'mod_sms.tasks.sms_campaign_running': {
        'queue': 'sms_tasks',
        'routing_key': 'mod_sms.sms_campaign_running',
    },
}

"""
from datetime import timedelta
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    "runs-every-second": {
        "task": "dialer_campaign.tasks.campaign_running",
        "schedule": timedelta(seconds=1),
        #"args": (50)
    },
}
"""

# LANGUAGES
# ===========
gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('fr', gettext('French')),
    ('es', gettext('Spanish')),
    ('pt', gettext('Portuguese')),
    ('zh', gettext('Chinese')),
    ('tr', gettext('Turkish')),
    ('ja', gettext('Japanese')),
    ('uk', gettext('Ukrainian')),
)

LOCALE_PATHS = (
    os.path.join(APPLICATION_DIR, 'locale'),
)

LANGUAGE_COOKIE_NAME = 'newfies_dialer_language'

# DJANGO-ADMIN-TOOL
# =================
ADMIN_TOOLS_MENU = 'custom_admin_tools.menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'custom_admin_tools.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'custom_admin_tools.dashboard.CustomAppIndexDashboard'
ADMIN_MEDIA_PREFIX = '/static/admin/'


# DJANGO REGISTRATION
# ===================
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_EMAIL_SUBJECT_PREFIX = '[Newfies-Dialer] '
SEND_ACTIVATION_EMAIL = True
REGISTRATION_AUTO_LOGIN = False
# indicating whether registration of new accounts is currently permitted
REGISTRATION_OPEN = True


# EMAIL BACKEND
# =============
# Use only in Debug mode. Not in production
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
MAILER_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# EMAIL_ADMIN will be used for forget password email sent
EMAIL_ADMIN = 'newfies_admin@localhost.com'

# ADD 'dummy','plivo','twilio','esl'
NEWFIES_DIALER_ENGINE = 'esl'

# DIALER
# ======
# NOTE: MAX_CALLS_PER_SECOND is no longer implemented
# MAX_CALLS_PER_SECOND = 20  # By default configured to 20 calls per second

# Number of time the spooling tasks will be run per minute,
# value like 10 will allow not waiting too long for 1st calls
HEARTBEAT_MIN = 1  # accepted value from 1 to 10

# Delay outbound call of X seconds
DELAY_OUTBOUND = 0

# Audio Convertion
# ================

# Frontend widget values
CHANNEL_TYPE_VALUE = 1  # 0-Keep original, 1-Mono, 2-Stereo

# 0-Keep original, 8000-8000Hz, 16000-16000Hz, 22050-22050Hz,
# 44100-44100Hz, 48000-48000Hz, 96000-96000Hz
FREQ_TYPE_VALUE = 8000

# 0-Keep original, 1-Convert to MP3, 2-Convert to WAV, 3-Convert to OGG
CONVERT_TYPE_VALUE = 2

AUDIO_DEBUG = False

# ESL
# ===
ESL_HOSTNAME = '127.0.0.1'
ESL_PORT = '8021'
ESL_SECRET = 'ClueCon'
ESL_SCRIPT = '&lua(/usr/share/newfies-lua/newfies.lua)'

# DIAL SETTINGS
# =============
# EARLY_MEDIA = "bridge_early_media=true"
EARLY_MEDIA = "ignore_early_media=true"

# TEXT-TO-SPEECH
# ==============
TTS_ENGINE = 'FLITE'  # FLITE, CEPSTRAL, ACAPELA, MSTRANSLATOR

# ACAPELA SPECIFIC SETTINGS
ACCOUNT_LOGIN = 'EVAL_XXXX'
APPLICATION_LOGIN = 'EVAL_XXXXXXX'
APPLICATION_PASSWORD = 'XXXXXXXX'
SERVICE_URL = 'http://vaas.acapela-group.com/Services/Synthesizer'
QUALITY = '22k'  # 22k, 8k, 8ka, 8kmu
ACAPELA_GENDER = 'W'
ACAPELA_INTONATION = 'NORMAL'

# MSTRANSLATOR SPECIFIC SETTINGS
CLIENT_ID = 'XXXXXXXXXXXX'
CLIENT_SECRET = 'YYYYYYYYYYYYYY'

# DEBUG DIALER
# ============
DIALERDEBUG = False
DIALERDEBUG_PHONENUMBER = 1000


# Survey in dev
# =============
SURVEYDEV = False
AMD = False

# Demo mode
# =========
# This will disable certain save, to avoid changing password
DEMO_MODE = False

# IPYTHON
# =======
IPYTHON_ARGUMENTS = [
    '--ext', 'django_extensions.management.notebook_extension',
    '--profile=nbserver',
    '--debug'
]

# GENERAL
# =======
# PREFIX_LIMIT_MIN & PREFIX_LIMIT_MAX are used to know
# how many digits are used to match against the dialcode prefix database
PREFIX_LIMIT_MIN = 2
PREFIX_LIMIT_MAX = 5

# List of phonenumber prefix to ignore, this will be remove prior analysis
PREFIX_TO_IGNORE = "+,0,00,000,0000,00000,011,55555,99999"

# CORS (Cross-Origin Resource Sharing)
# ====================================

# if True, the whitelist will not be used and all origins will be accepted
CORS_ORIGIN_ALLOW_ALL = True

# specify a list of origin hostnames that are authorized to make a cross-site HTTP request
# CORS_ORIGIN_WHITELIST = ()

# specify a regex list of origin hostnames that are authorized to make a cross-site HTTP request
# CORS_ORIGIN_REGEX_WHITELIST = ('^http?://(\w+\.)?google\.com$', )

# specify the allowed HTTP methods that can be used when making the actual request
CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
)


# specify which non-standard HTTP headers can be used when making the actual request
CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
)

CORS_ORIGIN_WHITELIST = (
    'hostname.example.com',
)
# specify which HTTP headers are to be exposed to the browser
CORS_EXPOSE_HEADERS = ()

# specify whether or not cookies are allowed to be included
CORS_ALLOW_CREDENTIALS = False

# Django-bower
# ------------
# Specifie path to components root (you need to use absolute path)
BOWER_COMPONENTS_ROOT = os.path.join(APPLICATION_DIR, 'components')

BOWER_PATH = '/usr/bin/bower'

BOWER_INSTALLED_APPS = (
    'jquery#2.0.3',
    'jquery-ui#~1.10.3',
    'bootstrap#3.0.3',
    'bootstrap-switch#2.0.0',
    'bootbox#4.1.0',
    'd3#3.3.6',
    'nvd3#1.1.12-beta',
    'components-font-awesome#4.0.3',
    'vis#3.7.1',
)

# South
# -----
SOUTH_MIGRATION_MODULES = {
    'authtoken': 'rest_framework.authtoken.south_migrations',
}

# Need to build documentation with Django 1.6
LOGGING_CONFIG = None

# DAJAXICE setting
# Not Include XmlHttpRequest.js inside dajaxice.core.js
DAJAXICE_XMLHTTPREQUEST_JS_IMPORT = False

# IMPORT LOCAL SETTINGS
# =====================
try:
    from settings_local import *
except ImportError:
    pass
