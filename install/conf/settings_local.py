#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public 
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
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

#TODO : Installation script should ask the timezone
TIME_ZONE = 'Europe/Madrid'

APPLICATION_DIR = os.path.dirname(globals()['__file__'])

#DATABASE SETTINGS
#=================
DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2','postgresql','mysql','sqlite3','oracle'
        'ENGINE': 'django.db.backends.sqlite3',
        # Or path to database file if using sqlite3.
        'NAME': APPLICATION_DIR + '/database/newfies-dialer.db',
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost.
                                         # Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default.
                                         # Not used with sqlite3.
        'OPTIONS': {
           'init_command': 'SET storage_engine=INNODB',
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


#PLIVO
#=====
PLIVO_DEFAULT_ANSWER_URL = 'http://SERVER_IP_PORT/api/v1/answercall/'
PLIVO_DEFAULT_HANGUP_URL = 'http://SERVER_IP_PORT/api/v1/hangupcall/'
PLIVO_DEFAULT_DIALCALLBACK_URL = 'http://SERVER_IP_PORT/api/v1/dialcallback/'
PLIVO_DEFAULT_SURVEY_ANSWER_URL = 'http://SERVER_IP_PORT/survey_finestatemachine/'

# ADD 'dummy','plivo','twilio'
NEWFIES_DIALER_ENGINE = 'dummy'

API_ALLOWED_IP = [
            '127.0.0.1', 
            'localhost', 
            #'SERVER_IP',
                ]
                
#TEXT-TO-SPEECH
#==============
ACCOUNT_LOGIN = 'EVAL_XXXX'
APPLICATION_LOGIN = 'EVAL_XXXXXXX'
APPLICATION_PASSWORD = 'XXXXXXXX'

SERVICE_URL = 'http://vaas.acapela-group.com/Services/Synthesizer'
QUALITY = '22k' # 22k, 8k, 8ka, 8kmu
TTS_ENGINE = 'FLITE' #FLITE, CEPSTRAL, ACAPELA
ACAPELA_GENDER = 'W'
ACAPELA_INTONATION = 'NORMAL'
