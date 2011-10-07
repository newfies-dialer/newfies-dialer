from piston.handler import BaseHandler
from piston.emitters import *
from piston.utils import rc, require_mime, require_extended, throttle
from dialer_campaign.models import *
from dialer_campaign.function_def import *
from dialer_gateway.models import Gateway
from voip_app.models import VoipApp
from django.db import IntegrityError
from django.db.models import Q
from common_functions import *
import time

#TODO make sure we get int for ID settings


def get_attribute(attrs, attr_name):
    """This is a helper to retrieve an attribute if it exists"""
    if attr_name in attrs:
        attr_value = attrs[attr_name]
    else:
        attr_value = None
    return attr_value


def save_if_set(record, fproperty, value):
    """function to save a property if it has been set"""
    if value:
        record.__dict__[fproperty] = value


def get_value_if_none(x, value):
    """return value if x is None"""
    if x is None:
        return value
    return x


class campaignHandler(BaseHandler):
    """This API server provides Campaign management giving basic functions
    to create and update campaigns."""
    model = Campaign
    allowed_methods = ('POST', 'GET', 'PUT', 'DELETE')    
    fields = ('id', 'campaign_code', 'name', 'status', 'callerid',
              'startingdate', 'expirationdate', 'frequency',
              'callmaxduration', 'maxretry', 'intervalretry',
              'calltimeout', 'aleg_gateway', 'bleg_gateway', 'voipapp',
              'extra_data', ('phonebook', ('id', 'name', ), ), )

    @classmethod
    def content_length(cls, campaign):
        return len(campaign.content)

    @staticmethod
    def resource_uri(self):
        return ('api_campaign_handler', ['id'])

    def create(self, request):
        """API to create a new campaign

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

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_campaign/campaign/ -d "name=mylittlecampaign&description=&callerid=1239876&startingdate=1301392136.0&expirationdate=1301332136.0&frequency=20&callmaxduration=50&maxretry=3&intervalretry=3000&calltimeout=60&aleg_gateway=1&voipapp=1&extra_data=2000"

        **Example Response**::

            {
                "status": 2,
                "voipapp": {
                    "gateway_id": 1,
                    "updated_date": "2011-06-22 09:58:22",
                    "user_id": 1,
                    "description": "",                    
                    "created_date": "2011-04-08 08:00:09",
                    "type": 1,
                    "id": 1,
                    "name": "Default_VoIP_App"
                },
                "startingdate": "2011-03-29 09:48:56",
                "name": "Default_Campaign",
                "callerid": "123987",
                "callmaxduration": 50,
                "intervalretry": 3000,
                "id": 1,
                "phonebook": [
                    {
                        "name": "Default_Phonebook",
                        "id": 1
                    }
                ],
                "frequency": 20,
                "maxretry": 3,
                "expirationdate": "2011-03-28 17:08:56",
                "campaign_code": "XIUER",
                "aleg_gateway": {
                    "status": 1,
                    "updated_date": "2011-06-15 00:28:52",
                    "addparameter": "",
                    "addprefix": "",
                    "description": "",
                    "gateway_codecs": "PCMA,PCMU",
                    "failover_id": null,
                    "count_call": null,
                    "created_date": "2011-06-15 00:28:52",
                    "maximum_call": null,
                    "gateway_timeouts": "10,10",
                    "count_in_use": null,
                    "removeprefix": "",
                    "gateway_retries": "2,1",
                    "gateways": "user/,user",
                    "secondused": null,
                    "originate_dial_string": "",                    
                    "id": 1,
                    "name": "Default_Gateway"
                },
                "extra_data": "2000",
                "calltimeout": 60
            }

        **Error**:

            * You have too many campaigns. Max allowed 5
            * The Gateway ID doesn't exist!
            * The VoipApp doesn't exist!
            * The Campaign name is duplicated!
        """
        if user_attached_with_dialer_settings(request):
            resp = rc.BAD_REQUEST
            resp.write("Your settings aren`t configured properly, \
                 Please contact the administrator.")
            return resp

        if check_dialer_setting(request, check_for="campaign"):
            resp = rc.BAD_REQUEST
            resp.write("You have too many campaigns. Max allowed %s" \
            % dialer_setting_limit(request, limit_for="campaign"))
            return resp
        else:
            attrs = self.flatten_dict(request.POST)

            name = get_attribute(attrs, 'name')
            description = get_attribute(attrs, 'description')
            status = 1 # per default
            callerid = get_attribute(attrs, 'callerid')
            startingdate = get_attribute(attrs, 'startingdate')
            expirationdate = get_attribute(attrs, 'expirationdate')
            frequency = get_attribute(attrs, 'frequency')
            if check_dialer_setting(request, check_for="frequency",
                                    field_value=int(frequency)):
                resp = rc.BAD_REQUEST
                resp.write("Maximum Frequency limit of %s exceeded." \
                % dialer_setting_limit(request, limit_for="frequency"))
                return resp

            callmaxduration = get_attribute(attrs, 'callmaxduration')
            if check_dialer_setting(request,
                                    check_for="duration",
                                    field_value=int(callmaxduration)):
                resp = rc.BAD_REQUEST
                resp.write("Maximum Duration limit of %s exceeded." \
                % dialer_setting_limit(request, limit_for="duration"))
                return resp

            maxretry = get_attribute(attrs, 'maxretry')
            if check_dialer_setting(request,
                                    check_for="retry",
                                    field_value=int(maxretry)):
                resp = rc.BAD_REQUEST
                resp.write("Maximum Retries limit of %s exceeded." \
                % dialer_setting_limit(request, limit_for="retry"))
                return resp
            intervalretry = get_attribute(attrs, 'intervalretry')
            calltimeout = get_attribute(attrs, 'calltimeout')
            if check_dialer_setting(request,
                                    check_for="timeout",
                                    field_value=int(calltimeout)):
                resp = rc.BAD_REQUEST
                resp.write("Maximum Timeout limit of %s exceeded." \
                % dialer_setting_limit(request, limit_for="timeout"))
                return resp

            aleg_gateway = get_attribute(attrs, 'aleg_gateway')
            voipapp = get_attribute(attrs, 'voipapp')
            extra_data = get_attribute(attrs, 'extra_data')
            daily_start_time = get_attribute(attrs, 'daily_start_time')
            daily_stop_time = get_attribute(attrs, 'daily_stop_time')
            monday = get_attribute(attrs, 'monday')
            tuesday = get_attribute(attrs, 'tuesday')
            wednesday = get_attribute(attrs, 'wednesday')
            thursday = get_attribute(attrs, 'thursday')
            friday = get_attribute(attrs, 'friday')
            saturday = get_attribute(attrs, 'saturday')
            sunday = get_attribute(attrs, 'sunday')

            startingdate = get_value_if_none(startingdate, time.time())
            # expires in 7 days
            expirationdate = \
            get_value_if_none(expirationdate, time.time() + 86400 * 7)

            startingdate = \
            time.strftime('%Y-%m-%d %H:%M:%S',
                          time.gmtime(float(startingdate)))
            expirationdate = \
            time.strftime('%Y-%m-%d %H:%M:%S',
                          time.gmtime(float(expirationdate)))

            daily_start_time = get_value_if_none(daily_start_time, '00:00:00')
            daily_stop_time = get_value_if_none(daily_stop_time, '23:59:59')
            monday = get_value_if_none(monday, 1)
            tuesday = get_value_if_none(tuesday, 1)
            wednesday = get_value_if_none(wednesday, 1)
            thursday = get_value_if_none(thursday, 1)
            friday = get_value_if_none(friday, 1)
            saturday = get_value_if_none(saturday, 1)
            sunday = get_value_if_none(sunday, 1)

            #TODO: Check it owns by user
            try:
                obj_aleg_gateway = Gateway.objects.get(id=aleg_gateway)
            except Gateway.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write("The Gateway ID doesn't exist!")
                return resp
                
            
            try:
                obj_voip_app = VoipApp.objects.get(id=voipapp)
            except VoipApp.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write("The VoipApp doesn't exist!")
                return resp

            try:
                campaign_code=get_unique_code(length=5)
                new_campaign = Campaign.objects.create(user=request.user,
                                    campaign_code=campaign_code,
                                    name=name,
                                    description=description,
                                    status=status,
                                    callerid=callerid,
                                    startingdate=startingdate,
                                    expirationdate=expirationdate,
                                    frequency=frequency,
                                    callmaxduration=callmaxduration,
                                    maxretry=maxretry,
                                    intervalretry=intervalretry,
                                    calltimeout=calltimeout,
                                    aleg_gateway=obj_aleg_gateway,
                                    voipapp=obj_voip_app,
                                    extra_data=extra_data,
                                    daily_start_time=daily_start_time,
                                    daily_stop_time=daily_stop_time,
                                    monday=monday,
                                    tuesday=tuesday,
                                    wednesday=wednesday,
                                    thursday=thursday,
                                    friday=friday,
                                    saturday=saturday,
                                    sunday=sunday,)
            except IntegrityError:
                #raise
                resp = rc.DUPLICATE_ENTRY
                resp.write("The Campaign name duplicated!")
                return resp
            
            try:
                new_phonebook = Phonebook.objects.create(user=request.user,
                                name=name + '-' + campaign_code,
                                description='Auto created Phonebook from API')
            except IntegrityError:
                #raise
                resp = rc.DUPLICATE_ENTRY
                resp.write("The Autogenerated Phonebook name duplicated - Internal Error!")
                return resp

            new_campaign.phonebook.add(new_phonebook)
            new_campaign.save()

            return new_campaign

    @throttle(1000, 1 * 60) #  Throttle if more that 1000 times within 1 minute
    def read(self, request, campaign_id=None):
        """API to read all pending campaigns, or a specific campaign if
        a campaign_id is supplied

        **Attributes**:

            * ``campaign_id`` - Campaign ID

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/dialer_campaign/campaign/

            curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/dialer_campaign/campaign/%campaign_id%/

        **Example Response**::

            [
                {
                    "status": 2,
                    "voipapp": {
                        "gateway_id": 1,
                        "updated_date": "2011-06-22 09:58:22",
                        "user_id": 1,
                        "description": "",                        
                        "created_date": "2011-04-08 08:00:09",
                        "type": 1,
                        "id": 1,
                        "name": "Default_VoIP_App"
                    },
                    "startingdate": "2011-03-29 09:48:56",
                    "name": "Default_Campaign",
                    "callerid": "123987",
                    "callmaxduration": 50,
                    "intervalretry": 3000,
                    "id": 1,
                    "phonebook": [
                        {
                            "name": "Default_Phonebook",
                            "id": 1
                        }
                    ],
                    "frequency": 20,
                    "maxretry": 3,
                    "expirationdate": "2011-03-28 17:08:56",
                    "campaign_code": "XIUER",
                    "aleg_gateway": {
                        "status": 1,
                        "updated_date": "2011-06-15 00:28:52",
                        "addparameter": "",
                        "addprefix": "",
                        "description": "",
                        "gateway_codecs": "PCMA,PCMU",
                        "failover_id": null,
                        "count_call": null,
                        "created_date": "2011-06-15 00:28:52",
                        "maximum_call": null,
                        "gateway_timeouts": "10,10",
                        "count_in_use": null,
                        "removeprefix": "",
                        "gateway_retries": "2,1",
                        "gateways": "user/,user",
                        "secondused": null,
                        "originate_dial_string": "",                        
                        "id": 1,
                        "name": "Default_Gateway"
                    },
                    "extra_data": "2000",
                    "calltimeout": 60
                }
            ]

        **Error**:

            * Campaign(s) not found
        """
        base = Campaign.objects
        if campaign_id:
            try:
                list_campaign = base.get(id=campaign_id)
                return list_campaign
            except:
                return rc.NOT_FOUND
        else:
            return base.all().order_by('-id')[:10]

    @throttle(100, 1 * 60) # allow 100 times in 1 minutes
    def update(self, request, campaign_id):
        """API to update campaign status or settings

        **Attributes**:

            * ``campaign_id`` - Campaign ID
            * ``status`` - New campaign status values (1:START, 2:PAUSE,\
            3:ABORT, 4:END)
            * ``startingdate`` - Start date. Epoch Time, ie 1301414368
            * ``expirationdate`` - Expiry date. Epoch Time, ie 1301414368
            * ``daily_start_time`` - Daily Start Time, default '00:00:00'
            * ``daily_stop_time`` - Daily Stop Time, default '23:59:59'
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
            * ``frequency`` - Defines the frequency and speed of the campaign.\
                              This is the number of calls per minute.
            * ``callmaxduration`` - Defines the maximum call duration.
            * ``maxretry`` - Defines the max retries allowed per user.
            * ``intervalretry`` - Defines the time to wait between retries\
                                  in seconds
            * ``calltimeout`` - Defines the number of second to timeout on calls
            * ``aleg_gateway`` - Defines the Gateway to use to call the\
                                 subscriber
            * ``voipapp`` - Defines the VoIP application
            * ``extra_data`` - Defines the additional data to pass to the\
                                 application
           

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X PUT http://127.0.0.1:8000/api/dialer_campaign/campaign/%campaign_id%/ -d "status=2"

            curl -u username:password -i -H "Accept: application/json" -X PUT http://127.0.0.1:8000/api/dialer_campaign/campaign/%campaign_id%/ -d "callerid=123987&status=2&startingdate=1301392136.0&expirationdate=1301332136.0&frequency=20&callmaxduration=50&maxretry=3&intervalretry=3000&calltimeout=60&aleg_gateway=1&voipapp=1&extra_data=2000"

        **Example Response**::

            {
                "status": "2",
                "voipapp": {
                    "gateway_id": 1,
                    "updated_date": "2011-06-22 09:58:22",
                    "user_id": 1,
                    "description": "",
                    "created_date": "2011-04-08 08:00:09",
                    "type": 1,
                    "id": 1,
                    "name": "Default_VoIP_App"
                },
                "startingdate": "2011-06-28 06:46:08",
                "name": "Default_Campaign",
                "callerid": "123987",
                "callmaxduration": 50,
                "intervalretry": 3000,
                "id": 1,
                "phonebook": [
                    {
                        "name": "Default_Phonebook",
                        "id": 1
                    }
                ],
                "frequency": 20,
                "maxretry": 3,
                "expirationdate": "2011-07-05 06:46:08",
                "campaign_code": "XIUER",
                "aleg_gateway": {
                    "status": 1,
                    "updated_date": "2011-06-15 00:28:52",
                    "addparameter": "",
                    "addprefix": "",
                    "description": "",
                    "gateway_codecs": "PCMA,PCMU",
                    "failover_id": null,
                    "count_call": null,
                    "created_date": "2011-06-15 00:28:52",
                    "maximum_call": null,
                    "gateway_timeouts": "10,10",
                    "count_in_use": null,
                    "removeprefix": "",
                    "gateway_retries": "2,1",
                    "gateways": "user/,user",
                    "secondused": null,
                    "originate_dial_string": "", 
                    "id": 1,
                    "name": "Default_Gateway"
                },
                "extra_data": "2000",
                "calltimeout": 60
            }

        **Error**:

            * Campaign not found.
        """
        if user_attached_with_dialer_settings(request):
            resp = rc.BAD_REQUEST
            resp.write("Your settings are not configured properly, \
                 Please contact the administrator.")
            return resp
        attrs = self.flatten_dict(request.POST)

        #Retrieve Post settings
        status = get_attribute(attrs, 'status')
        callerid = get_attribute(attrs, 'callerid')
        startingdate = get_attribute(attrs, 'startingdate')
        expirationdate = get_attribute(attrs, 'expirationdate')
        daily_start_time = get_attribute(attrs, 'daily_start_time')
        daily_stop_time = get_attribute(attrs, 'daily_stop_time')
        monday = get_attribute(attrs, 'monday')
        tuesday = get_attribute(attrs, 'tuesday')
        wednesday = get_attribute(attrs, 'wednesday')
        thursday = get_attribute(attrs, 'thursday')
        friday = get_attribute(attrs, 'friday')
        saturday = get_attribute(attrs, 'saturday')
        sunday = get_attribute(attrs, 'sunday')
        frequency = get_attribute(attrs, 'frequency')
        if frequency and check_dialer_setting(request,
                                check_for="frequency",
                                field_value=int(frequency)):
            resp = rc.BAD_REQUEST
            resp.write("Maximum Frequency limit of %s exceeded." \
            % dialer_setting_limit(request, limit_for="frequency"))
            return resp

        callmaxduration = get_attribute(attrs, 'callmaxduration')
        if callmaxduration and check_dialer_setting(request,
                                check_for="duration",
                                field_value=int(callmaxduration)):
            resp = rc.BAD_REQUEST
            resp.write("Maximum Duration limit of %s exceeded." \
            % dialer_setting_limit(request, limit_for="duration"))
            return resp

        maxretry = get_attribute(attrs, 'maxretry')
        if maxretry and check_dialer_setting(request,
                                check_for="retry",
                                field_value=int(maxretry)):
            resp = rc.BAD_REQUEST
            resp.write("Maximum Retries limit of %s exceeded." \
            % dialer_setting_limit(request, limit_for="retry"))
            return resp
        intervalretry = get_attribute(attrs, 'intervalretry')
        calltimeout = get_attribute(attrs, 'calltimeout')
        if calltimeout and check_dialer_setting(request,
                                check_for="timeout",
                                field_value=int(calltimeout)):
            resp = rc.BAD_REQUEST
            resp.write("Maximum Timeout limit of %s exceeded." \
            % dialer_setting_limit(request, limit_for="timeout"))
            return resp

        aleg_gateway = get_attribute(attrs, 'aleg_gateway')
        voipapp = get_attribute(attrs, 'voipapp')
        extra_data = get_attribute(attrs, 'extra_data')
        startingdate = get_value_if_none(startingdate, time.time())
        # expire in 7 days
        expirationdate = \
        get_value_if_none(expirationdate, time.time() + 86400 * 7)
        startingdate = \
        time.strftime('%Y-%m-%d %H:%M:%S',
                      time.gmtime(float(startingdate)))
        expirationdate = \
        time.strftime('%Y-%m-%d %H:%M:%S',
                      time.gmtime(float(expirationdate)))
        daily_start_time = get_value_if_none(daily_start_time, '00:00:00')
        daily_stop_time = get_value_if_none(daily_stop_time, '23:59:59')
        monday = get_value_if_none(monday, 1)
        tuesday = get_value_if_none(tuesday, 1)
        wednesday = get_value_if_none(wednesday, 1)
        thursday = get_value_if_none(thursday, 1)
        friday = get_value_if_none(friday, 1)
        saturday = get_value_if_none(saturday, 1)
        sunday = get_value_if_none(sunday, 1)
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            save_if_set(campaign, 'callerid', callerid)
            save_if_set(campaign, 'status', int(status))
            save_if_set(campaign, 'startingdate', startingdate)
            save_if_set(campaign, 'expirationdate', expirationdate)
            save_if_set(campaign, 'frequency', frequency)
            save_if_set(campaign, 'callmaxduration', callmaxduration)
            save_if_set(campaign, 'maxretry', maxretry)
            save_if_set(campaign, 'intervalretry', intervalretry)
            save_if_set(campaign, 'calltimeout', calltimeout)
            save_if_set(campaign, 'aleg_gateway_id', aleg_gateway)
            save_if_set(campaign, 'voipapp_id', voipapp)
            save_if_set(campaign, 'extra_data', extra_data)
            save_if_set(campaign, 'daily_start_time', daily_start_time)
            save_if_set(campaign, 'daily_stop_time', daily_stop_time)
            save_if_set(campaign, 'monday', monday)
            save_if_set(campaign, 'tuesday', tuesday)
            save_if_set(campaign, 'wednesday', wednesday)
            save_if_set(campaign, 'thursday', thursday)
            save_if_set(campaign, 'friday', friday)
            save_if_set(campaign, 'saturday', saturday)
            save_if_set(campaign, 'sunday', sunday)
            campaign.save()
            return campaign
        except:
            return rc.NOT_FOUND

    @throttle(100, 1 * 60) # allow 100 times in 1 minutes
    def delete(self, request, campaign_id):
        """API to delete campaign status

        **Attributes**:

            * ``campaign_id`` - Campaign ID

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X DELETE http://127.0.0.1:8000/api/dialer_campaign/campaign/%campaign_id%/

        **Example Response**::

            HTTP/1.0 204 NO CONTENT
            Date: Wed, 18 May 2011 13:23:14 GMT
            Server: WSGIServer/0.1 Python/2.6.2
            Vary: Authorization
            Content-Length: 0
            Content-Type: text/plain

        **Error**:

            * NOT FOUND Campaign ID doesn't exist.
        """
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            campaign.delete()
            resp = rc.DELETED
            resp.write(" Campaign is deleted")
            return resp
        except:
            resp = rc.NOT_FOUND
            resp.write(" Campaign ID doesn't exist")
            return resp


