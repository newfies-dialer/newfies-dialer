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


update_style = 'style="text-decoration:none;background-image:url(' + \
                    settings.STATIC_URL + 'newfies/icons/page_edit.png);"'
delete_style = 'style="text-decoration:none;background-image:url(' + \
                settings.STATIC_URL + 'newfies/icons/delete.png);"'

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
    if action=='update' and request.user.has_perm(perm_name):
        link = '<a href="' + str(row_id) + '/" class="icon" '\
               + update_style + ' title="' + title + '">&nbsp;</a>'

    if action=='delete' and request.user.has_perm(perm_name):
        link = '<a href="del/' + str(row_id) + '/" class="icon" '\
               + delete_style + ' onClick="return get_alert_msg('\
               + str(row_id) + ');" title="' + title + '">&nbsp;</a>'
    return link



import inspect


#TODO: Move this to common libs
class Choice(object):

    class __metaclass__(type):
        def __init__(self, name, type, other):
            self._data = []
            for name, value in inspect.getmembers(self):
                if not name.startswith("_") and not inspect.isfunction(value):
                    if isinstance(value, tuple) and len(value) > 1:
                        data = value
                    else:
                        data = (value, " ".join([x.capitalize() for x in name.split("_")]),)
                    self._data.append(data)
                    setattr(self, name, data[0])

        def __iter__(self):
            for value, data in self._data:
                yield value, data
