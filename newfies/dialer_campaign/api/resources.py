from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.validation import Validation
from dialer_campaign.models import Campaign
from dialer_campaign.function_def import user_attached_with_dialer_settings, check_dialer_setting
import time


def get_value_if_none(x, value):
    """return value if x is None"""
    if x is None:
        return value
    return x


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
            setattr(bundle.obj, 'aleg_gateway_id', aleg_gateway_id)
        except:
            errors['chk_gateway'] = ["The Gateway ID doesn't exist!"]

        try:
            voip_app_id = VoipApp.objects.get(id=bundle.data['voipapp']).id
            setattr(bundle.obj, 'voipapp_id', voip_app_id)
        except:
            errors['chk_voipapp'] = ["The VoipApp doesn't exist!"]

                    
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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X POST --data '{"name": "mylittlecampaign", "description": "", "callerid": "1239876", "startingdate": "1301392136.0", "expirationdate": "1301332136.0", "frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "60", "aleg_gateway": "1", "voipapp": "1", "extra_data": "2000" }' http://localhost:8000/api/v1/campaign/

        Response::

            HTTP/1.0 201 CREATED
            Date: Fri, 23 Sep 2011 06:08:34 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Type: text/html; charset=utf-8
            Location: http://localhost:8000/api/app/country/1/
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


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"name": "mylittlecampaign", "description": "", "callerid": "1239876", "startingdate": "1301392136.0", "expirationdate": "1301332136.0","frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "60", "aleg_gateway": "1", "voipapp": "1", "extra_data": "2000" }' http://localhost:8000/api/v1/campaign/1/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:46:12 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us


    **Delete**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/campaign/1/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/v1/campaign/

        Response::

            HTTP/1.0 204 NO CONTENT
            Date: Fri, 23 Sep 2011 06:48:03 GMT
            Server: WSGIServer/0.1 Python/2.7.1+
            Vary: Accept-Language, Cookie
            Content-Length: 0
            Content-Type: text/html; charset=utf-8
            Content-Language: en-us

    **Search**:

        CURL Usage::

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/v1/campaign/?country=IN

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
                     "active":true,
                     "country":"IN",
                     "id":"2",
                     "resource_uri":"/api/app/country/2/"
                  }
               ]
            }
    """
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

    def obj_create(self, bundle, request=None, **kwargs):

        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)
        setattr(bundle.obj, 'user_id', User.objects.get(username=request.user).id)
        bundle = self.full_hydrate(bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle
    
    """
    def obj_update(self, bundle, request=None, **kwargs):

        if not bundle.obj or not bundle.obj.pk:
            # Attempt to hydrate data from kwargs before doing a lookup for the object.
            # This step is needed so certain values (like datetime) will pass model validation.
            try:
                bundle.obj = self.get_object_list(request).model()
                bundle.data.update(kwargs)
                #bundle = self.full_hydrate(bundle)
                bundle = self.hydrate(bundle, request)
                lookup_kwargs = kwargs.copy()
                lookup_kwargs.update(dict(
                    (k, getattr(bundle.obj, k))
                    for k in kwargs.keys()
                    if getattr(bundle.obj, k) is not None))
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs

            try:
                bundle.obj = self.obj_get(request, **lookup_kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")
        #setattr(bundle.obj, 'user_id', User.objects.get(username=request.user).id)
        #bundle = self.full_hydrate(bundle)
        #bundle = self.hydrate(bundle, request)
        bundle.obj.save()

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle
    """
