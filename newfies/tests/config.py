import os

from django.conf import settings, global_settings


#TODO : https://github.com/pinax/pinax/blob/master/tests/runner.py
# build_app_list
def configure(nose_args):
    if not settings.configured:
        # Helper function to extract absolute path
        location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), x)

        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
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
                'country_dialcode',
                'dialer_gateway',
                'dialer_campaign',
                'dialer_cdr',
                'dialer_settings',
                'user_profile',
                'common',
                'djcelery',
                'dateutil',
                #'pagination',
                'linaro_django_pagination',
                'memcache_status',
                'notification',
                'survey',
                'dialer_audio',
                'common',
                #'raven.contrib.django',
                'admin_tools_stats',
                'chart_tools',
                'south',
                'tastypie',
                'audiofield',
                'tagging',
                'adminsortable',
                'dajaxice',
                'dajax',
                'genericadmin',
            ],
            TEMPLATE_CONTEXT_PROCESSORS=(
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
            ),
            TEMPLATE_DIRS=(
                location('templates'),
            ),
            MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES + (
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
            ),
            ROOT_URLCONF='urls',
            DEBUG=False,
            SITE_ID=1,
            APPEND_SLASH=True,
            NOSE_ARGS=nose_args,
        )
