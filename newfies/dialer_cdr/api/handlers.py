from piston.handler import BaseHandler
from piston.emitters import *
from piston.utils import rc, require_mime, require_extended, throttle
from dialer_cdr.models import Callrequest
from datetime import *
from random import choice
from random import seed
import uuid

seed()


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
    """
    function to generate password with a letter suffix
    """
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digit = "1234567890"
    pass_str_char = ''.join([choice(chars) for i in range(char_length)])
    pass_str_digit = ''.join([choice(digit) for i in range(digit_length)])
    return pass_str_char + pass_str_digit


class callrequestHandler(BaseHandler):
    """This API server as Callrequest management, it provides basic function
    to create, read and update callrequest."""
    model = Callrequest
    allowed_methods = ('GET', 'POST', 'PUT', )
    #anonymous = 'AnonymousLanguageHandler'

    @classmethod
    def content_length(cls, callrequest):
        return len(callrequest.content)

    @classmethod
    def resource_uri(cls, callrequest):
        return ('callrequest', ['json'])

    @throttle(1000, 1 * 60) # Throttle if more that 1000 times within 1 minute
    def read(self, request, callrequest_id=None):
        """API to read all pending callrequest, or a specific callrequest
        if callrequest_id is supplied

        **Attributes**:

            * ``callrequest_id``- Callrequest Id

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/dialer_cdr/callrequest/

            curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/dialer_cdr/callrequest/xx/

        **Example Response**::

            [
                {
                    "status": 4,
                    "callerid": "650784355",
                    "num_attempt": 0,
                    "timeout": "30000",
                    "voipapp": "",
                    "call_time": "2011-05-07 13:03:11",
                    "call_type": "",
                    "result": "",
                    "request_uuid": "2342jtdsf-00123",
                    "last_attempt_time": null,
                    "phone_number": "1231321"
                }
            ]

        **Error**:

            * Bad Request.
        """
        base = Callrequest.objects
        if callrequest_id:
            try:
                list_callrequest = base.get(id=callrequest_id)
                return list_callrequest
            except:
                return rc.BAD_REQUEST
        else:
            return base.all()

    def create(self, request):
        """Create new callrequest,
        Create a callrequest will spool a call directly from the platform using
        a gateway and an application
        This can be used if you are not willing to create campaign or
        subscriber to proceed calls.

        **Attributes**:

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



        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_cdr/callrequest/ -d "request_uuid=2342jtdsf-00123&call_time=YYYY-MM-DD HH:MM:SS&phone_number=8792749823&voipapp=&timeout=30000&callerid=650784355&call_type=1"

        **Example Response**::

            {
                "status": "1",
                "callerid": "650784355",
                "num_attempt": 0,
                "timeout": "30000",
                "voipapp": "",
                "call_time": "2011-05-07 13:03:11",
                "call_type": "",
                "result": "",
                "request_uuid": "2342jtdsf-00123",
                "last_attempt_time": null,
                "phone_number": "1231321"
            }

        **Error**:

            * Duplicate Entry
        """
        attrs = self.flatten_dict(request.POST)
        if self.exists(**attrs):
            return rc.DUPLICATE_ENTRY
        else:
            request_uuid = get_attribute(attrs, 'request_uuid')
            call_type = get_attribute(attrs, 'call_type')
            timeout = get_attribute(attrs, 'timeout')
            callerid = get_attribute(attrs, 'callerid')
            voipapp = get_attribute(attrs, 'voipapp')
            phone_number = get_attribute(attrs, 'phone_number')
            call_time = datetime.strptime(get_attribute(attrs,
                            'call_time'), '%Y-%m-%d %H:%M:%S')

            new_callrequest = Callrequest(request_uuid=request_uuid,
                            call_time=call_time,
                            phone_number=phone_number,
                            voipapp_id=voipapp,
                            timeout=timeout,
                            callerid=callerid,
                            call_type=call_type,
                            user=request.user)

            new_callrequest.save()
            return new_callrequest

    #@throttle(5, 10 * 60) # allow 5 times in 10 minutes
    def update(self, request, callrequest_id):
        """API to update callrequest

        **Attributes**:

            * ``status`` - Status Values (1:Pending, 2:Failure, 3:Retry, \
                           4:Success, 5:Abort, 6:Pause, 7:Process)

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X PUT http://127.0.0.1:8000/api/dialer_cdr/callrequest/%callrequest_id%/ -d "status=5"

        **Example Response**::

            {
                "status": "5",
                "callerid": "650784355",
                "num_attempt": 0,
                "timeout": "30000",
                "voipapp": "",
                "call_time": "2011-05-07 13:03:11",
                "call_type": "",
                "result": "",
                "request_uuid": "2342jtdsf-00123",
                "last_attempt_time": null,
                "phone_number": "1231321"
            }

        **Error**:

            * Not here.
        """
        try:
            callrequest = Callrequest.objects.get(id=callrequest_id)
            callrequest.status = request.PUT.get('status')
            callrequest.save()
            return callrequest
        except:
            return rc.NOT_HERE


