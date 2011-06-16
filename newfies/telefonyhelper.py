import plivohelper


REST_API_URL = 'http://127.0.0.1:8088'
API_VERSION = 'v0.1'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'


def call_plivo(callerid=None, phone_number=None, Gateways=None, GatewayCodecs=None, 
                    GatewayTimeouts=None, GatewayRetries=None, ExtraDialString=None, 
                    AnswerUrl=None, HangupUrl=None, RingUrl=None, TimeLimit=None, 
                    HangupOnRing=None):
    # URL of the Plivo REST service
    
    # Define Channel Variable - http://wiki.freeswitch.org/wiki/Channel_Variables
    extra_dial_string = "bridge_early_media=true,hangup_after_bridge=true"

    # Create a REST object
    plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)

    # Initiate a new outbound call to user/1000 using a HTTP POST
    call_params = {
        'From': '919191919191', # Caller Id
        'To' : '1000', # User Number to Call
        'Gateways' : "user/,user/", # Gateway string to try dialing separated by comma. First in list will be tried first
        'GatewayCodecs' : "'PCMA,PCMU','PCMA,PCMU'", # Codec string as needed by FS for each gateway separated by comma
        'GatewayTimeouts' : "10,10",      # Seconds to timeout in string for each gateway separated by comma
        'GatewayRetries' : "2,1", # Retry String for Gateways separated by comma, on how many times each gateway should be retried
        'ExtraDialString' : extra_dial_string,
        'AnswerUrl' : "http://127.0.0.1:5000/answered/",
        'HangupUrl' : "http://127.0.0.1:5000/hangup/",
        #'RingUrl' : "http://127.0.0.1:5000/ringing/",
        #'TimeLimit' : '10',
        #'HangupOnRing': '0',
    }

    #Perform the Call on the Rest API
    try:
        result = plivo.call(call_params)
        if result:
            print result['RequestUUID']
            return result
    except Exception, e:
        print e
        raise

    return False