class phonebookHandler(BaseHandler):
    """This API provides Phonebook management giving basic functions
    to create and read phonebooks."""
    model = Phonebook
    allowed_methods = ('POST', 'GET',)
    fields = ('id', 'name', 'description', ('campaign', ('id', 'name',)))

    @classmethod
    def content_length(cls, phonebook):
        return len(phonebook.content)

    @staticmethod
    def resource_uri(self):
        return ('api_phonebook_handler', ['campaign_id'])

    def create(self, request):
        """API to create a new phonebook

        **Attributes**:

            * ``name`` - Name of the Phonebook
            * ``description`` - Short description of the Campaign
            * ``campaign_id`` - Campaign ID

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_campaign/phonebook/ -d "name=mylittlephonebook&description=&campaign_id=1"

        **Example Response**::

            {
                "id": 1,
                "name": "mylittlephonebook",
                "description": ""
            }

        **Error**:

            * The Campaign ID doesn't exist!
            * Error adding Phonebook!
        """
        attrs = self.flatten_dict(request.POST)

        campaign_id = get_attribute(attrs, 'campaign_id')
        name = get_attribute(attrs, 'name')
        description = get_attribute(attrs, 'description')
        
        try:
            obj_campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            resp = rc.BAD_REQUEST
            resp.write("The Campaign ID doesn't exist!")
            return resp

        try:
            new_phonebook = Phonebook.objects.create(user=request.user,
                                    name=name,
                                    description=description,)
            obj_campaign.phonebook.add(new_phonebook)
            obj_campaign.save()

        except IntegrityError:
            #raise
            resp = rc.BAD_REQUEST
            resp.write("Error adding Phonebook!")
            return resp

        return new_phonebook

    @throttle(1000, 1 * 60) #  Throttle if more that 1000 times within 1 minute
    def read(self, request, phonebook_id=None):
        """API to read all created phonebooks, or a specific phonebook\
        if a phonebook_id is supplied

        **Attributes**:

            * ``phonebook_id`` - Phonebook ID

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/dialer_campaign/phonebook/

            curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/dialer_campaign/phonebook/%phonebook_id%/

        **Example Response**::

            [
                {
                    "id": 2,
                    "name": "mylittlephonebook",
                    "description": ""
                },
                {
                    "id": 1,
                    "name": "Default_Phonebook",
                    "description": "This is default phone book"
                }
            ]

        **Error**:

            * Phonebook not found
        """
        base = Phonebook.objects
        if phonebook_id:
            try:
                list_phonebook = base.get(id=phonebook_id)
                return list_phonebook
            except:
                return rc.NOT_FOUND
        else:
            return base.all().order_by('-id')[:10]


