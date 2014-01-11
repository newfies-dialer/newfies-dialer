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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dialer_contact.models import Phonebook, Contact
from dialer_campaign.function_def import dialer_setting_limit, check_dialer_setting


class BulkContactViewSet(APIView):
    """
    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"phonebook_id": "1", "phoneno_list" : "12345,54344"}' http://localhost:8000/rest-api/bulkcontact/

        Response::
            HTTP/1.0 200 OK
            Date: Mon, 01 Jul 2013 13:14:10 GMT
            Server: WSGIServer/0.1 Python/2.7.3
            Vary: Accept, Accept-Language, Cookie
            Content-Type: application/json; charset=utf-8
            Content-Language: en-us
            Allow: POST, OPTIONS

            {"result": "Bulk contacts are created"}
    """
    authentication = (BasicAuthentication, SessionAuthentication)

    def post(self, request):
        """
        create contacts in bulk
        """
        error = {}
        if request.method == 'POST':
            if not request.DATA:
                error['error'] = 'Data set is empty'

            if check_dialer_setting(request, check_for="contact"):
                error['error'] = "You have too many contacts per campaign. You are allowed a maximum of %s" % \
                    dialer_setting_limit(request, limit_for="contact")

            phonebook_id = request.DATA.get('phonebook_id')
            if phonebook_id and phonebook_id != '':
                try:
                    Phonebook.objects.get(id=phonebook_id, user=request.user)
                except Phonebook.DoesNotExist:
                    error['error'] = 'Phonebook is not valid!'
            else:
                error['error'] = 'Phonebook is not selected!'

        if error:
            return Response(error)

        phoneno_list = request.DATA.get('phoneno_list')
        phonebook_id = request.DATA.get('phonebook_id')
        phonenolist = list(phoneno_list.split(","))

        obj_phonebook = Phonebook.objects.get(id=phonebook_id, user=request.user)
        new_contact_count = 0
        for phoneno in phonenolist:
            # check phoneno in Contact
            dup_count = Contact.objects.filter(contact=phoneno, phonebook__user=request.user).count()

            # If dup_count is zero, create new contact
            if dup_count == 0:
                new_contact = Contact.objects.create(
                    phonebook=obj_phonebook,
                    contact=phoneno,
                )
                new_contact_count = new_contact_count + 1
                new_contact.save()
            else:
                error_msg = "The contact duplicated (%s)!\n" % phoneno
                return Response({'error': error_msg})

        return Response({'result': 'Bulk contacts are created'})
