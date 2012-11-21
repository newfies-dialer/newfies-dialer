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

from django.conf import settings
from common.common_functions import variable_value


def get_pagination_vars(request, col_field_list, default_sort_field):
    """Return data for pagination"""
    # Define no of records per page
    PAGE_SIZE = settings.PAGE_SIZE
    try:
        PAGE_NUMBER = int(request.GET['page'])
    except:
        PAGE_NUMBER = 1

    # page index
    if PAGE_NUMBER > 1:
        start_page = (PAGE_NUMBER - 1) * int(PAGE_SIZE)
        end_page = start_page + int(PAGE_SIZE)
    else:
        start_page = int(0)
        end_page = int(PAGE_SIZE)

    # default column order
    col_name_with_order = {}
    for field_name in col_field_list:
        col_name_with_order[field_name] = '-' + field_name

    sort_field = variable_value(request, 'sort_by')
    if not sort_field:
        sort_field = default_sort_field  # default sort field
        sort_order = '-' + sort_field  # desc
    else:
        if "-" in sort_field:
            sort_order = sort_field
            col_name_with_order[sort_field[1:]] = sort_field[1:]
        else:
            sort_order = sort_field
            col_name_with_order[sort_field] = '-' + sort_field

    data = {
        'PAGE_SIZE': PAGE_SIZE,
        'PAGE_NUMBER': PAGE_NUMBER,
        'start_page': start_page,
        'end_page': end_page,
        'col_name_with_order': col_name_with_order,
        'sort_order': sort_order,
    }
    return data
