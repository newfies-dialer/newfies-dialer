#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
import os
import djcelery
djcelery.setup_loader()

# Django settings for project.
DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = (
    ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

SERVER_EMAIL = 'newfies@localhost.com'

APPLICATION_DIR = os.path.dirname(globals()['__file__'])

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
        # 'OPTIONS': {
        #    'init_command': 'SET storage_engine=INNODB',
        # }
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
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

DATETIME_FORMAT = 'Y-m-d H:i:s'

DATE_FORMAT = 'Y-m-d'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'usermedia')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/mediafiles/'

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
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'dajaxice.finders.DajaxiceFinder',
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
    #'raven.contrib.django.middleware.SentryResponseErrorIdMiddleware',
    #'raven.contrib.django.middleware.Sentry404CatchMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'pagination.middleware.PaginationMiddleware',
    'linaro_django_pagination.middleware.PaginationMiddleware',
    'common.filter_persist_middleware.FilterPersistMiddleware',
    'audiofield.middleware.threadlocals.ThreadLocals',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.csrf",
    "django.contrib.messages.context_processors.messages",
    "context_processors.newfies_version",
    #needed by Sentry
    "django.core.context_processors.request",
)

ROOT_URLCONF = 'urls'

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
#DAJAXICE_MEDIA_PREFIX = "dajax"  # http://domain.com/dajax/
#DAJAXICE_CACHE_CONTROL = 10 * 24 * 60 * 60

INSTALLED_APPS = (
    #admin tool apps
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'django.contrib.markup',
    'django_countries',
    'admin_tools_stats',
    'genericadmin',
    'south',
    'djcelery',
    'tastypie',
    'audiofield',
    'tagging',
    'adminsortable',
    'dajaxice',
    'dajax',
    'dateutil',
    #'pagination',
    'linaro_django_pagination',
    'memcache_status',
    'chart_tools',
    'country_dialcode',
    'common',
    'dialer_contact',
    'dialer_cdr',
    'dialer_audio',
    'dialer_campaign',
    'dialer_gateway',
    'dialer_settings',
    'user_profile',
    'notification',
    'survey',
    'dnc',
    #'raven.contrib.django',
    'apiplayground',
    'frontend_notification',
    'django_nvd3',
)

# Django extensions
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
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar', 'template_timings_panel',)
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + \
        ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
        'template_timings_panel.panels.TemplateTimings.TemplateTimings',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'HIDE_DJANGO_SQL': False,
        'ENABLE_STACKTRACES': True,
    }

# Django extensions
try:
    import django_extensions
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('django_extensions',)

# Nose
try:
    import nose
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('django_nose',)
    TEST_RUNNER = 'utils.test_runner.MyRunner'

# Dilla
try:
    import django_dilla
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('dilla',)

# SMS MODULE
"""
try:
    import sms
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('sms',)

try:
    import sms_module
except ImportError:
    pass
else:
    INSTALLED_APPS = INSTALLED_APPS + ('sms_module',)

#DEBUG SMS
#=========
SMSDEBUG = False
"""

#API PLAYGROUND
#==============
API_PLAYGROUND_FEEDBACK = False

#No of records per page
#=======================
PAGE_SIZE = 10

# AUTH MODULE SETTINGS
AUTH_PROFILE_MODULE = 'user_profile.UserProfile'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/pleaselog/'

#DILLA SETTINGS
#==============
DICTIONARY = "/usr/share/dict/words"
DILLA_USE_LOREM_IPSUM = False  # set to True ignores dictionary
DILLA_APPS = [
    'auth',
    #'dialer_gateway',
    'voip_app',
    'dialer_campaign',
    'dialer_cdr',
]
DILLA_SPAMLIBS = [
    #'voip_app.voip_app_custom_spamlib',
    #'dialer_campaign.dialer_campaign_custom_spamlib',
    'dialer_cdr.dialer_cdr_custom_spamlib',
]
# To use Dilla
# > python manage.py run_dilla --cycles=100


#MEMCACHE
#========
#CACHES = {
#  'default': {
#    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#    'LOCATION': '127.0.0.1:11211',
#    'KEY_PREFIX': 'newfies_',
#  }
#}

#REDIS-CACHE
#===========
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
        #'OPTIONS': {
        #    'DB': 1,
        #    'PASSWORD': 'yadayada',
        #    'PARSER_CLASS': 'redis.connection.HiredisParser'
        #},
    },
}