class answercallHandler(BaseHandler):
    """This API server to answer call"""
    allowed_methods = ('POST', 'GET',)

    def create(self, request):
        """API to answer the call

        **Attributes**:

            * ``RequestUUID`` - A unique identifier for the API request.

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_cdr/answercall/ -d "RequestUUID=48092924-856d-11e0-a586-0147ddac9d3e"

        **Example Response**::

            {
                "result": "OK",
            }
        """

        """
        attrs = self.flatten_dict(request.POST)

        opt_RequestUUID = get_attribute(attrs, 'RequestUUID')

        if not opt_RequestUUID:
            resp = rc.BAD_REQUEST
            resp.write("Wrong parameters!")
            return resp

        # Update the Callrequest to Status Ok : A-Leg at least is fine
        try:
            obj_callrequest = \
                Callrequest.objects.get(uniqueid=opt_RequestUUID)
            #TODO : use constant
            Callrequest.status = 4 # SUCCESS
            obj_callrequest.save()
        except:
            return rc.NOT_FOUND

        if not obj_callrequest.voipapp:
            #TODO : change the rc.BAD_REQUEST to a server error
            resp = rc.BAD_REQUEST
            resp.write('This Call Request is not attached to a VoIP App')
            return resp
        
        # get the VoIP application
        if obj_callrequest.voipapp.type == 1:
            #Redirect
            RESTXML = '<xml redirect>'
        elif obj_callrequest.voipapp.type == 2:
            #PlayAudio
            RESTXML = '<xml playaudio>'
        elif obj_callrequest.voipapp.type == 3:
            #Conference
            RESTXML = '<xml conference>'
        """
        
        return [ {'Speak': 'Hello World'}, {'Dial': {'Number': '1000'}, },]

    def read(self, request):
        """API to answer the call

        **Attributes**:

            * ``RequestUUID`` - A unique identifier for the API request.

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X GET http://127.0.0.1:8000/api/dialer_cdr/answercall/ -d "RequestUUID=48092924-856d-11e0-a586-0147ddac9d3e"

        **Example Response**::

            {
                "result": "OK",
            }
        """

        # return <Speak>Hello World</Speak><Dial><Number>1000</Number></Dial>
        
        return [ {'Speak': 'Hello World'},
                 {'Dial': {'Number': '1000'}, },]



class hangupcallHandler(BaseHandler):
    """This API server to hangup call

    This will update the call with the final status
    """
    allowed_methods = ('POST',)

    def create(self, request):
        """API to hangup the call

        **Attributes**:

            * ``call-uuid`` - Call UUID

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_cdr/hangupcall/ -d "RequestUUID=48092924-856d-11e0-a586-0147ddac9d3e"

        **Example Response**::

            {
                "result": "OK",
            }
        """
        attrs = self.flatten_dict(request.POST)

        opt_request_uuid = get_attribute(attrs, 'RequestUUID')
        opt_hangup_cause = get_attribute(attrs, 'HangupCause')
        
        if not opt_request_uuid:
            resp = rc.BAD_REQUEST
            resp.write("Wrong parameters - missing RequestUUID!")
            return resp

        if not opt_hangup_cause:
            resp = rc.BAD_REQUEST
            resp.write("Wrong parameters - missing HangupCause!")
            return resp

        try:
            callrequest = Callrequest.objects.get(request_uuid=opt_request_uuid)
            # 2 / FAILURE ; 3 / RETRY ; 4 / SUCCESS
            if opt_hangup_cause=='NORMAL_CLEARING':
                callrequest.status = 4 # Success
            else:
                callrequest.status = 2 # Failure
            callrequest.hangup_cause = opt_hangup_cause
            callrequest.save()
        except:
            raise
            return rc.BAD_REQUEST

        #TODO : Create CDR

        return {'result': 'OK'}



class testcallHandler(BaseHandler):
    """This API server as Test suit to initiate call and retrieve their status

    It aims to be used as a test function that will simulate the behavior
    of sending the call via an API
    """
    allowed_methods = ('POST', )

    def create(self, request):
        """API to initiate a new call

        **Attributes**:

            * ``From`` - Caller Id
            * ``To`` - User Number to Call
            * ``Gateways`` - "user/,user", # Gateway string to try dialing separated by comma. First in list will be tried first
            * ``GatewayCodecs`` - "'PCMA,PCMU','PCMA,PCMU'", # Codec string as needed by FS for each gateway separated by comma
            * ``GatewayTimeouts`` - "10,10", # Seconds to timeout in string for each gateway separated by comma
            * ``GatewayRetries`` - "2,1", # Retry String for Gateways separated by comma, on how many times each gateway should be retried
            * ``OriginateDialString`` - originate_dial_string
            * ``AnswerUrl`` - "http://localhost/answer_url/",
            * ``HangUpUrl`` - "http://localhost/hangup_url/",
            * ``RingUrl`` - "http://localhost/ring_url/",

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_cdr/testcall/ -d "From=650784355&To=1000&Gateways=user/&AnswerUrl=http://localhost/answer_url/"

        **Example Response**::

            {
                "RequestUUID": '48092924-856d-11e0-a586-0147ddac9d3e'
            }

        **Error**:

            * Gateway error
            * User unreachable
            * Timeout
        """
        attrs = self.flatten_dict(request.POST)

        opt_from = get_attribute(attrs, 'From')
        opt_to = get_attribute(attrs, 'To')

        if not opt_from or not opt_to:
            resp = rc.BAD_REQUEST
            resp.write("Wrong parameters!")
            return resp

        request_uuid = str(uuid.uuid1())
        return {'RequestUUID': request_uuid}
