#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from dialer_gateway.models import Gateway


#NOTE: This might get deleted as replaced by prepare_phonenumber
def phonenumber_change_prefix(phone_number, gateway_id):
    """
    apply prefix modification for a given phone_number and gateway
    """
    try:
        obj_gateway = Gateway.objects.get(id=gateway_id)
    except:
        print 'Can\'t find this Gateway : %s' % gateway_id
        return False

    if not phone_number:
        return False

    if obj_gateway.status != 1:
        #Gateway not Active
        return False

    if (len(obj_gateway.removeprefix) > 0
       and phone_number.startswith(obj_gateway.removeprefix)):
        phone_number = phone_number[len(obj_gateway.removeprefix):]

    phone_number = obj_gateway.addprefix + phone_number

    return phone_number


def prepare_phonenumber(phone_number, addprefix, removeprefix, gw_status):
    """
    apply prefix modification for a given phone_number and gateway
    """
    if not phone_number:
        return False

    if gw_status != 1:
        #Gateway not Active
        return False

    if (len(removeprefix) > 0
       and phone_number.startswith(removeprefix)):
        phone_number = phone_number[len(removeprefix):]

    phone_number = addprefix + phone_number

    return phone_number
