#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
import plivohelper

REST_API_URL = 'http://127.0.0.1:8088'
API_VERSION = 'v0.1'

# Sid and AuthToken
SID = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'


def call_plivo(callerid=None, phone_number=None, Gateways=None,
               GatewayCodecs="'PCMA,PCMU'", GatewayTimeouts="60",
               GatewayRetries='1', ExtraDialString=None,
               AnswerUrl=None, HangupUrl=None, TimeLimit="3600"):
    # URL of the Plivo REST service

    # Define Channel Variable -
    # http://wiki.freeswitch.org/wiki/Channel_Variables
    extra_dial_string = "bridge_early_media=true,hangup_after_bridge=true"
    if len(ExtraDialString) > 0:
        extra_dial_string = extra_dial_string + ',' + ExtraDialString

    if not phone_number:
        print "Error : Phone Number needs to be defined!"
        return False

    if not callerid:
        callerid = '8888888888'

    if not GatewayCodecs:
        GatewayCodecs = "'PCMA,PCMU'"

    if not GatewayTimeouts:
        GatewayTimeouts = "1800"

    if not GatewayRetries:
        GatewayRetries = "1"

    if not TimeLimit:
        TimeLimit = "3600"

    # Create a REST object
    plivo = plivohelper.REST(REST_API_URL, SID, AUTH_TOKEN, API_VERSION)

    # Initiate a new outbound call to user/1000 using a HTTP POST
    call_params = {
        'From': callerid,  # Caller Id
        'To': phone_number,  # User Number to Call
        'Gateways': Gateways,  # Gateway string to try dialing separated by comma. First in list will be tried first
        'GatewayCodecs': GatewayCodecs,  # Codec string as needed by FS for each gateway separated by comma
        'GatewayTimeouts': GatewayTimeouts,  # Seconds to timeout in string for each gateway separated by comma
        'GatewayRetries': GatewayRetries,  # Retry String for Gateways separated by comma, on how many times each gateway should be retried
        'ExtraDialString': extra_dial_string,
        #TODO : Remove this
        #'AnswerUrl': 'http://localhost/~areski/django/MyProjects/plivohelper-php/examples/test.php',
        #'AnswerUrl': 'http://192.168.1.11:8000/api/dialer_cdr/answercall/',
        'AnswerUrl': AnswerUrl,
        'HangupUrl': HangupUrl,
        #TODO : Fix TimeLimit on Plivo
        #'TimeLimit': TimeLimit,
    }

    print call_params

    #Perform the Call on the Rest API
    try:
        result = plivo.call(call_params)
        if result:
            print "RESULT FROM PLIVO HELPER : " + result['RequestUUID']
            return result
    except Exception, e:
        print e
        raise

    return False