class contactHandler(BaseHandler):
    """This API provides as Contact management, giving basic function
    to create, read and update contacts."""
    model = CampaignSubscriber
    allowed_methods = ('POST', 'GET', 'PUT',)
    fields = ('id', 'contact', 'last_name', 'first_name', 'description',
              'status', 'additional_vars', ('phonebook', ('id', 'last_name', )))

    @classmethod
    def content_length(cls, subscriber):
        return len(subscriber.content)

    @staticmethod
    def resource_uri(self):
        return ('subscriber', ['json'])

    def create(self, request):
        """API to create a new contact

        **Attributes Details**:

            * ``contact`` - contact number of the Subscriber
            * ``last_name`` - last name of the Subscriber
            * ``first_name`` - first name of the Subscriber
            * ``email`` - email id of the Subscriber
            * ``description`` - Short description of the Subscriber
            * ``additional_vars`` - Additional settings for the Subscriber
            * ``phonebook_id`` - the phonebook Id to which we want to add\
            the Subscriber

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_campaign/contact/ -d "contact=650784355&last_name=belaid&first_name=areski&email=areski@gmail.com&phonebook_id=1"

        **Example Response**::

            {
                "status": 1,
                "contact": {
                    "status": 1,
                    "updated_date": "2011-05-09 02:16:29",
                    "last_name": "belaid",
                    "first_name": "areski",
                    "email": "areski@gmail.com",
                    "additional_vars": "",
                    "phonebook": {
                        "id": 1,
                        "name": "Default_Phonebook",
                        "description": "This is default phone book"
                    },
                    "contact": "650784355",
                    "created_date": "2011-05-09 02:16:29",
                    "description": null
                },
                "id": 1
            }

        **Error**:

            * You have too many contacts per campaign.
              You are allowed a maximum of xxx
            * The PhoneBook ID doesn't exist!
            * The contact duplicated xxxxxxxxxxxxx
        """
        if check_dialer_setting(request, check_for="contact"):
            resp = rc.BAD_REQUEST
            resp.write("You have too many contacts per campaign. \
            You are allowed a maximum of %s" \
            % dialer_setting_limit(request, limit_for="contact"))
            return resp
        else:
            attrs = self.flatten_dict(request.POST)

            contact = get_attribute(attrs, 'contact')
            last_name = get_attribute(attrs, 'last_name')
            first_name = get_attribute(attrs, 'first_name')
            email = get_attribute(attrs, 'email')
            description = get_attribute(attrs, 'description')
            status = 1 # per default
            phonebook_id = get_attribute(attrs, 'phonebook_id')
            
            #TODO: Check it owns by user
            try:
                obj_phonebook = Phonebook.objects.get(id=phonebook_id)
            except Phonebook.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write("The PhoneBook ID doesn't exist!")
                return resp

            try:
                #this method will also create a record into CampaignSubscriber
                #this is defined in signal post_save_add_contact
                new_contact = Contact.objects.create(
                                        contact=contact,
                                        last_name=last_name,
                                        first_name=first_name,
                                        email=email,
                                        description=description,
                                        status=status,
                                        phonebook=obj_phonebook)
            except IntegrityError:
                #raise
                resp = rc.DUPLICATE_ENTRY
                resp.write("The contact duplicated (%s)!" % str(contact))
                return resp

            get_campaignsubscriber = CampaignSubscriber.objects\
                                     .get(contact=new_contact)

            #return the new subscribed contact
            return get_campaignsubscriber

    @throttle(1000, 1 * 60) #  Throttle if more that 1000 times within 1 minute
    def read(self, request, campaign_id=None, contact=None):
        """API to read all pending contacts, or a specific contact if \
        a contact_id is supplied

        **Attributes**:

            * ``campaign_id`` - Campaign ID
            * ``contact`` - contact number of the subscriber

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/dialer_campaign/contact/%campaign_id%/

            curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/dialer_campaign/contact/%campaign_id%/%contact%/

        **Example Response**::

            [
                {
                    "status": null,
                    "contact_id": 1,
                    "last_attempt": null,
                    "count_attempt": 0
                },
                {
                    "status": null,
                    "contact_id": 4,
                    "last_attempt": null,
                    "count_attempt": 0
                }
            ]

        **Error**:

            * No value for Campaign ID !
        """
        from django.db import connection, transaction
        cursor = connection.cursor()

        if not campaign_id:
            resp = rc.BAD_REQUEST
            resp.write("No value for Campaign ID !")
            return resp

        if contact:
            if not isint(contact):
                resp = rc.BAD_REQUEST
                resp.write("Wrong value for contact !")
                return resp

            sql_statement = 'SELECT contact_id, last_attempt, count_attempt,'\
                    'dialer_campaign_subscriber.status '\
                    'FROM dialer_campaign_subscriber '\
                    'LEFT JOIN dialer_callrequest ON '\
                    'campaign_subscriber_id=dialer_campaign_subscriber.id '\
                    'LEFT JOIN dialer_campaign ON '\
                    'dialer_callrequest.campaign_id=dialer_campaign.id '\
                    'WHERE dialer_campaign_subscriber.campaign_id = %s '\
                    'AND dialer_campaign_subscriber.duplicate_contact = "%s"'\
                    % (str(campaign_id), str(contact))

        else:
            sql_statement = 'SELECT contact_id, last_attempt, count_attempt,'\
                        'dialer_campaign_subscriber.status '\
                        'FROM dialer_campaign_subscriber '\
                        'LEFT JOIN dialer_callrequest ON '\
                        'campaign_subscriber_id=' \
                        'dialer_campaign_subscriber.id '\
                        'LEFT JOIN dialer_campaign ON '\
                        'dialer_callrequest.campaign_id=dialer_campaign.id '\
                        'WHERE dialer_campaign_subscriber.campaign_id' \
                        '= %s' % (str(campaign_id))

        cursor.execute(sql_statement)
        row = cursor.fetchall()

        result = []
        for record in row:
            modrecord = {}
            modrecord['contact_id'] = record[0]
            modrecord['last_attempt'] = record[1]
            modrecord['count_attempt'] = record[2]
            modrecord['status'] = record[3]
            result.append(modrecord)

        return result

    @throttle(1000, 1 * 60) #  allow 1000 times in 1 minutes
    def update(self, request, campaign_id=None, contact=None):
        """API to update a contact

        **Attributes**:

            * ``campaign_id`` - Campaign ID
            * ``contact`` - contact number of the subscriber
            * ``status`` - campaign subscriber status values (1:START, \
            2:PAUSE, 3:ABORT, 4:FAIL, 5:COMPLETE)

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X PUT http://127.0.0.1:8000/api/dialer_campaign/contact/%campagin_id%/%contact%/ -d "status=2"

        **Example Response**::

            {
                "status": "2",
                "contact": {
                    "status": 1,
                    "updated_date": "2011-04-29 08:44:26",
                    "name": "Belaid Arezqui",
                    "additional_vars": "amount=1",
                    "phonebook": {
                        "id": 1,
                        "name": "Default_Phonebook",
                        "description": "This is default phone book"
                    },
                    "contact": "650784355",
                    "created_date": "2011-04-29 08:44:26",
                    "description": "Happy customer"
                },
                "id": 1
            }

        **Error**:

            * CampaignSubscriber is not found
        """
        try:
            campaignsubscriber = \
            CampaignSubscriber.objects.get(duplicate_contact=contact,
                                           campaign=campaign_id)
            campaignsubscriber.status = request.PUT.get('status')
            campaignsubscriber.save()
            return campaignsubscriber
        except:
            return rc.NOT_FOUND


