#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2015 Star2Billing S.L.
#
# The primary maintainer of this project is
# Arezqui Belaid <info@star2billing.com>
#

from django.utils.translation import ugettext as _


def tpl_control_icon(icon):
    """
    function to produce control html icon
    """
    return '<i class="fa %s icon-small"></i>' % (icon)


def get_common_campaign_status_url(id, status, status_link, STATUS_OF_CAMPAIGN):
    """
    Helper to display campaign status button on the grid

    example : get_common_campaign_status_url(id, status, 'update_campaign_status_cust/', CAMPAIGN_STATUS)

              get_common_campaign_status_url(id, status, 'update_sms_campaign_status_cust/', SMS_CAMPAIGN_STATUS)
    """
    # Store html for campaign control button
    control_play_style = tpl_control_icon('fa-play')
    control_pause_style = tpl_control_icon('fa-pause')
    control_abort_style = tpl_control_icon('fa-eject')
    control_stop_style = tpl_control_icon('fa-stop')

    # set different url for the campaign status
    url_cpg_status = status_link + '%s' % str(id)
    url_cpg_start = '%s/%s/' % (url_cpg_status, STATUS_OF_CAMPAIGN.START)
    url_cpg_pause = '%s/%s/' % (url_cpg_status, STATUS_OF_CAMPAIGN.PAUSE)
    url_cpg_abort = '%s/%s/' % (url_cpg_status, STATUS_OF_CAMPAIGN.ABORT)
    url_cpg_stop = '%s/%s/' % (url_cpg_status, STATUS_OF_CAMPAIGN.END)

    # according to the current status, disable link and change the button color
    if status == STATUS_OF_CAMPAIGN.START:
        url_cpg_start = '#'
        control_play_style = tpl_control_icon('fa-play')
    elif status == STATUS_OF_CAMPAIGN.PAUSE:
        url_cpg_pause = '#'
        control_pause_style = tpl_control_icon('fa-pause')
    elif status == STATUS_OF_CAMPAIGN.ABORT:
        url_cpg_abort = '#'
        control_abort_style = tpl_control_icon('fa-eject')
    elif status == STATUS_OF_CAMPAIGN.END:
        url_cpg_stop = '#'
        control_stop_style = tpl_control_icon('fa-stop')

    # return all the html button for campaign status management
    return "<a href='%s' title='%s'>%s</a> <a href='%s' title='%s'>%s</a> " \
        "<a href='%s' title='%s'>%s</a> <a href='%s' title='%s'>%s</a>" % \
        (url_cpg_start, _("Start"), control_play_style,
         url_cpg_pause, _("Pause"), control_pause_style,
         url_cpg_abort, _("Abort"), control_abort_style,
         url_cpg_stop, _("Stop"), control_stop_style)


def get_common_campaign_status(id, STATUS_OF_CAMPAIGN, STATUS_COLOR):
    """To get status name from CAMPAIGN_STATUS as well as SMS_CAMPAIGN_STATUS

    example : get_common_campaign_status(id, CAMPAIGN_STATUS, CAMPAIGN_STATUS_COLOR)
              get_common_campaign_status(id, SMS_CAMPAIGN_STATUS, SMS_CAMPAIGN_STATUS_COLOR)
    """
    if STATUS_OF_CAMPAIGN.START == id:
        return '<font color="%s">%s</font>' % (STATUS_COLOR[id], _("Started"))
    elif STATUS_OF_CAMPAIGN.PAUSE == id:
        return '<font color="%s">%s</font>' % (STATUS_COLOR[id], _("Paused"))
    elif STATUS_OF_CAMPAIGN.ABORT == id:
        return '<font color="%s">%s</font>' % (STATUS_COLOR[id], _("Aborted"))
    else:
        return '<font color="%s">%s</font>' % (STATUS_COLOR[id], _("Stopped"))


def get_status_value(value, STATUS_LIST):
    """common function to get status value

    example: get_status_value(1, EVENT_STATUS)
             get_status_value(3, ALARM_STATUS)
    """
    if not value:
        return ''
    STATUS = dict(STATUS_LIST)
    try:
        return STATUS[value].encode('utf-8')
    except:
        return ''
