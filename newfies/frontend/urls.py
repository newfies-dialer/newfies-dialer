#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#
# from django.conf.urls import patterns
from django.conf.urls import url
from frontend import views

# django 1.8 - https://docs.djangoproject.com/en/1.8/ref/urls/#django.conf.urls.url
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view),
    url(r'^logout/$', views.logout_view),
    url(r'^index/$', views.index),
    url(r'^pleaselog/$', views.pleaselog),
    url(r'^dashboard/$', views.customer_dashboard),
]

#
# TODO: patterns is depreciated from 1.8, apply the above changes over the whole application
#
# urlpatterns = patterns('frontend.views',
#                        (r'^$', 'index', name='index'),
#                        (r'^login/$', 'login_view'),
#                        (r'^logout/$', 'logout_view'),
#                        (r'^index/$', 'index'),
#                        (r'^pleaselog/$', 'pleaselog'),
#                        (r'^dashboard/$', 'customer_dashboard'),
#                        )
