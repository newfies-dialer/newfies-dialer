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
from django.contrib.auth import authenticate
from django.contrib.auth import login

from agent.models import Agent, AgentProfile
from agent.serializers import (AgentSerializer, AgentProfileSerializer,
    AgentPasswordSerializer, AgentSubscriberSerializer)
from agent.permission import IsOwnerOrReadOnly
from rest_framework import viewsets
# from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.authentication import (TokenAuthentication,
    SessionAuthentication)

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import parsers
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import serializers

from dialer_campaign.models import Subscriber
from dialer_cdr.models import Callrequest
from dialer_cdr.constants import CALLREQUEST_STATUS
from callcenter.models import CallAgent
import json

#review security
#make sure to display and allow change only on agent / not admin

#TODO Add TokenAuthentication / SessionAuthentication

class AgentViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Agent.objects.filter(is_staff=False, is_superuser=False)
    serializer_class = AgentSerializer
    authentication_classes = (SessionAuthentication, TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )


class AgentPasswordViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    authentication_classes = (SessionAuthentication, TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrReadOnly, )
    queryset = Agent.objects.all()
    serializer_class = AgentPasswordSerializer


class AgentProfileViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = AgentProfile.objects.filter(user__is_staff=False,
                                           user__is_superuser=False)
    serializer_class = AgentProfileSerializer
    authentication = (SessionAuthentication, TokenAuthentication, )
    permissions = (permissions.IsAuthenticated, )
    lookup_field = ('user_id')


class AgentSubscriberViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Subscriber.objects.all()
    serializer_class = AgentSubscriberSerializer
    permissions = (permissions.IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication, )


def get_last_callrequest():
    subscriber_all = Subscriber.objects.all()
    subscriber_obj = subscriber_all[0]

    try:
        last_callrequest = Callrequest.objects.get(
            subscriber_id=subscriber_obj.id)
    except:
        last_callrequest = Callrequest.objects.all()[0]
    return last_callrequest


class AgentQueueStatusViewSet(APIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication, )
    permissions = (permissions.IsAuthenticated, )

    def get(self, request, agent_id=0, format=None):
        error = {}
        data = {}
        try:
            Agent.objects.get(id=agent_id)
        except:
            error_msg = "Agent ID does not exists!"
            error['error'] = error_msg
            return Response(error)

        try:
            call_agent = CallAgent.objects \
                .filter(agent__user_id=agent_id) \
                .exclude(callrequest__status=CALLREQUEST_STATUS.SUCCESS) \
                .order_by('-id')[0]
        except:
            # empty response
            # No calls are waiting
            return Response(data)

        #print call_agent
        last_callrequest = call_agent.callrequest

        request_uuid = last_callrequest.request_uuid
        subscriber_obj = last_callrequest.subscriber
        contact_obj = subscriber_obj.contact
        camp_obj = subscriber_obj.campaign

        campaign_data = json.dumps({
            "id": camp_obj.id,
            "name": camp_obj.name,
            "callerid": camp_obj.callerid,
            "agent_script": camp_obj.agent_script,
            "lead_disposition": camp_obj.lead_disposition,
            "external_link": camp_obj.external_link
        })

        contact_obj = subscriber_obj.contact
        contact_data = json.dumps({
            "id": contact_obj.id,
            "contact": contact_obj.contact,
            "status": contact_obj.status,
            "last_name": contact_obj.last_name,
            "first_name": contact_obj.first_name,
            "email": contact_obj.email,
            "address": contact_obj.address,
            "city": contact_obj.city,
            "state": contact_obj.state,
            "country": str(contact_obj.country),
            "unit_number": contact_obj.unit_number,
            "additional_vars": contact_obj.additional_vars,
            "description": contact_obj.description,
        })

        data = {
            "subscriber_id": subscriber_obj.id,
            "request_uuid": request_uuid,
            "campaign": campaign_data,
            "contact": contact_data,
            "callstate": call_agent.callstate,
        }

        return Response(data)


### Login part
class AgentAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')

                # Check user is agent or not
                try:
                    AgentProfile.objects.get(user=user, is_agent=True)
                except:
                    raise serializers.ValidationError('User is not an agent.')

                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Unable to login with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password"')


#TODO: Review this and see if we can do an other approach without using that hack
class ObtainAuthTokenLogin(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser, )
    renderer_classes = (renderers.JSONRenderer, )
    serializer_class = AgentAuthTokenSerializer
    model = Token

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            if serializer.object['user'].is_active:
                login(request, serializer.object['user'])
                request.session['has_notified'] = False
            token, created = Token.objects.get_or_create(user=serializer.object['user'])
            data = {
                'token': token.key,
                'username': serializer.object['user'].username,
                'userid': serializer.object['user'].id,
            }
            return Response(data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

obtain_auth_token_login = ObtainAuthTokenLogin.as_view()
