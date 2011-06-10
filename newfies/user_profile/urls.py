from django.conf.urls.defaults import *
from django.conf import settings
from user_profile.views import *


urlpatterns = patterns('',

# User detail change for Customer UI
(r'^user_detail_change/$', 'user_profile.views.customer_detail_change'),

(r'^user_detail_change/', include('notification.urls')),
(r'^view_notification/(?P<id>[^/]+)', 'user_profile.views.view_notification'),

# Notification Status (seen/unseen) for customer UI
(r'^update_notice_status_cust/(\d*)/$',
                'user_profile.views.update_notice_status_cust'),
)
