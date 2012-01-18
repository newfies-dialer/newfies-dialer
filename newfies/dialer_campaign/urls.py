from django.conf.urls.defaults import *
from django.conf import settings
from dialer_campaign.views import *


urlpatterns = patterns('',
    (r'^$', 'dialer_campaign.views.index'),
    (r'^login/$', 'dialer_campaign.views.login_view'),
    (r'^logout/$', 'dialer_campaign.views.logout_view'),
    (r'^index/$', 'dialer_campaign.views.index'),
    (r'^pleaselog/$', 'dialer_campaign.views.pleaselog'),
    (r'^dashboard/$', 'dialer_campaign.views.customer_dashboard'),

    # Password reset for Customer UI
    (r'^password_reset/$', 'dialer_campaign.views.cust_password_reset'),
    (r'^password_reset/done/$',
                    'dialer_campaign.views.cust_password_reset_done'),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                    'dialer_campaign.views.cust_password_reset_confirm'),
    (r'^reset/done/$', 'dialer_campaign.views.cust_password_reset_complete'),

    # Phonebook urls
    (r'^phonebook/$', 'dialer_campaign.views.phonebook_list'),
    (r'^phonebook_grid/$', 'dialer_campaign.views.phonebook_grid'),
    (r'^phonebook/add/$', 'dialer_campaign.views.phonebook_add'),
    (r'^phonebook/contact_count/$', 'dialer_campaign.views.get_contact_count'),
    (r'^phonebook/del/(.+)/$', 'dialer_campaign.views.phonebook_del'),
    (r'^phonebook/(.+)/$', 'dialer_campaign.views.phonebook_change'),

    # Contacts urls
    (r'^contact/$', 'dialer_campaign.views.contact_list'),
    (r'^contact_grid/$', 'dialer_campaign.views.contact_grid'),
    (r'^contact/add/$', 'dialer_campaign.views.contact_add'),
    (r'^contact/import/$', 'dialer_campaign.views.contact_import'),
    (r'^contact/del/(.+)/$', 'dialer_campaign.views.contact_del'),
    (r'^contact/(.+)/$', 'dialer_campaign.views.contact_change'),


    # Campaign urls
    (r'^campaign/$', 'dialer_campaign.views.campaign_list'),
    (r'^campaign_grid/$', 'dialer_campaign.views.campaign_grid'),
    (r'^campaign/add/$', 'dialer_campaign.views.campaign_add'),
    (r'^campaign/del/(.+)/$', 'dialer_campaign.views.campaign_del'),
    # Campaign Actions (start|stop|pause|abort) for customer UI
    (r'^campaign/update_campaign_status_cust/(\d*)/(\d*)/$',
                    'dialer_campaign.views.update_campaign_status_cust'),
    (r'^campaign/(.+)/$', 'dialer_campaign.views.campaign_change'),

    # Campaign Actions (start|stop|pause|abort) for Admin UI
    (r'^update_campaign_status_admin/(\d*)/(\d*)/$',
                    'dialer_campaign.views.update_campaign_status_admin'),
    # Send notification to admin regarding dialer setting
    (r'^notify/admin/$', 'dialer_campaign.views.notify_admin'),
)
