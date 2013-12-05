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

from rest_framework import serializers
from dialer_campaign.models import Subscriber
from dialer_contact.models import Phonebook
from dialer_campaign.function_def import dialer_setting_limit, check_dialer_setting
from django_countries.countries import COUNTRIES


class SubscriberSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"contact": "650784355", "last_name": "belaid", "first_name": "areski", "email": "areski@gmail.com", "phonebook_id" : "1"}' http://localhost:8000/rest-api/subscriber/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Wed, 18 May 2011 13:23:14 GMT
            Server: WSGIServer/0.1 Python/2.6.2
            Vary: Authorization
            Content-Length: 0
            Location: http://localhost:8000/api/v1/subscriber/1/
            Content-Type: text/plain

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/subscriber/

        Response::

            [
                {
                    "id": 1,
                    "contact": "/rest-api/contact/11/",
                    "campaign": "/rest-api/campaigns/3/",
                    "last_attempt": null,
                    "count_attempt": 0,
                    "completion_count_attempt": 0,
                    "duplicate_contact": "34235464",
                    "status": 1
                },
                {
                    "id": 2,
                    "contact": "/rest-api/contact/12/",
                    "campaign": "/rest-api/campaigns/3/",
                    "last_attempt": null,
                    "count_attempt": 0,
                    "completion_count_attempt": 0,
                    "duplicate_contact": "34235464",
                    "status": 1
                }
            ]

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"status": "2", "duplicate_contact": "650784355"}' http://localhost:8000/rest-api/subscriber/%subscriber_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    last_name = serializers.CharField(required=False, max_length=100)
    first_name = serializers.CharField(required=False, max_length=100)
    email = serializers.EmailField(required=False, max_length=100)
    address = serializers.CharField(required=False, max_length=100)
    city = serializers.CharField(required=False, max_length=100)
    state = serializers.CharField(required=False, max_length=100)
    unit_number = serializers.CharField(required=False, max_length=100)
    description = serializers.CharField(required=False, max_length=100)
    #additional_vars = serializers.CharField(required=False, max_length=100)
    country = serializers.ChoiceField(required=False, choices=COUNTRIES)
    #status = serializers.ChoiceField(required=False, choices=list(CONTACT_STATUS), default=CONTACT_STATUS.ACTIVE)
    phonebook_id = serializers.IntegerField(required=True)

    class Meta:
        model = Subscriber
        fields = ('id', 'contact', 'campaign', 'last_attempt',
                  'count_attempt', 'completion_count_attempt',
                  'duplicate_contact', 'last_name', 'first_name',
                  'email', 'phonebook_id', 'status',
                  )

    def get_fields(self):
        """filter field"""
        fields = super(SubscriberSerializer, self).get_fields()

        if self.object is not None:
            field_list = [
                'last_name', 'first_name', 'email', 'phonebook_id',
            ]
            for i in field_list:
                del fields[i]

        if self.context != {}:
            request = self.context['request']
            if request.method == 'POST':
                #del fields['contact']
                field_list = [
                    'campaign', 'last_attempt', 'count_attempt',
                    'completion_count_attempt', 'duplicate_contact',
                    'status'
                ]
                for i in field_list:
                    del fields[i]

                fields['contact'] = serializers.CharField(required=True, max_length=100)
                fields['address'] = serializers.CharField(required=True, max_length=100)
                fields['city'] = serializers.CharField(required=True, max_length=100)
                fields['state'] = serializers.CharField(required=True, max_length=100)
                fields['country'] = serializers.ChoiceField(required=False, choices=COUNTRIES)
                fields['description'] = serializers.CharField(required=True, max_length=100)
                fields['unit_number'] = serializers.CharField(required=True, max_length=100)
                #fields['additional_vars'] = serializers.CharField(required=True, max_length=100)

            if request.method == 'PUT' or request.method == 'PATCH':
                #fields['contact'].queryset = Contact.objects.filter(pk=self.object.contact_id)
                #fields['campaign'].queryset = Campaign.objects.filter(pk=self.object.campaign_id)
                field_list = [
                    'contact', 'campaign', 'last_attempt',
                    'completion_count_attempt',
                ]
                for i in field_list:
                    del fields[i]

                #del fields['duplicate_contact']

        return fields

    def validate(self, attrs):
        """
        Validate campaign request
        """
        request = self.context['request']

        if request.method == 'POST':
            if check_dialer_setting(request, check_for="contact"):
                raise serializers.ValidationError(
                    "You have too many contacts per campaign. You are allowed a maximum of %s" % dialer_setting_limit(request, limit_for="contact"))

            phonebook_id = request.POST.get('phonebook_id')
            if phonebook_id:
                try:
                    Phonebook.objects.get(id=phonebook_id, user=request.user)
                except Phonebook.DoesNotExist:
                    raise serializers.ValidationError("Phonebook is not selected!")
            else:
                raise serializers.ValidationError("Phonebook is not selected!")

        if request.method == 'PUT' or request.method == 'PATCH':
            try:
                subscriber = Subscriber.objects\
                    .get(duplicate_contact=request.POST.get('duplicate_contact'),
                         campaign=self.object.campaign,
                         campaign__user=request.user)
                subscriber.status = request.POST.get('status')
                subscriber.save()
            except:
                raise serializers.ValidationError("A model matching arguments could not be found.")

        return attrs
