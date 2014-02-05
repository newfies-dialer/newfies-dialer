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
import newfies_dialer
from django.conf import settings
from dialer_campaign.function_def import user_dialer_setting_msg


def newfies_version(request):
    return {'newfies_version': newfies_dialer.__version__, 'SURVEYDEV': settings.SURVEYDEV}


def newfies_page_size(request):
    """return the value of PAGE_SIZE in templates"""
    return {'newfies_page_size': settings.PAGE_SIZE if settings.PAGE_SIZE else 10}


def newfies_dialer_setting_msg(request):
    """return dialer_setting_msg in templates"""
    return {'dialer_setting_msg': user_dialer_setting_msg(request.user)}
