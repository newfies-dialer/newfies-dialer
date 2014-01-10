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
from dnc.models import DNC, DNCContact


class DNCContactSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"phone_number": "12345", "dnc": "/rest-api/dnc-list/1/"}' http://localhost:8000/rest-api/dnc-contact/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Location: http://localhost:8000/rest-api/dnc_contact/1/
            Allow: GET, POST, HEAD, OPTIONS

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/dnc-contact/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/dnc-contact/1/",
                        "dnc": "http://127.0.0.1:8000/rest-api/dnc-list/1/",
                        "phone_number": "12345"
                    }
                ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"phone_number": "54353432"}' http://localhost:8000/rest-api/dnc-contact/%dnc-contact-id%/

        Response::

            HTTP/1.0 202 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """

    class Meta:
        model = DNCContact
        fields = ('url', 'dnc', 'phone_number')

    def get_fields(self, *args, **kwargs):
        """filter survey field"""
        fields = super(DNCContactSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']

        if request.method != 'GET' and self.init_data is not None:
            dnc = self.init_data.get('dnc')
            if dnc and dnc.find('http://') == -1:
                try:
                    DNC.objects.get(pk=int(dnc))
                    self.init_data['dnc'] = '/rest-api/dnc-list/%s/' % dnc
                except:
                    self.init_data['dnc'] = ''
                    pass

        if request.method != 'GET':
            fields['dnc'].queryset = DNC.objects.filter(user=request.user)

        return fields