#CELERY SETTINGS
#===============
## Broker settings
BROKER_URL = "redis://localhost:6379/0"
#BROKER_URL = 'amqp://guest:guest@localhost:5672//'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
#REDIS_CONNECT_RETRY = True

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.

#CELERY_REDIS_CONNECT_RETRY = True
CELERY_TIMEZONE = 'Europe/Madrid'
CELERY_ENABLE_UTC = True

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

#LANGUAGES
#===========
gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('fr', gettext('French')),
    ('es', gettext('Spanish')),
    ('pt', gettext('Portuguese')),
    ('zh', gettext('Chinese')),
    ('tr', gettext('Turkish')),
    ('ja', gettext('Japanese')),
)

LOCALE_PATHS = (
    os.path.join(APPLICATION_DIR, 'locale'),
)

LANGUAGE_COOKIE_NAME = 'newfies_dialer_language'

#DJANGO-ADMIN-TOOL
#=================
ADMIN_TOOLS_MENU = 'custom_admin_tools.menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = \
    'custom_admin_tools.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = \
    'custom_admin_tools.dashboard.CustomAppIndexDashboard'
ADMIN_MEDIA_PREFIX = '/static/admin/'

#EMAIL BACKEND
#=============
# Use only in Debug mode. Not in production
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# ADD 'dummy','plivo','twilio','esl'
NEWFIES_DIALER_ENGINE = 'esl'

#TASTYPIE API
#============
API_ALLOWED_IP = ['127.0.0.1', 'localhost']

#SENTRY SETTINGS
#===============
#SENTRY_DSN = 'http://asdada:asdasd@localhost:9000/1'

#DIALER
#======
MAX_CALLS_PER_SECOND = 20  # By default configured to 20 calls per second


# Frontend widget values
CHANNEL_TYPE_VALUE = 1  # 0-Keep original, 1-Mono, 2-Stereo

# 0-Keep original, 8000-8000Hz, 16000-16000Hz, 22050-22050Hz,
# 44100-44100Hz, 48000-48000Hz, 96000-96000Hz
FREQ_TYPE_VALUE = 8000

# 0-Keep original, 1-Convert to MP3, 2-Convert to WAV, 3-Convert to OGG
CONVERT_TYPE_VALUE = 2

AUDIO_DEBUG = False

#ESL
#===
ESL_HOSTNAME = '127.0.0.1'
ESL_PORT = '8021'
ESL_SECRET = 'ClueCon'
ESL_SCRIPT = '&lua(/usr/share/newfies-lua/newfies.lua)'

#TEXT-TO-SPEECH
#==============
TTS_ENGINE = 'FLITE'  # FLITE, CEPSTRAL, ACAPELA

ACCOUNT_LOGIN = 'EVAL_XXXX'
APPLICATION_LOGIN = 'EVAL_XXXXXXX'
APPLICATION_PASSWORD = 'XXXXXXXX'

SERVICE_URL = 'http://vaas.acapela-group.com/Services/Synthesizer'
QUALITY = '22k'  # 22k, 8k, 8ka, 8kmu
ACAPELA_GENDER = 'W'
ACAPELA_INTONATION = 'NORMAL'

#DEBUG DIALER
#============
DIALERDEBUG = False
DIALERDEBUG_PHONENUMBER = 1000

#Survey in dev
#=============
SURVEYDEV = False
AMD = False

#Demo mode
#=========
#This will disable certain save, to avoid changing password
DEMO_MODE = False

#IPYTHON
#=======
IPYTHON_ARGUMENTS = [
    '--ext', 'django_extensions.management.notebook_extension',
    '--profile=nbserver',
    '--debug'
]

#GENERAL
#=======
# PREFIX_LIMIT_MIN & PREFIX_LIMIT_MAX are used to know
# how many digits are used to match against the dialcode prefix database
PREFIX_LIMIT_MIN = 2
PREFIX_LIMIT_MAX = 5

# List of phonenumber prefix to ignore, this will be remove prior analysis
PREFIX_TO_IGNORE = "+,0,00,000,0000,00000,011,55555,99999"


#IMPORT LOCAL SETTINGS
#=====================
try:
    from settings_local import *
except ImportError:
    pass
