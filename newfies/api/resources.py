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

from django.utils.encoding import smart_unicode
from django.utils.xmlutils import SimplerXMLGenerator

from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie import http

from dialer_cdr.models import VoIPCall
from settings_local import API_ALLOWED_IP
from random import seed
from cStringIO import StringIO
import urllib
import time
import logging

seed()


logger = logging.getLogger('newfies.filelog')


CDR_VARIABLES = ['plivo_request_uuid', 'plivo_answer_url', 'plivo_app',
                 'direction', 'endpoint_disposition', 'hangup_cause',
                 'hangup_cause_q850', 'duration', 'billsec', 'progresssec',
                 'answersec', 'waitsec', 'mduration', 'billmsec',
                 'progressmsec', 'answermsec', 'waitmsec',
                 'progress_mediamsec', 'call_uuid',
                 'origination_caller_id_number', 'caller_id',
                 'answer_epoch', 'answer_uepoch']


class CustomJSONSerializer(Serializer):

    def from_json(self, content):
        decoded_content = urllib.unquote(content.decode("utf8"))
        #data = simplejson.loads(content)
        data = {}
        data['cdr'] = decoded_content[4:]
        return data


def create_voipcall(obj_callrequest, plivo_request_uuid, data, data_prefix='',
    leg='a', hangup_cause='', from_plivo='', to_plivo=''):
    """
    Common function to create CDR / VoIP Call

    **Attributes**:

        * data : list with call details data
        * obj_callrequest:  refer to the CallRequest object
        * plivo_request_uuid : cdr uuid

    """

    if 'answer_epoch' in data and data['answer_epoch']:
        try:
            cur_answer_epoch = int(data['answer_epoch'])
        except ValueError:
            raise
        starting_date = time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(cur_answer_epoch))
    else:
        starting_date = None

    if leg == 'a':
        #A-Leg
        leg_type = 1
        used_gateway = obj_callrequest.aleg_gateway
    else:
        #B-Leg
        leg_type = 2
        used_gateway = obj_callrequest.content_object.gateway

    #check the right variable for hangup cause
    data_hangup_cause = data["%s%s" % (data_prefix, 'hangup_cause')]
    if data_hangup_cause and data_hangup_cause != '':
        cdr_hangup_cause = data_hangup_cause
    else:
        cdr_hangup_cause = hangup_cause

    if cdr_hangup_cause == 'USER_BUSY':
        disposition = 'BUSY'
    else:
        disposition = data["%s%s" % \
                        (data_prefix, 'endpoint_disposition')] or ''

    logger.debug('Create CDR - request_uuid=%s ; leg=%d ; hangup_cause= %s' % \
                    (plivo_request_uuid, leg_type, cdr_hangup_cause))

    new_voipcall = VoIPCall(
                    user=obj_callrequest.user,
                    request_uuid=plivo_request_uuid,
                    leg_type=leg_type,
                    used_gateway=used_gateway,
                    callrequest=obj_callrequest,
                    callid=data["%s%s" % (data_prefix, 'call_uuid')] or '',
                    callerid=from_plivo,
                    phone_number=to_plivo,
                    dialcode=None,  # TODO
                    starting_date=starting_date,
                    duration=data["%s%s" % (data_prefix, 'duration')] or 0,
                    billsec=data["%s%s" % (data_prefix, 'billsec')] or 0,
                    progresssec=data["%s%s" % \
                                        (data_prefix, 'progresssec')] or 0,
                    answersec=data["%s%s" % (data_prefix, 'answersec')] or 0,
                    disposition=disposition,
                    hangup_cause=cdr_hangup_cause,
                    hangup_cause_q850=data["%s%s" % \
                                    (data_prefix, 'hangup_cause_q850')] or '',)

    new_voipcall.save()


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


def save_if_set(record, fproperty, value):
    """function to save a property if it has been set"""
    if value:
        record.__dict__[fproperty] = value


class IpAddressAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        if request.META['REMOTE_ADDR'] in API_ALLOWED_IP:
            return True
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())
            return False


class IpAddressAuthentication(Authentication):
    def is_authorized(self, request, object=None):
        if request.META['REMOTE_ADDR'] in API_ALLOWED_IP:
            return True
        else:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())
            return False


class CustomXmlEmitter():
    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                self._to_xml(xml, item)
        elif isinstance(data, dict):
            for key, value in data.iteritems():
                xml.startElement(key, {})
                self._to_xml(xml, value)
                xml.endElement(key.split()[0])
        else:
            xml.characters(smart_unicode(data))

    def render(self, request, data):
        stream = StringIO()
        xml = SimplerXMLGenerator(stream, "utf-8")
        xml.startDocument()
        xml.startElement("Response", {})
        self._to_xml(xml, data)
        xml.endElement("Response")
        xml.endDocument()
        return stream.getvalue()
