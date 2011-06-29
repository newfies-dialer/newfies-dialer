

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
#CARROT_BACKEND = "ghettoq.taproot.Redis"
CARROT_BACKEND = "redis"


