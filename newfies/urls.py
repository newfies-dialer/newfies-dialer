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
from django.conf.urls.defaults import handler404, handler500, \
                                    include, patterns
from django.conf import settings
from django.conf.urls.i18n import *
from dialer_campaign.urls import urlpatterns as urlpatterns_dialer_campaign
from dialer_cdr.urls import urlpatterns as urlpatterns_dialer_cdr
from user_profile.urls import urlpatterns as urlpatterns_user_profile
from voice_app.urls import urlpatterns as urlpatterns_voice_app
from survey.urls import urlpatterns as urlpatterns_survey
from tastypie.api import Api
from api.user_api import UserResource
from api.voiceapp_api import VoiceAppResource
from api.gateway_api import GatewayResource
from api.content_type_api import ContentTypeResource
from api.phonebook_api import PhonebookResource
from api.campaign_api import CampaignResource
from api.bulk_contact_api import BulkContactResource
from api.campaign_delete_cascade_api import CampaignDeleteCascadeResource
from api.campaign_subscriber_api import CampaignSubscriberResource
from api.campaignsubscriber_per_campaign_api import \
                                    CampaignSubscriberPerCampaignResource
from api.callrequest_api import CallrequestResource
from api.answercall_api import AnswercallResource
from api.dialcallback_api import DialCallbackResource
from api.hangupcall_api import HangupcallResource
from api.store_cdr_api import CdrResource
#from api.resources import *
from survey.api.resources import SurveyAppResource, SurveyQuestionResource, \
                                    SurveyResponseResource
import os
from django.contrib import admin
admin.autodiscover()
from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

# tastypie api
tastypie_api = Api(api_name='v1')
tastypie_api.register(UserResource())
tastypie_api.register(VoiceAppResource())
tastypie_api.register(GatewayResource())
tastypie_api.register(ContentTypeResource())
tastypie_api.register(PhonebookResource())
tastypie_api.register(CampaignResource())
tastypie_api.register(BulkContactResource())
tastypie_api.register(CampaignDeleteCascadeResource())
tastypie_api.register(CampaignSubscriberResource())
tastypie_api.register(CampaignSubscriberPerCampaignResource())
tastypie_api.register(CallrequestResource())
tastypie_api.register(AnswercallResource())
tastypie_api.register(DialCallbackResource())
tastypie_api.register(HangupcallResource())
tastypie_api.register(CdrResource())
"""
tastypie_api.register(SurveyAppResource())
tastypie_api.register(SurveyQuestionResource())
tastypie_api.register(SurveyResponseResource())
"""
js_info_dict = {
    'domain': 'djangojs',
    'packages': ('dialer_campaign',
                 'user_profile',
                 'voice_app',
                 'survey',
                 'audiofield'),
}

urlpatterns = patterns('',
    (r'^logout/$', 'dialer_campaign.views.logout_view'),
    (r'^admin/', include(admin.site.urls)),
    (r'^api/', include(tastypie_api.urls)),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^admin_tools/', include('admin_tools.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': settings.STATIC_ROOT}),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', \
                            {'url': 'static/newfies/images/favicon.png'}),
    #(r'^sentry/', include('sentry.web.urls')),
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)

urlpatterns += urlpatterns_dialer_campaign
urlpatterns += urlpatterns_dialer_cdr
urlpatterns += urlpatterns_user_profile
urlpatterns += urlpatterns_voice_app
urlpatterns += urlpatterns_survey

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
