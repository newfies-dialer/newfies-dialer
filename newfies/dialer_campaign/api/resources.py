import logging

from django.contrib.auth.models import User
from django.conf.urls.defaults import url

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.validation import Validation
from tastypie.throttle import BaseThrottle
from tastypie.utils import dict_strip_unicode_keys, trailing_slash
from tastypie.http import HttpCreated
from dialer_campaign.models import Campaign
from tastypie import fields
from dialer_campaign.function_def import user_attached_with_dialer_settings, check_dialer_setting
from dialer_gateway.models import Gateway
from voip_app.models import VoipApp
import time


log = logging.getLogger(__name__)


def get_value_if_none(x, value):
    """return value if x is None"""
    if x is None:
        return value
    return x

class VoipAppResource(ModelResource):
    class Meta:
        queryset = VoipApp.objects.all()
        resource_name = 'voipapp'


class GatewayResource(ModelResource):
    class Meta:
        queryset = Gateway.objects.all()
        resource_name = 'gateway'


class UserResource(ModelResource):
    class Meta:
        allowed_methods = ['get'] # Don't display or update User
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'last_login', 'id']
        #excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        filtering = {
            'username': 'exact',
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

        
class CampaignValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        if user_attached_with_dialer_settings(request):
            errors['user_dialer_setting'] = ['Your settings are not \
                        configured properly, Please contact the administrator.']

        if check_dialer_setting(request, check_for="campaign"):
            errors['chk_campaign'] = ["You have too many campaigns. Max allowed %s" \
            % dialer_setting_limit(request, limit_for="campaign")]

        frequency = bundle.data['frequency']
        if check_dialer_setting(request, check_for="frequency",
                                    field_value=int(frequency)):
            errors['chk_frequency'] = ["Maximum Frequency limit of %s exceeded." \
            % dialer_setting_limit(request, limit_for="frequency")]

        callmaxduration = bundle.data['callmaxduration']
        if check_dialer_setting(request,
                                check_for="duration",
                                field_value=int(callmaxduration)):
            errors['chk_duration'] = ["Maximum Duration limit of %s exceeded." \
            % dialer_setting_limit(request, limit_for="duration")]

        maxretry = bundle.data['maxretry']
        if check_dialer_setting(request,
                                check_for="retry",
                                field_value=int(maxretry)):
            errors['chk_duration'] = ["Maximum Retries limit of %s exceeded." \
            % dialer_setting_limit(request, limit_for="retry")]

        calltimeout = bundle.data['calltimeout']
        if check_dialer_setting(request,
                                check_for="timeout",
                                field_value=int(calltimeout)):
            errors['chk_timeout'] = ["Maximum Timeout limit of %s exceeded." \
            % dialer_setting_limit(request, limit_for="timeout")]

        try:
            aleg_gateway_id = Gateway.objects.get(id=bundle.data['aleg_gateway']).id
            bundle.data['aleg_gateway'] = '/api/v1/gateway/%s/' % aleg_gateway_id
        except:
            errors['chk_gateway'] = ["The Gateway ID doesn't exist!"]

        try:
            voip_app_id = VoipApp.objects.get(id=bundle.data['voipapp']).id
            bundle.data['voipapp'] = '/api/v1/voipapp/%s/' % voip_app_id
        except:
            errors['chk_voipapp'] = ["The VoipApp doesn't exist!"]

        try:
            user_id = User.objects.get(username=request.user).id
            bundle.data['user'] = '/api/v1/user/%s/' % user_id
        except:
            errors['chk_user'] = ["The User doesn't exist!"]

        return errors

    
