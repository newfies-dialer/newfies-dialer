from django.conf.urls.defaults import *
from django.conf import settings
from voice_app.views import *


urlpatterns = patterns('voice_app.views',
(r'^voiceapp/$', 'voiceapp_list'),
(r'^voiceapp_grid/$', 'voiceapp_grid'),
(r'^voiceapp/add/$', 'voiceapp_add'),
(r'^voiceapp/del/(.+)/$', 'voiceapp_del'),
(r'^voiceapp/(.+)/$', 'voiceapp_change'),
)

