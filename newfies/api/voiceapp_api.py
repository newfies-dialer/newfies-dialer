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

from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from tastypie import fields
from api.user_api import UserResource
from voice_app.models import VoiceApp_template


class VoiceAppValidation(Validation):
    """VoiceApp Validation Class"""
    def is_valid(self, bundle, request=None):
        errors = {}

        if not bundle.data:
            errors['Data'] = ['Data set is empty']

        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        return errors


class VoiceAppResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    class Meta:
        queryset = VoiceApp_template.objects.all()
        resource_name = 'voiceapp'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = VoiceAppValidation()
