# -*- coding: utf-8 -*-

#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie import fields
from dnc.models import DNCContact
from api.dnc_api import DNCResource


class DNCContactResource(ModelResource):
    """DNCContact Model"""
    dnc = fields.ForeignKey(DNCResource, 'dnc', full=True)
    class Meta:
        queryset = DNCContact.objects.all()
        resource_name = 'dnc_contact'
        authorization = Authorization()
        authentication = BasicAuthentication()
