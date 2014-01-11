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
from rest_framework import serializers
from agent.models import Agent, AgentProfile
from django import forms
from dialer_campaign.models import Subscriber

HIDDEN_PASSWORD_STRING = '<hidden>'


#From https://groups.google.com/forum/#!msg/django-rest-framework/abMsDCYbBRg/d2orqUUdTqsJ
class PasswordField(serializers.CharField):
    """Special field to update a password field."""
    widget = forms.widgets.PasswordInput

    def from_native(self, value):
        """Hash if new value sent, else retrieve current password"""
        from django.contrib.auth.hashers import make_password
        if value == HIDDEN_PASSWORD_STRING or value == '':
            return self.parent.object.password
        else:
            return make_password(value)

    def to_native(self, value):
        """Hide hashed-password in API display"""
        return HIDDEN_PASSWORD_STRING


# Serializers
class AgentProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgentProfile
        partial = True
        fields = ('status', 'user')

    def get_fields(self, *args, **kwargs):
        """filter content_type field"""
        fields = super(AgentProfileSerializer, self).get_fields(*args, **kwargs)
        fields['user'].queryset = Agent.objects.filter(is_staff=False,
            is_superuser=False)
        return fields

# # Serializers
# class AgentProfileSerializer(serializers.HyperlinkedModelSerializer):
#     #user = serializers.Field(source='user.username')
#     user = serializers.HyperlinkedRelatedField(view_name='agent-detail')
#     manager = serializers.RelatedField()

#     class Meta:
#         model = AgentProfile
#         #fields = ('is_agent', 'call_timeout', 'type', 'contact', 'status', 'user')


class AgentSerializer(serializers.HyperlinkedModelSerializer):
    #api_key = serializers.Field(source='api_key')
    #profile = AgentProfileSerializer()

    class Meta:
        model = Agent
        fields = ('url', 'username', 'last_name', 'first_name', 'email', 'groups')  # 'profile'


class AgentPasswordSerializer(serializers.HyperlinkedModelSerializer):
    password = PasswordField()
    username = serializers.CharField(read_only=True)

    class Meta:
        model = Agent
        fields = ('url', 'password', 'username')


class AgentSubscriberSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/subscriber/

        Response::

            [
                {
                    "id": 1,
                    "status": 1,
                    "disposition": 1,
                    "collected_data": "",
                },
                {
                    "id": 2,
                    "status": 1,
                    "disposition": 1,
                    "collected_data": "",
                }
            ]
    """

    class Meta:
        model = Subscriber
        fields = ('id', 'status', 'disposition',
                  'collected_data', 'agent')

    def get_fields(self, *args, **kwargs):
        """filter content_type field"""
        fields = super(AgentSubscriberSerializer, self).get_fields(*args, **kwargs)
        fields['agent'].queryset = Agent.objects.filter(is_staff=False,
                                                        is_superuser=False)
        return fields
