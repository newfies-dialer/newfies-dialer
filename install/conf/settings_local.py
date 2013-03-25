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

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

TIME_ZONE = 'Europe/Madrid'

APPLICATION_DIR = os.path.dirname(globals()['__file__'])

#DATABASE SETTINGS
#=================
DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2','postgresql','mysql','sqlite3','oracle'
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'DATABASENAME',
        'USER': 'DB_USERNAME',
        'PASSWORD': 'DB_PASSWORD',
        'HOST': 'DB_HOSTNAME',
        'PORT': 'DB_PORT',
        'OPTIONS': {
            #Needed on Mysql
            # 'init_command': 'SET storage_engine=INNODB',
            #Postgresql Autocommit
            'autocommit': True,
        }
    }
}

#CELERY SETTINGS
#===============
CARROT_BACKEND = 'redis'
BROKER_HOST = 'localhost'  # Maps to redis host.
BROKER_PORT = 6379         # Maps to redis port.
BROKER_VHOST = 0        # Maps to database number.

CELERY_RESULT_BACKEND = 'redis'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
#REDIS_CONNECT_RETRY = True


#EMAIL BACKEND
#=============
# Use only in Debug mode. Not in production
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#ESL
#===
ESL_HOSTNAME = 'localhost'
ESL_PORT = '8021'
ESL_SECRET = 'ClueCon'
ESL_SCRIPT = '&lua(/usr/share/newfies-lua/newfies.lua)'

#CUSTOM
#======
FS_RECORDING_PATH = '/usr/share/newfies/usermedia/recording/'

# ADD 'dummy','plivo','twilio','esl'
NEWFIES_DIALER_ENGINE = 'esl'

API_ALLOWED_IP = [
    '127.0.0.1',
    'localhost',
    #'SERVER_IP',
]

ALLOWED_HOSTS = ['SERVER_IP']

#LOGGING
#=======
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    #'root': {
    #    'level': 'WARNING',
    #    'handlers': ['sentry'],
    #},
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s || %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        # Include the default Django email handler for errors
        # This is what you'd get without configuring logging at all.
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            # But the emails are plain text by default - HTML is nicer
            'include_html': True,
        },
        'default': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/newfies/newfies-django.log',
            'formatter': 'verbose',
        },
        'default-db': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/newfies/newfies-django-db.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 20,
            'formatter': 'verbose',
        },
        #'sentry': {
        #    'level': 'ERROR',
        #    'class': 'raven.contrib.django.handlers.SentryHandler',
        #    'formatter': 'verbose'
        #},
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        # Again, default Django configuration to email unhandled exceptions
        'django': {
            'handlers': ['default'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'newfies.filelog': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['default-db'],
            'level': 'ERROR',
            'propagate': False,
        },
        #'raven': {
        #    'level': 'DEBUG',
        #    'handlers': ['console'],
        #    'propagate': False,
        #},
        #'sentry.errors': {
        #    'level': 'DEBUG',
        #    'handlers': ['console'],
        #    'propagate': False,
        #},
        'audiofield_log': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

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
