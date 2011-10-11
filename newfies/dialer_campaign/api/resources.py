from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from dialer_campaign.models import *


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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X POST --data '{"name": "mylittlecampaign", "description": "", "callerid": "1239876", "startingdate": "1301392136.0", "expirationdate": "1301332136.0","frequency": "20", "callmaxduration": "50", "maxretry": "3", "intervalretry": "3000", "calltimeout": "60", "aleg_gateway": "1", "voipapp": "1", "extra_data": "2000" }' http://localhost:8000/api/app/campaign/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/app/campaign/?format=json

        Response::

            {
               "meta":{
                  "limit":20,
                  "next":null,
                  "offset":0,
                  "previous":null,
                  "total_count":4
               },
               "objects":[
                  {
                     "active":true,
                     "country":"IN",
                     "id":"1",
                     "resource_uri":"/api/app/country/1/"
                  },
               ]
            }


    **Update**:

        CURL Usage::

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X PUT --data '{"country": "IN", "active": 1}' http://localhost:8000/api/app/campaign/1/

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

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/app/campaign/1/

            curl -u username:password --dump-header - -H "Content-Type: application/json" -X DELETE  http://localhost:8000/api/app/campaign/

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

            curl -u username:password -H 'Accept: application/json' http://localhost:8000/api/app/campaign/?country=IN

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