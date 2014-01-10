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

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dialer_contact.models import Phonebook, Contact
from dialer_contact.constants import CONTACT_STATUS
from dialer_campaign.models import Campaign, Subscriber
from dialer_campaign.constants import SUBSCRIBER_STATUS

import logging
logger = logging.getLogger('newfies.filelog')


class SubscriberViewSet(APIView):
    """SubscriberViewSet"""
    authentication = (BasicAuthentication, SessionAuthentication)

    def post(self, request, pk=None):
        """
        It will insert active contact to the subscriber for each
        active campaign using this phonebook which are not imported into
        subscriber before

        phonebook_id - To check valid phonebook_id & To add new contact in that phonebook
        additional_vars - Must be in JSON format

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"contact": "650784355", "last_name": "belaid", "first_name": "areski", "email": "areski@gmail.com", "phonebook_id" : "1"}' http://localhost:8000/rest-api/new-subscriber/

        """
        try:
            phonebook_id = request.DATA.get('phonebook_id')
            obj_phonebook = Phonebook.objects.get(
                id=phonebook_id, user=request.user)
        except:
            return Response({'error': 'phonebook id is not valid'})

        add_var = {}
        if request.POST.get('additional_vars'):
            try:
                import json
                add_var = json.loads(str(request.DATA.get('additional_vars')))
            except:
                return Response({'error': 'additional_vars is not valid format'})

        Contact.objects.create(
            contact=request.DATA.get('contact'),
            last_name=request.DATA.get('last_name'),
            first_name=request.DATA.get('first_name'),
            email=request.DATA.get('email'),
            description=request.DATA.get('description'),
            address=request.DATA.get('address'),
            city=request.DATA.get('city'),
            state=request.DATA.get('state'),
            country=request.DATA.get('country'),
            unit_number=request.DATA.get('unit_number'),
            additional_vars=add_var,
            status=CONTACT_STATUS.ACTIVE,  # default active
            phonebook=obj_phonebook)

        # Insert the contact to the subscriber also for
        # each campaign using this phonebook
        campaign_obj = Campaign.objects.filter(
            phonebook=obj_phonebook,
            user=request.user)

        for c_campaign in campaign_obj:
            imported_phonebook = []
            if c_campaign.imported_phonebook:
                # for example:- c_campaign.imported_phonebook = 1,2,3
                # So convert imported_phonebook string into int list
                imported_phonebook = map(int,
                    c_campaign.imported_phonebook.split(','))

            phonebook_list = c_campaign.phonebook \
                .values_list('id', flat=True) \
                .all()
            phonebook_list = map(int, phonebook_list)

            common_phonebook_list = []
            if phonebook_list:
                common_phonebook_list = list(set(imported_phonebook) & set(phonebook_list))
                if common_phonebook_list:
                    contact_list = Contact.objects \
                        .filter(phonebook__in=common_phonebook_list,
                                status=CONTACT_STATUS.ACTIVE)
                    for con_obj in contact_list:
                        try:
                            Subscriber.objects.create(
                                contact=con_obj,
                                duplicate_contact=con_obj.contact,
                                status=SUBSCRIBER_STATUS.PENDING,  # PENDING
                                campaign=c_campaign)
                        except:
                            error_msg = "Duplicate Subscriber"
                            logger.error(error_msg)
                            pass

        logger.debug('Subscriber POST API : result ok 200')
        return Response({'status': 'Contact created'})
