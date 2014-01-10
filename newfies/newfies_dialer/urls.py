#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.conf.urls import handler404, handler500, \
    include, patterns, url
from django.conf import settings
from apirest.urls import urlpatterns as urlpatterns_apirest
from agent.api_urls import urlpatterns as urlpatterns_agent_apirest
from appointment.urls import urlpatterns as urlpatterns_appointment
from frontend.urls import urlpatterns as urlpatterns_frontend
from dialer_contact.urls import urlpatterns as urlpatterns_dialer_contact
from dialer_campaign.urls import urlpatterns as urlpatterns_dialer_campaign
from dialer_cdr.urls import urlpatterns as urlpatterns_dialer_cdr
from dnc.urls import urlpatterns as urlpatterns_dnc
from user_profile.urls import urlpatterns as urlpatterns_user_profile
from survey.urls import urlpatterns as urlpatterns_survey
from dialer_audio.urls import urlpatterns as urlpatterns_dialer_audio
from frontend_notification.urls import urlpatterns as urlpatterns_frontend_notification
#from agent.urls import urlpatterns as urlpatterns_agent
#from callcenter.urls import urlpatterns as urlpatterns_callcenter
from sms_module.urls import urlpatterns as urlpatterns_sms_module
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib import admin
import os


admin.autodiscover()
dajaxice_autodiscover()

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('dialer_campaign',
                 'user_profile',
                 'survey',
                 'audiofield'),
}

urlpatterns = patterns('',
    (r'^logout/$', 'frontend.views.logout_view'),
    (r'^admin/', include(admin.site.urls)),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^admin_tools/', include('admin_tools.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
    #(r'^sentry/', include('sentry.web.urls')),
    #(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )


urlpatterns += urlpatterns_apirest
urlpatterns += urlpatterns_agent_apirest
urlpatterns += urlpatterns_frontend
urlpatterns += urlpatterns_dialer_contact
urlpatterns += urlpatterns_dialer_campaign
urlpatterns += urlpatterns_dialer_cdr
urlpatterns += urlpatterns_dnc
urlpatterns += urlpatterns_user_profile
urlpatterns += urlpatterns_survey
urlpatterns += urlpatterns_dialer_audio
urlpatterns += urlpatterns_frontend_notification
#urlpatterns += urlpatterns_agent
#urlpatterns += urlpatterns_callcenter
urlpatterns += urlpatterns_appointment
urlpatterns += urlpatterns_sms_module

urlpatterns += patterns('',
    (r'^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip(os.sep),
        'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)


handler404 = 'urls.custom_404_view'
handler500 = 'urls.custom_500_view'


def custom_404_view(request, template_name='404.html'):
    """404 error handler which includes ``request`` in the context.

    Templates: `404.html`
    Context: None
    """
    from django.template import Context, loader
    from django.http import HttpResponseServerError

    t = loader.get_template('404.html')  # Need to create a 404.html template.
    return HttpResponseServerError(t.render(Context({
        'request': request,
    })))


def custom_500_view(request, template_name='500.html'):
    """500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """
    from django.template import Context, loader
    from django.http import HttpResponseServerError

    t = loader.get_template('500.html')  # Need to create a 500.html template.
    return HttpResponseServerError(t.render(Context({
        'request': request,
    })))
