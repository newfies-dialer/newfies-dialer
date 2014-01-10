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

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from dialer_settings.models import DialerSetting
from common.app_label_renamer import AppLabelRenamer
AppLabelRenamer(native_app_label=u'dialer_settings', app_label=_('Dialer Settings')).main()


# DialerSetting
class DialerSettingAdmin(admin.ModelAdmin):
    """Allows the administrator to view and modify certain attributes
    of a DialerSetting."""
    list_display = ('name', 'max_frequency', 'callmaxduration', 'maxretry',
                    'max_calltimeout', 'max_cpg', 'max_subr_cpg', 'max_contact',
                    'sms_max_frequency', 'sms_maxretry', 'sms_max_number_campaign',
                    'sms_max_number_subscriber_campaign', 'updated_date')
    # 'blacklist', 'whitelist',
    #list_filter = ['setting_group']
    search_fields = ('name', )
    ordering = ('-name', )

admin.site.register(DialerSetting, DialerSettingAdmin)