class CampaignResource(ModelResource):
    """
    **Attributes**:

            * ``campaign_code`` - Autogenerate campaign code
            * ``name`` - Name of the Campaign
            * ``description`` - Short description of the Campaign
            * ``callerid`` - Caller ID
            * ``startingdate`` - Start date. Epoch Time, ie 1301414368
            * ``expirationdate`` - Expiry date. Epoch Time, ie 1301414368
            * ``daily_start_time`` - Daily start time, default '00:00:00'
            * ``daily_stop_time`` - Daily stop time, default '23:59:59'
            * ``monday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``tuesday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``wednesday`` - Set to 1 if you want to run this day of the week\
            , default '1'
            * ``thursday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``friday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``saturday`` - Set to 1 if you want to run this day of the week,\
            default '1'
            * ``sunday`` - Set to 1 if you want to run this day of the week,\
            default '1'

        **Campaign Settings**:

            * ``frequency`` - Defines the frequency, speed of the campaign.\
                              This is the number of calls per minute.
            * ``callmaxduration`` - Maximum call duration.
            * ``maxretry`` - Defines the max retries allowed per user.
            * ``intervalretry`` - Defines the time to wait between retries\
                                  in seconds
            * ``calltimeout`` - Defines the number of seconds to timeout on calls

        **Gateways**:

            * ``aleg_gateway`` - Defines the Gateway to use to call the\
                                 subscriber
            * ``voipapp`` - Defines the  application to use when the \
                            call is established on the A-Leg
            * ``extra_data`` - Defines the additional data to pass to the\
                                 application

    **Create**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type:application/json" -X POST --data '{"name": "mycampaign", "description": "", "callerid": "1239876", "frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "45", "aleg_gateway": "1", "voipapp": "1", "extra_data": "2000"}' http://localhost:8000/api/v1/campaign/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/campaign/?format=json

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
                     "callerid":"123987",
                     "callmaxduration":1800,
                     "calltimeout":45,
                     "campaign_code":"XIUER",
                     "created_date":"2011-06-15T00:49:16",
                     "daily_start_time":"00:00:00",
                     "daily_stop_time":"23:59:59",
                     "description":"",
                     "expirationdate":"2011-06-22T00:01:15",
                     "extra_data":"",
                     "frequency":10,
                     "friday":true,
                     "id":"1",
                     "intervalretry":3,
                     "maxretry":3,
                     "monday":true,
                     "name":"Default_Campaign",
                     "resource_uri":"/api/app/campaign/1/",
                     "saturday":true,
                     "startingdate":"2011-06-15T00:01:15",
                     "status":1,
                     "sunday":true,
                     "thursday":true,
                     "tuesday":true,
                     "updated_date":"2011-06-15T00:49:16",
                     "wednesday":true
                  }
               ]
            }
    """
    user = fields.ForeignKey(UserResource, 'user', full=True)
    aleg_gateway = fields.ForeignKey(GatewayResource, 'aleg_gateway', full=True)
    voipapp = fields.ForeignKey(VoipAppResource, 'voipapp', full=True)
    class Meta:
        queryset = Campaign.objects.all()
        resource_name = 'campaign'
        authorization = Authorization()
        authentication = BasicAuthentication()
        validation = CampaignValidation()
        filtering = {
            'name': ALL,
            'status': ALL,
        }
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def post_list(self, request, **kwargs):
        """
        Creates a new resource/object with the provided data.

        Calls ``obj_create`` with the provided data and returns a response
        with the new resource's location.

        If a new resource is created, return ``HttpCreated`` (201 Created).
        """
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

        # Force this in an ugly way, at least should do "reverse"
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized))

        self.is_valid(bundle, request)
        updated_bundle = self.obj_create(bundle, request=request)
        return HttpCreated(location=self.get_resource_uri(updated_bundle))

    """
    def hydrate(self, bundle):
        startingdate = bundle.data.get('startingdate')
        expirationdate = bundle.data.get('expirationdate')

        bundle.data['startingdate'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.gmtime(float(startingdate)))

        bundle.data['expirationdate'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.gmtime(float(expirationdate)))

        #setattr(bundle.obj, 'aleg_gateway_id', bundle.data['aleg_gateway'])
        #setattr(bundle.obj, 'voipapp_id', bundle.data['voipapp'])

        return bundle

    """




class MyCampaignResource(ModelResource):

    user = fields.ForeignKey(UserResource, 'user')    
    rating = fields.FloatField(readonly=True)

    class Meta:
        queryset = Campaign.objects.all()
        resource_name = 'mycampaign'
        authorization = Authorization()
        authentication = BasicAuthentication()
        throttle = BaseThrottle(throttle_at=1000, timeframe=3600) #default 1000 calls / hour

    def dehydrate_rating(self, bundle):
        total_score = 5.0
        
        return total_score

    def dehydrate(self, bundle):
        # Include the request IP in the bundle.
        bundle.data['request_ip'] = bundle.request.META.get('REMOTE_ADDR')
        return bundle
        
        
    
class MyResource(ModelResource):
    # As is, this is just an empty field. Without the ``dehydrate_rating``
    # method, no data would be populated for it.
    rating = fields.FloatField(readonly=True)

    class Meta:
        queryset = Campaign.objects.all()
        resource_name = 'rating'
        authorization = Authorization()
        authentication = BasicAuthentication()

    def dehydrate_rating(self, bundle):
        total_score = 5.0
        
        return total_score

    def dehydrate(self, bundle):
        # Include the request IP in the bundle.
        bundle.data['request_ip'] = bundle.request.META.get('REMOTE_ADDR')
        return bundle
