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
from dialer_contact.models import Phonebook, Contact


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"contact": "12345678", "status": "1", "last_name": "Belaid", "first_name": "Areski", "phonebook": "/rest-api/phonebook/1/"}' http://localhost:8000/rest-api/contact/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 14 Jun 2013 09:52:27 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Allow: GET, POST, HEAD, OPTIONS

    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/contact/

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/rest-api/contact/%contact-id%/

        Response::

            {
                "count": 1,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "url": "http://127.0.0.1:8000/rest-api/contact/1/",
                        "phonebook": "http://127.0.0.1:8000/rest-api/phonebook/1/",
                        "contact": "55555555",
                        "status": 1,
                        "last_name": "Belaid",
                        "first_name": "Arezqui",
                        "email": "areski@gmail.com",
                        "address": "Address",
                        "city": "Barcelona",
                        "state": "state",
                        "country": "ES",
                        "unit_number": "123",
                        "additional_vars": "{\"facility\":\"hurron\",\"debt\":10,\"address\":\"Sant Lluis street 60\"}",
                        "description": "test subscriber",
                        "created_date": "2013-06-27T19:48:45.118",
                        "updated_date": "2013-06-27T19:48:45.118"
                    },
                ]
            }


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PATCH --data '{"contact": "12345678", "status": "1", "last_name": "Belaid", "first_name": "Areski", "phonebook": "/rest-api/phonebook/1/"}' http://localhost:8000/rest-api/contact/%contact-id%/

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
        model = Contact

    def get_fields(self, *args, **kwargs):
        """filter survey field"""
        fields = super(ContactSerializer, self).get_fields(*args, **kwargs)
        request = self.context['request']

        if request.method != 'GET' and self.init_data is not None:
            phonebook = self.init_data.get('phonebook')
            if phonebook and phonebook.find('http://') == -1:
                try:
                    Phonebook.objects.get(pk=int(phonebook))
                    self.init_data['phonebook'] = '/rest-api/phonebook/%s/' % phonebook
                except:
                    self.init_data['phonebook'] = ''
                    pass

        if request.method != 'GET':
            fields['phonebook'].queryset = Phonebook.objects.filter(user=request.user)

        return fields
