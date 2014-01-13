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

from django.conf import settings
from django import db
import os


def debug_query(number):
    """
    Function to debug the SQL queries
    """
    if settings.DIALERDEBUG and number >= 20:
        print("%d) " % number)
        print("QUERY #) %d" % len(db.connection.queries))
        print(db.connection.queries)
    if settings.DIALERDEBUG:
        db.reset_queries()


def check_celeryd_process():
    """Check celeryd service running or not"""
    process = os.popen("ps x | grep celeryd").read().splitlines()
    if len(process) > 2:
        return True
    else:
        return False


def search_tag_string(mstring, tag):
    """
    Search in string tag with their value

    >>> mstring = 'needledtag1=143432,needledtag2=143432'

    >>> search_tag_string(mstring, 'needledtag1')
    '143432'
    """
    if not mstring or len(mstring) < 2:
        return False
    sval = {}
    try:
        sval = dict(e.split('=') for e in mstring.split(','))
    except ValueError:
        return False
    if tag in sval:
        return sval[tag]
    else:
        return False
