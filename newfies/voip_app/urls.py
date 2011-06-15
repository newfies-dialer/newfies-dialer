from django.conf.urls.defaults import *
from django.conf import settings
from voip_app.views import *


urlpatterns = patterns('voip_app.views',
(r'^voipapp/$', 'voipapp_list'),
(r'^voipapp_grid/$', 'voipapp_grid'),
(r'^voipapp/add/$', 'voipapp_add'),
(r'^voipapp/del/(.+)/$', 'voipapp_del'),
(r'^voipapp/(.+)/$', 'voipapp_change'),
)

