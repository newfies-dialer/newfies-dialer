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
# from django.utils.translation import ugettext as _
from mod_mailer.models import MailTemplate, MailSpooler


class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'template_key', 'label', 'from_email', 'from_name', 'subject', 'created_date')
    list_display_links = ['id', 'template_key']

admin.site.register(MailTemplate, MailTemplateAdmin)


#MailSpooler
class MailSpoolerAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailtemplate', 'contact_email', 'mailspooler_type', 'created_date')
    list_display_links = ['id', 'mailtemplate']
    #raw_id_fields = ('contact',)

admin.site.register(MailSpooler, MailSpoolerAdmin)
