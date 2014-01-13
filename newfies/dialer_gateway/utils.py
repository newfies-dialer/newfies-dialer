#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2014 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from dialer_gateway.constants import GATEWAY_STATUS


def prepare_phonenumber(phone_number, addprefix, removeprefix, gw_status):
    """
    apply prefix modification for a given phone_number and gateway
    """
    if not phone_number:
        return False

    if gw_status != GATEWAY_STATUS.ACTIVE:
        #Gateway not Active
        return False

    if (len(removeprefix) > 0
       and phone_number.startswith(removeprefix)):
        phone_number = phone_number[len(removeprefix):]

    phone_number = addprefix + phone_number

    return phone_number
