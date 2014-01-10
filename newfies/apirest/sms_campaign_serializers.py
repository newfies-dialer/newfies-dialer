# -*- coding: utf-8 -*-

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
from dialer_campaign.function_def import user_dialer_setting, dialer_setting_limit
from sms_module.models import SMSCampaign
from sms_module.function_def import check_sms_dialer_setting
from dialer_contact.models import Phonebook
from sms.models import Gateway as SMSGateway


class SMSCampaignSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "sms", "description": "", "callerid": "1239876", "startingdate": "2013-06-13 13:13:33", "expirationdate": "2013-06-14 13:13:33", "frequency": "20", "maxretry": "3", "sms_gateway": "/rest-api/sms-gateway/1/", "phonebook_id": "1"}' http://localhost:8000/rest-api/sms-campaigns/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Allow: GET, POST, HEAD, OPTIONS

            {"id": 1, "sms_campaign_code": "JDQBG", "name": "mysmscampaign1", "description": "", "callerid": "1239876", "phonebook": ["/rest-api/phonebook/1/", "/rest-api/phonebook/2/"], "startingdate": "2013-06-13T13:13:33", "expirationdate": "2013-06-14T13:13:33", "sms_gateway": "http://localhost:8000/rest-api/sms-gateway/1/", "user": "http://localhost:8000/rest-api/users/1/", "status": 2, "frequency": 20, "daily_start_time": "00:00:00", "daily_stop_time": "23:59:59", "monday": true, "tuesday": true, "wednesday": true, "thursday": true, "friday": true, "saturday": true, "sunday": true}


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/sms-campaigns/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/sms-campaigns/%sms-campaign-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "id": 2,
                        "sms_campaign_code": "BXTWX",
                        "name": "Sample SMS campaign",
                        "description": "",
                        "callerid": "",
                        "phonebook": [
                            "http://127.0.0.1:8000/rest-api/phonebook/1/"
                        ],
                        "startingdate": "2011-12-27T14:35:46",
                        "expirationdate": "2011-12-28T14:35:46",
                        "sms_gateway": "http://127.0.0.1:8000/rest-api/sms-gateway/1/",
                        "user": "http://127.0.0.1:8000/rest-api/users/1/",
                        "status": 2,
                        "frequency": 10,
                        "callmaxduration": 1800,
                        "maxretry": 0,
                        "daily_start_time": "00:00:00",
                        "daily_stop_time": "23:59:59",
                        "monday": true,
                        "tuesday": true,
                        "wednesday": true,
                        "thursday": true,
                        "friday": true,
                        "saturday": true,
                        "sunday": true,
                    }
                ]
            }


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"name": "mylittlesmscampaign243"}' http://localhost:8000/rest-api/sms-campaigns/%sms-campaign-id%/

        Response::

            HTTP/1.0 202 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    **Delete**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/rest-api/sms-campaigns/%sms-campaign_id%/

        Response::

            {
                "data": "sms campaign deleted"
            }
    """
    user = serializers.Field(source='user')
    sms_gateway = serializers.HyperlinkedRelatedField(
        read_only=False, view_name='sms-gateway-detail')

    class Meta:
        model = SMSCampaign

    def get_fields(self, *args, **kwargs):
        """filter content_type field"""
        fields = super(SMSCampaignSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']

        if request.method != 'GET' and self.init_data is not None:
            phonebook = self.init_data.get('phonebook')
            if phonebook and phonebook.find('http://') == -1:
                try:
                    phonebook_id_list = phonebook.split(",")
                    m2m_phonebook = []
                    for i in phonebook_id_list:
                        try:
                            Phonebook.objects.get(pk=int(i), user=request.user)
                            m2m_phonebook.append('/rest-api/phonebook/%s/' % i)
                        except:
                            pass

                    if m2m_phonebook:
                        self.init_data['phonebook'] = m2m_phonebook
                    else:
                        self.init_data['phonebook'] = ''
                except:
                    self.init_data['phonebook'] = ''

            fields['sms_gateway'].queryset = SMSGateway.objects.all()
            fields['phonebook'].queryset = Phonebook.objects.filter(user=request.user)

        return fields

    def validate(self, attrs):
        """
        Validate sms campaign form
        """
        request = self.context['request']

        if request.method == 'POST':
            name_count = SMSCampaign.objects.filter(name=attrs.get('name'),
                user=request.user).count()
            if name_count != 0:
                raise serializers.ValidationError("The SMS Campaign name duplicated!")

        if not user_dialer_setting(request.user):
            raise serializers.ValidationError("Your settings are not configured properly, Please contact the administrator.")

        if check_sms_dialer_setting(request, check_for="smscampaign"):
            raise serializers.ValidationError("Too many sms campaigns. Max allowed %s"
                    % dialer_setting_limit(request, limit_for="smscampaign"))

        frequency = attrs.get('frequency')
        if frequency:
            if check_sms_dialer_setting(request, check_for="smsfrequency", field_value=int(frequency)):
                raise serializers.ValidationError("Frequency limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="smsfrequency"))

        maxretry = attrs.get('maxretry')
        if maxretry:
            if check_sms_dialer_setting(request, check_for="smsretry", field_value=int(maxretry)):
                raise serializers.ValidationError("Retries limit of %s exceeded."
                    % dialer_setting_limit(request, limit_for="smsretry"))

        return attrs
