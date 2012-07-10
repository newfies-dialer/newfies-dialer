# -*- coding: utf-8 -*-

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

from django.contrib.contenttypes.models import ContentType
from tastypie.resources import ModelResource


class ContentTypeResource(ModelResource):
    class Meta:
        queryset = ContentType.objects.all()
        resource_name = "contenttype"
        fields = ['model']
        detail_allowed_methods = ['get']
        list_allowed_methods = ['get']