class bulkcontactHandler(BaseHandler):
    """This API  provides basic functionality to bulk create contacts."""
    model = Contact
    allowed_methods = ('POST',)

    @classmethod
    def content_length(cls, contact):
        return len(contact.content)

    @staticmethod
    def resource_uri(self):
        return ('contact', ['json'])

    def create(self, request):
        """API to bulk create contacts

        **Attributes**

            * ``contact`` - contact number of the Subscriber
            * ``phonebook_id`` - the phonebook Id to which we want to add\
            the contact

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_campaign/bulkcontact/ -d "phonebook_id=1&phoneno_list=12345,54344"

        **Example Response**::

            HTTP/1.0 200 OK
            Date: Mon, 09 May 2011 07:25:44 GMT
            Server: WSGIServer/0.1 Python/2.6.2
            Vary: Authorization
            Content-Type: application/json; charset=utf-8

            2

        **Error**:

            * You have too many contacts per campaign.
              You are allowed a maximum of xxx
            * The PhoneBook ID doesn't exist!
            * The contact duplicated xxxx!
        """
        if check_dialer_setting(request, check_for="contact"):
            resp = rc.BAD_REQUEST
            resp.write("You have too many contacts per campaign. \
                You are allowed a maximum of %s" \
                % dialer_setting_limit(request, limit_for="contact"))
            return resp
        else:
            attrs = self.flatten_dict(request.POST)
            phoneno_list = get_attribute(attrs, 'phoneno_list')
            phonenolist = list(phoneno_list.split(","))
            total_no = len(list(phonenolist))

            phonebook_id = get_attribute(attrs, 'phonebook_id')

            # TODO: Check it owns by user
            try:
                obj_phonebook = Phonebook.objects.get(id=phonebook_id)
            except Phonebook.DoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write("The PhoneBook ID doesn't exist!")
                return resp

            try:
                new_contact_count = 0
                for phoneno in phonenolist:
                    new_contact = Contact.objects.create(
                                            phonebook=obj_phonebook,
                                            contact=phoneno,)
                    new_contact_count = new_contact_count + 1
                    new_contact.save()

            except IntegrityError:
                resp.write("The contact duplicated (%s)!\n" % phoneno)
                pass

            # return the new subscribed contact
            return new_contact_count


