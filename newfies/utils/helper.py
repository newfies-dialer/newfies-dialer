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


update_style = \
    'style="text-decoration:none;background-image:url(%snewfies/icons/page_edit.png);"' %\
    settings.STATIC_URL
delete_style = \
    'style="text-decoration:none;background-image:url(%snewfies/icons/delete.png);"' %\
    settings.STATIC_URL

# grid_test_data used in test-cases
grid_test_data = {'page': 1,
                  'rp': 10,
                  'sortname': 'id',
                  'sortorder': 'asc'}


def grid_common_function(request):
    """To get common flexigrid variable"""
    grid_data = {}

    grid_data['page'] = variable_value(request, 'page')
    grid_data['rp'] = variable_value(request, 'rp')
    grid_data['sortname'] = variable_value(request, 'sortname')
    grid_data['sortorder'] = variable_value(request, 'sortorder')
    grid_data['query'] = variable_value(request, 'query')
    grid_data['qtype'] = variable_value(request, 'qtype')

    # page index
    if int(grid_data['page']) > 1:
        grid_data['start_page'] = (int(grid_data['page']) - 1) * \
            int(grid_data['rp'])
        grid_data['end_page'] = grid_data['start_page'] + int(grid_data['rp'])
    else:
        grid_data['start_page'] = int(0)
        grid_data['end_page'] = int(grid_data['rp'])

    grid_data['sortorder_sign'] = ''
    if grid_data['sortorder'] == 'desc':
        grid_data['sortorder_sign'] = '-'

    return grid_data


def get_grid_update_delete_link(request, row_id, perm_name, title, action):
    """Function to check user permission to change or delete

        ``request`` - to check request.user.has_perm() attribute
        ``row_id`` - to pass record id in link
        ``link_style`` - update / delete link style
        ``title`` - alternate name of link
        ``action`` - link to update or delete
    """
    link = ''
    if action == 'update' and request.user.has_perm(perm_name):
        link = '<a href="%s/" class="icon" %s title="%s">&nbsp;</a>' %\
               (str(row_id), update_style, title)

    if action == 'delete' and request.user.has_perm(perm_name):
        link = '<a href="del/%s/" class="icon" %s onClick="return get_alert_msg(%s);" title="%s">&nbsp;</a>' %\
                    (str(row_id), delete_style, str(row_id), title)
    return link


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
