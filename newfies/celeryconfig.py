
#CELERY CONFIG

SITE_ID = 1

#CARROT_BACKEND = "ghettoq.taproot.Redis"
CARROT_BACKEND = "redis"

BROKER_HOST = "localhost"  # Maps to redis host.
BROKER_PORT = 6379         # Maps to redis port.
BROKER_VHOST = "0"         # Maps to database number.

CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0
#CELERY_REDIS_CONNECT_RETRY = True
CELERY_TIMEZONE = 'Europe/London'
CELERY_ENABLE_UTC = True
