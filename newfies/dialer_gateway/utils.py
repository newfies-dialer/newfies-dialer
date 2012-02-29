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

from dialer_gateway.models import Gateway


def phonenumber_change_prefix(phone_number, gateway_id):
    """apply prefix modification for a given phone_number and gateway"""

    """
    **Attributes**:

        * ``name`` - Gateway name.
        * ``description`` - Description about Gateway.
        * ``addprefix`` - Add prefix.
        * ``removeprefix`` - Remove prefix.
        * ``gateways`` - "user/,user", # Gateway string to try dialing separated by comma. First in list will be tried first
        * ``gateway_codecs`` - "'PCMA,PCMU','PCMA,PCMU'", # Codec string as needed by FS for each gateway separated by comma
        * ``gateway_timeouts`` - "10,10", # Seconds to timeout in string for each gateway separated by comma
        * ``gateway_retries`` - "2,1", # Retry String for Gateways separated by comma, on how many times each gateway should be retried
        * ``originate_dial_string`` - originate_dial_string
        * ``secondused`` -
        * ``failover`` -
        * ``addparameter`` -
        * ``count_call`` -
        * ``count_in_use`` -
        * ``maximum_call`` -
        * ``status`` - Gateway status
    """
    try:
        obj_gateway = Gateway.objects.get(id=gateway_id)
    except:
        print 'Can\'t find this Gateway : %s' % gateway_id
        return False

    if not phone_number:
        return False
    
    if obj_gateway.status!=1:
        print 'Gateway not Active: %s' % gateway_id
        return False

    if len(obj_gateway.removeprefix) > 0 and phone_number.startswith(obj_gateway.removeprefix):
        phone_number = phone_number[len(obj_gateway.removeprefix):]

    phone_number = obj_gateway.addprefix + phone_number

    return phone_number
