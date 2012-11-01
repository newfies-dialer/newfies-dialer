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

"""This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools_stats.modules import DashboardCharts, get_active_graph
from admin_tools.utils import get_admin_site_name


class HistoryDashboardModule(modules.LinkList):
    title = 'History'

    def init_with_context(self, context):
        request = context['request']
        # we use sessions to store the visited pages stack
        history = request.session.get('history', [])
        for item in history:
            self.children.append(item)
        # add the current page to the history
        history.insert(0, {
            'title': context['title'],
            'url': request.META['PATH_INFO'],
        })
        if len(history) > 10:
            history = history[:10]
        request.session['history'] = history


class CustomIndexDashboard(Dashboard):
    """Custom index dashboard"""

    def init_with_context(self, context):

        request = context['request']

        # we want a 3 columns layout
        self.columns = 3

        self.children.append(modules.Group(
            title="General",
            display="tabs",
            children=[
                modules.AppList(
                    title='User',
                    models=('django.contrib.*', 'user_profile.*', ),
                ),
                modules.AppList(
                    _('Task Manager'),
                    models=('djcelery.*', ),
                ),
                modules.AppList(
                    _('Dashboard Stats'),
                    models=('admin_tools_stats.*', ),
                ),
                modules.RecentActions(_('Recent Actions'), 5),
            ]
        ))

        self.children.append(modules.AppList(
            _('Settings'),
            models=('dialer_settings.*', ),
        ))

        # append an app list module for "Dialer"
        self.children.append(modules.AppList(
            _('Voip Dialer'),
            models=('dialer_cdr.*', 'dialer_gateway.*',
                    'dialer_contact.*', 'dialer_campaign.*', ),
        ))

        # append an app list module for "Dialer"
        self.children.append(modules.AppList(
            _('Voice Applications'),
            models=('voice_app.*', 'survey.*', ),
        ))

        # append an app list module for "Dialer"
        self.children.append(modules.AppList(
            _('Audio Files'),
            models=('audiofield.*', ),
        ))

        # append a link list module for "quick links"
        """
        site_name = get_admin_site_name(context)

        #Quick link seems to broke the admin design if too many element
        self.children.append(modules.LinkList(
            _('Quick links'),
            layout='inline',
            draggable=True,
            deletable=True,
            collapsible=True,
            children=[
                [_('Go to Newfies-Dialer'), 'http://www.newfies-dialer.org/'],
                [_('Change password'),
                 reverse('%s:password_change' % site_name)],
                [_('Log out'), reverse('%s:logout' % site_name)],
            ],
        ))
        """

        if not settings.DEBUG:
            # append a feed module
            self.children.append(modules.Feed(
                _('Latest Newfies-Dialer News'),
                feed_url='http://www.newfies-dialer.org/category/blog/feed/',
                limit=5
            ))

        # append an app list module for "Country_prefix"
        self.children.append(modules.AppList(
            _('Dashboard Stats Settings'),
            models=('admin_dashboard_stats.*', ),
        ))

        # Copy following code into your custom dashboard
        graph_list = get_active_graph()
        for i in graph_list:
            kwargs = {}
            kwargs['chart_size'] = "360x100"
            kwargs['graph_key'] = i.graph_key
            if request.POST.get('select_box_' + i.graph_key):
                kwargs['select_box_' + i.graph_key] = request.POST['select_box_' + i.graph_key]

            self.children.append(DashboardCharts(**kwargs))


class CustomAppIndexDashboard(AppIndexDashboard):
    """Custom app index dashboard for admin."""

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5,
            ),
        ]

    def init_with_context(self, context):
        """Use this method if you need to access the request context."""
        return super(CustomAppIndexDashboard, self).init_with_context(context)
