
#DEBUG
#=====
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

#DATABASE SETTINGS
#=================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'newfies',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
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


#PISTON
#======
PISTON_DISPLAY_ERRORS = True
PISTON_EMAIL_ERRORS = "root@localhost.localdomain"
#PISTON_IGNORE_DUPE_MODELS = True

# Use only in Debug mode. Not in production
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


#PLIVO
#=====
PLIVO_DEFAULT_ANSWER_URL='http://127.0.0.1:8000/api/dialer_cdr/answercall/'
PLIVO_DEFAULT_HANGUP_URL='http://127.0.0.1:8000/api/dialer_cdr/hangupcall/'

# ADD 'dummy','plivo','twilio'
NEWFIES_DIALER_ENGINE = 'plivo'

API_ALLOWED_IP = ['127.0.0.1' , 'localhost']
