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

from rest_framework import viewsets
from apirest.phonebook_serializers import PhonebookSerializer
from rest_framework.permissions import IsAuthenticated, \
    DjangoObjectPermissions
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from dialer_contact.models import Phonebook


class CustomObjectPermissions(DjangoObjectPermissions):
    """
    Similar to `DjangoObjectPermissions`, but adding 'view' permissions.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class PhonebookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows phonebook to be viewed or edited.
    """
    model = Phonebook
    queryset = Phonebook.objects.all()
    serializer_class = PhonebookSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticated, CustomObjectPermissions)

    def get_queryset(self):
        """
        This view should return a list of all the phonebooks
        for the currently authenticated user.
        """
        if self.request.user.is_superuser:
            queryset = Phonebook.objects.all()
        else:
            queryset = Phonebook.objects.filter(user=self.request.user)
        return queryset

    def pre_save(self, obj):
        obj.user = self.request.user
