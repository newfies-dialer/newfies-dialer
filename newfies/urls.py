from django.conf.urls.defaults import *
from django.conf import settings
from django.conf.urls.i18n import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from dialer_campaign.urls import urlpatterns as urlpatterns_dialer_campaign
from dialer_cdr.urls import urlpatterns as urlpatterns_dialer_cdr
from user_profile.urls import urlpatterns as urlpatterns_user_profile
from voip_app.urls import urlpatterns as urlpatterns_voip_app


urlpatterns = patterns('',
    # redirect
    #('^$', 'django.views.generic.simple.redirect_to',
    #{'url': '/dialer_campaign/'}),

    # Example:

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    (r'^api/dialer_cdr/', include('dialer_cdr.api.urls'), ),

    (r'^api/dialer_campaign/', include('dialer_campaign.api.urls')),

    (r'^i18n/', include('django.conf.urls.i18n')),

    (r'^admin_tools/', include('admin_tools.urls')),

    #(r'^$', include('dialer_campaign.urls')),
    #(r'^dialer_cdr/', include('dialer_cdr.urls')),
    #(r'^user_profile/', include('user_profile.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
)

urlpatterns += urlpatterns_dialer_campaign
urlpatterns += urlpatterns_dialer_cdr
urlpatterns += urlpatterns_user_profile
urlpatterns += urlpatterns_voip_app
