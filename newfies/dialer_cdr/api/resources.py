import logging

from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.utils import dict_strip_unicode_keys, trailing_slash
from tastypie.http import HttpCreated
from tastypie.exceptions import NotFound
from tastypie import fields

from dialer_cdr.models import Callrequest, VoIPCall
from voip_app.models import VoipApp
from dialer_campaign.api.resources import VoipAppResource, UserResource

from datetime import datetime
from random import choice, seed

import time
import uuid


log = logging.getLogger(__name__)

def get_attribute(attrs, attr_name):
    """this is a helper to retrieve an attribute if it exists"""
    if attr_name in attrs:
        attr_value = attrs[attr_name]
    else:
        attr_value = None
    return attr_value


def get_value_if_none(x, value):
    """return value if x is None"""
    if x is None:
        return value
    return x


def pass_gen(char_length=2, digit_length=6):
    """function to generate password with a letter suffix"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digit = "1234567890"
    pass_str_char = ''.join([choice(chars) for i in range(char_length)])
    pass_str_digit = ''.join([choice(digit) for i in range(digit_length)])
    return pass_str_char + pass_str_digit


class CallrequestValidation(Validation):
    """
    Callrequest Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}

        voipapp_id = bundle.data.get('voipapp')
        if voipapp_id:
            try:
                voip_app_id = VoipApp.objects.get(id=voipapp_id).id
                bundle.data['voipapp'] = '/api/v1/voipapp/%s/' % voip_app_id
            except:
                errors['chk_voipapp'] = ["The VoipApp doesn't exist!"]
                
        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        if request.method=='POST':
            rq_count = Callrequest.objects.filter(request_uuid=bundle.data.get('request_uuid')).count()
            if (rq_count!=0):
                errors['chk_request_uuid'] = ["The Request uuid duplicated!"]

        return errors


class CallrequestResource(ModelResource):
    """
    **Attributes**:

        * ``callrequest_id``- Callrequest Id
        * ``request_uuid`` -
        * ``call_time`` -
        * ``call_type`` -
        * ``timeout`` -
        * ``timelimit`` -
        * ``status`` -
        * ``campaign_subscriber`` -
        * ``campaign`` -
        * ``voipapp`` -
        * ``callerid`` -
        * ``phone_number`` -
        * ``extra_dial_string`` -
        * ``extra_data`` -
        * ``num_attempt`` -
        * ``last_attempt_time`` -
        * ``result`` -
        * ``hangup_cause`` -
        * ``last_attempt_time`` -

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"request_uuid": "2342jtdsf-00123", "call_time": "2011-10-20 12:21:22", "phone_number": "8792749823", "voipapp": "1","timeout": "30000", "callerid": "650784355", "call_type": "1"}' http://localhost:8000/api/v1/callrequest/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/app/campaign/1/
            Content-Language: en-us


    **Read**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/callrequest/?format=json

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/callrequest/%callreq_id%/?format=json

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":1
               },
               "objects":[
                  {
                     "call_time":"2011-10-20T12:21:22",
                     "call_type":1,
                     "callerid":"650784355",
                     "created_date":"2011-10-14T07:33:41",
                     "extra_data":"",
                     "extra_dial_string":"",
                     "hangup_cause":"",
                     "id":"1",
                     "last_attempt_time":null,
                     "num_attempt":0,
                     "phone_number":"8792749823",
                     "request_uuid":"2342jtdsf-00123",
                     "resource_uri":"/api/v1/callrequest/1/",
                     "result":"",
                     "status":1,
                     "timelimit":3600,
                     "timeout":30000,
                     "updated_date":"2011-10-14T07:33:41",
                     "user":{
                        "first_name":"",
                        "id":"1",
                        "last_login":"2011-10-11T01:03:42",
                        "last_name":"",
                        "resource_uri":"/api/v1/user/1/",
                        "username":"areski"
                     },
                     "voipapp":{
                        "created_date":"2011-04-08T08:00:09",
                        "data":"",
                        "description":"",
                        "id":"1",
                        "name":"Default_VoIP_App",
                        "resource_uri":"/api/v1/voipapp/1/",
                        "type":1,
                        "updated_date":"2011-10-14T07:33:41"
                     }
                  }
               ]
            }

    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"status": "5"}' http://localhost:8000/api/v1/callrequest/%callrequest_id%/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us
    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    voipapp = fields.ForeignKey(VoipAppResource, 'voipapp', full=True)
    class Meta:
        queryset = Callrequest.objects.all()
        resource_name = 'callrequest'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = CallrequestValidation()
        list_allowed_methods = ['get', 'post', 'put']
        detail_allowed_methods = ['get', 'post', 'put']
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour


class HangupcallValidation(Validation):
    """
    Hangupcall Validation Class
    """
    def is_valid(self, bundle, request=None):
        errors = {}
        
        opt_request_uuid = bundle.data.get('RequestUUID')
        if not opt_request_uuid:
            errors['RequestUUID'] = ["Wrong parameters - missing RequestUUID!"]

        opt_hangup_cause = bundle.data.get('HangupCause')
        if not opt_hangup_cause:
            errors['HangupCause'] = ["Wrong parameters - missing HangupCause!"]

        try:
            callrequest = Callrequest.objects.get(request_uuid=opt_request_uuid)
        except:
            errors['CallRequest'] = ["CallRequest not found!"]

        return errors


class HangupcallResource(ModelResource):
    """
    **Attributes**:

       * ``call-uuid`` - Call UUID

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"RequestUUID": "48092924-856d-11e0-a586-0147ddac9d3e", "HangupCause": "SUBSCRIBER_ABSENT"}' http://localhost:8000/api/v1/hangupcall/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/app/hangupcall/None/
            Content-Language: en-us
    """
    class Meta:
        queryset = Callrequest.objects.all()
        resource_name = 'hangupcall'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = HangupcallValidation()
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """        
        opt_request_uuid = bundle.data.get('RequestUUID')
        opt_hangup_cause = bundle.data.get('HangupCause')

        callrequest = Callrequest.objects.get(request_uuid=opt_request_uuid)
        # 2 / FAILURE ; 3 / RETRY ; 4 / SUCCESS
        if opt_hangup_cause=='NORMAL_CLEARING':
            callrequest.status = 4 # Success
        else:
            callrequest.status = 2 # Failure
        callrequest.hangup_cause = opt_hangup_cause
        callrequest.save()

        #TODO : Create CDR

        return bundle

