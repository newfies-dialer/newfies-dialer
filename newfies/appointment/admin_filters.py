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
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext as _
from appointment.function_def import manager_list_of_calendar_user
from appointment.models.users import CalendarUserProfile


class ManagerFilter(SimpleListFilter):
    title = _('manager')
    parameter_name = 'manager'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return manager_list_of_calendar_user()

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is not None:
            calendar_user_id_list = CalendarUserProfile.objects.values_list('user_id', flat=True).filter(manager_id=self.value())
            return queryset.filter(id__in=calendar_user_id_list)
        else:
            return queryset
