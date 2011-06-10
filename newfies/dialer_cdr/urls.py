from django.conf.urls.defaults import *
from django.conf import settings
from dialer_cdr.views import *


urlpatterns = patterns('',
    # VoIP Call Report urls
    (r'^voipcall_report/$', 'dialer_cdr.views.voipcall_report'),
    (r'^voipcall_report_grid/$', 'dialer_cdr.views.voipcall_report_grid'),
    (r'^export_voipcall_report/$', 'dialer_cdr.views.export_voipcall_report'),
)
