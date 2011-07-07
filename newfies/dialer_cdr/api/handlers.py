from piston.handler import BaseHandler
from piston.emitters import *
from piston.utils import rc, require_mime, require_extended, throttle
from dialer_cdr.models import Callrequest, VoIPCall
from voip_app.models import VoipApp
from datetime import datetime
from random import choice
from random import seed
import uuid
import time

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
    """function to generate password with a letter suffix"""
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
                        4:Success, 5:Abort, 6:Pause, 7:Process, 8: In-Progress)

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
    allowed_methods = ('POST',)

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
        return [ {'Speak': 'System error'},]
        
        attrs = self.flatten_dict(request.POST)

        opt_ALegRequestUUID = get_attribute(attrs, 'ALegRequestUUID')

        if not opt_ALegRequestUUID:
            resp = rc.BAD_REQUEST
            resp.write("Wrong parameters!")
            return resp

        # Update the Callrequest to Status Ok : A-Leg at least is fine
        try:
            #TODO: If we update the Call to success here we should not do it in hangup url
            obj_callrequest = \
                Callrequest.objects.get(request_uuid=opt_ALegRequestUUID)
            #TODO : use constant
            Callrequest.status = 8 # IN-PROGRESS
            obj_callrequest.save()
        except:
            resp = rc.NOT_FOUND
            resp.write('Call Request cannot be found!')
            return resp

        if not obj_callrequest.voipapp:
            resp = rc.NOT_IMPLEMENTED
            resp.write('This Call Request is not attached to a VoIP App')
            return resp

        # get the VoIP application
        if obj_callrequest.voipapp.type == 1:
            #Dial
            return [ {'Dial': {'Number': obj_callrequest.voipapp.data}, },]
        elif obj_callrequest.voipapp.type == 2:
            #PlayAudio
            return [ {'Play': obj_callrequest.voipapp.data},]
        elif obj_callrequest.voipapp.type == 3:
            #Conference
            return [ {'Conference': obj_callrequest.voipapp.data},]
        elif obj_callrequest.voipapp.type == 4:
            #Speak
            return [ {'Speak': obj_callrequest.voipapp.data},]

        #return [ {'Speak': 'Hello World'}, {'Dial': {'Number': '1000'}, },]
        return [ {'Speak': 'System error'},]


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

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_cdr/hangupcall/ -d "RequestUUID=48092924-856d-11e0-a586-0147ddac9d3e&HangupCause=SUBSCRIBER_ABSENT"

        **Example Response**::

            {
                "result": "OK",
            }
        """
        attrs = self.flatten_dict(request.POST)

        opt_request_uuid = get_attribute(attrs, 'RequestUUID')
        print opt_request_uuid
        opt_hangup_cause = get_attribute(attrs, 'HangupCause')
        print opt_hangup_cause

        if not opt_request_uuid:
            resp = rc.BAD_REQUEST
            resp.write("Wrong parameters - missing RequestUUID!")
            return resp

        if not opt_hangup_cause:
            resp = rc.BAD_REQUEST
            resp.write("Wrong parameters - missing HangupCause!")
            return resp

        try:
            callrequest = \
                Callrequest.objects.get(request_uuid=opt_request_uuid)
            # 2 / FAILURE ; 3 / RETRY ; 4 / SUCCESS
            if opt_hangup_cause=='NORMAL_CLEARING':
                callrequest.status = 4 # Success
            else:
                callrequest.status = 2 # Failure
            callrequest.hangup_cause = opt_hangup_cause
            callrequest.save()
        except:
            resp = rc.BAD_REQUEST
            resp.write("CallRequest not found!")
            return resp

        #TODO : Create CDR

        return {'result': 'OK'}


class cdrHandler(BaseHandler):
    """This API server to store CDR and relevant information attached to it
    """
    model = VoIPCall
    allowed_methods = ('POST', )


    @classmethod
    def content_length(cls, voipcall):
        return len(voipcall.content)

    @classmethod
    def resource_uri(cls, voipcall):
        return ('voipcall', ['json'])


    def create(self, request):
        """API to store CDR

        **Attributes**:

            * ``params`` -

        **CURL Usage**::

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_cdr/store_cdr/?uuid=48092924-856d-11e0-a586-0147ddac9d3e -d "cdr=thisismyxmlcdr"

            curl -u username:password -i -H "Accept: application/json" -X POST http://127.0.0.1:8000/api/dialer_cdr/store_cdr/ -d 'cdr=<?xml version="1.0"?><cdr><other></other><variables><plivo_request_uuid>7a641180-a742-11e0-b6b3-00231470a30c</plivo_request_uuid><duration>3</duration></variables><notvariables><plivo_request_uuid>TESTc</plivo_request_uuid><duration>5</duration></notvariables></cdr>'

        **Example Response**::

            {
                "status": 'OK'
            }

        **Error**:

            * Timeout
        """
        attrs = self.flatten_dict(request.POST)

        opt_cdr = str(get_attribute(attrs, 'cdr'))
        #print opt_cdr

        if not opt_cdr:
            resp = rc.BAD_REQUEST
            resp.write("Wrong parameters : missing cdr!")
            return resp

        data = {}
        import xml.etree.ElementTree as ET
        tree = ET.fromstring(opt_cdr)
        #parse file
        #tree = ET.parse("/tmp/cdr.xml")
        lst = tree.find("variables")

        cdr_vars = ['plivo_request_uuid', 'plivo_answer_url', 'plivo_app',
                    'direction', 'endpoint_disposition', 'hangup_cause',
                    'hangup_cause_q850', 'duration', 'billsec', 'progresssec',
                    'answersec', 'waitsec', 'mduration', 'billmsec',
                    'progressmsec', 'answermsec', 'waitmsec',
                    'progress_mediamsec', 'call_uuid',
                    'origination_caller_id_number', 'caller_id',
                    'answer_epoch', 'answer_uepoch']

        for j in lst:
            if j.tag in cdr_vars:
                data[j.tag] = j.text

        for element in cdr_vars:
            print element
            if not data.has_key(element):
                data[element] = None

        if not 'plivo_request_uuid' in data:
            #CDR not related to plivo
            #TODO : Add tag for newfies in outbound call
            return {'status': 'OK'}

        #TODO : delay if not find callrequest
        try:
            obj_callrequest = Callrequest.objects.get(request_uuid=data['plivo_request_uuid'])
        except:
            print "error get Callrequest %s " % data['plivo_request_uuid']
            raise

        if data.has_key('answer_epoch') and len(data['answer_epoch']) > 0:
            try:
                cur_answer_epoch = int(data['answer_epoch'])
            except ValueError:
                raise
            starting_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cur_answer_epoch))
        else:
            starting_date = None

        new_voipcall = VoIPCall(user = obj_callrequest.user,
                                request_uuid=data['plivo_request_uuid'],
                                used_gateway=None, #TODO
                                callrequest=obj_callrequest,
                                callid=data['call_uuid'] or '',
                                callerid=data['origination_caller_id_number'] or '',
                                phone_number=data['caller_id'] or '',
                                dialcode=None, #TODO
                                starting_date=starting_date,
                                duration=data['duration'] or 0,
                                billsec=data['billsec'] or 0,
                                progresssec=data['progresssec'] or 0,
                                answersec=data['answersec'] or 0,
                                disposition=data['endpoint_disposition'] or '',
                                hangup_cause=data['hangup_cause'] or '',
                                hangup_cause_q850=data['hangup_cause_q850'] or '',)

        new_voipcall.save()

        return new_voipcall


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
            * ``Gateways`` - "user/,user", # Gateway string to \
            try dialing separated by comma. First in list will be tried first
            * ``GatewayCodecs`` - "'PCMA,PCMU','PCMA,PCMU'", \
            # Codec string as needed by FS for each gateway separated by comma
            * ``GatewayTimeouts`` - "10,10", # Seconds to timeout in string\
            for each gateway separated by comma
            * ``GatewayRetries`` - "2,1",# Retry String for Gateways separated\
            by comma, on how many times each gateway should be retried
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