class campaignDeleteCascadeHandler(BaseHandler):
    """This API provides provides basic functionality
    to delete campaigns."""
    allowed_methods = ('DELETE')

    @classmethod
    def content_length(cls, campaign):
        return len(campaign.content)

    @staticmethod
    def resource_uri(self):
        return ('campaign', ['json'])

    @throttle(100, 1 * 60) # allow 100 times in 1 minutes
    def delete(self, request, campaign_id):
        """API to delete campaign status

        **Attributes**:

            * ``campaign_id`` - Campaign ID

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X DELETE http://127.0.0.1:8000/api/dialer_campaign/campaign/delete_cascade/%campaign_id%/

        **Example Response**::

            HTTP/1.0 204 NO CONTENT
            Date: Wed, 18 May 2011 13:23:14 GMT
            Server: WSGIServer/0.1 Python/2.6.2
            Vary: Authorization
            Content-Length: 0
            Content-Type: text/plain

        **Error**:

            * NOT FOUND Campaign ID doesn't exist.
        """
        try:
            del_campaign = Campaign.objects.get(id=campaign_id)
            phonebook_count = del_campaign.phonebook.all().count()

            if phonebook_count == 0:
                del_campaign.delete()
                resp = rc.DELETED
                resp.write(" Campaign is deleted !")
            else: # phonebook_count > 0
                other_campaing_count = \
                Campaign.objects.filter(user=request.user,
                         phonebook__in=del_campaign.phonebook.all())\
                .exclude(id=campaign_id).count()

                if other_campaing_count == 0:
                    # delete phonebooks as well as contacts belong to it

                    # 1) delete all contacts which are belong to phonebook
                    contact_list = Contact.objects\
                    .filter(phonebook__in=del_campaign.phonebook.all())
                    total_contact = contact_list.count()
                    contact_list.delete()

                    # 2) delete phonebook
                    phonebook_list = Phonebook.objects\
                    .filter(id__in=del_campaign.phonebook.all())
                    total_phonebook = phonebook_list.count()
                    phonebook_list.delete()

                    # 3) delete campaign
                    del_campaign.delete()
                    resp = rc.DELETED
                    resp.write("Campaign is deleted with %d phonebook(s)\
                           & its %d contact(s)!" % (total_phonebook,
                                                    total_contact))
                else:
                    del_campaign.delete()
                    resp = rc.DELETED
                    resp.write(" Campaign is deleted !")
            return resp
        except:
            resp = rc.NOT_FOUND
            resp.write(" Campaign ID doesn't exist")
            return resp
