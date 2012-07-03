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
from random import choice
import calendar
import string
import urllib
import os


def relative_days(from_day, from_year):
    """Related to date manipulation"""
    if from_day == 30:
        relative_days = 2
        return relative_days
    elif from_day == 31:
        relative_days = 1
        return relative_days
    else:
        if calendar.isleap(from_year) == 'false':
            relative_days = 2
        else:
            relative_days = 1
        return relative_days


def uniq(inlist):
    """Order preserving"""
    uniques = []
    for item in inlist:
        if item not in uniques:
            uniques.append(item)
    return uniques


def get_unique_id():
    """Generate unique id"""
    length = 8
    chars = "abcdefghijklmnopqrstuvwxyz1234567890"
    return ''.join([choice(chars) for i in range(length)])


def get_news(url):
    """Get news from an simple API
    Usage get_news('http://www.newfies-dialer.org/news')"""
    news_final = []
    try:
        news_handler = urllib.urlopen()
        news = news_handler.read()
        news = nl2br(news)
        news = string.split(news, '<br/>')

        news_array = {}
        value = {}
        for newsweb in news:
            value = string.split(newsweb, '|')
            if len(value[0]) > 1:
                news_array[value[0]] = value[1]

        info = {}
        for k in news_array:
            link = k[int(k.find("http://") - 1):len(k)]
            info = k[0:int(k.find("http://") - 1)]
            info = string.split(k, ' - ')
            news_final.append((info[0], info[1], news_array[k]))

        news_handler.close()
    except IndexError:
        pass
    except IOError:
        pass

    return news_final


def variable_value(request, field_name):
    """Variable check with request"""
    if request.method == 'GET':
        if field_name in request.GET:
            field_name = request.GET[field_name]
        else:
            field_name = ''

    if request.method == 'POST':
        if field_name in request.POST:
            field_name = request.POST[field_name]
        else:
            field_name = ''

    return field_name


def nl2br(s):
    """Related to string operation"""
    return '<br/>'.join(s.split('\n'))


def reverseString(s):
    """Reverse a string"""
    return s[::-1]


def int_convert_to_minute(value):
    """Convert int to minutes:seconds format"""
    min = int(int(value) / 60)
    sec = int(int(value) % 60)
    return "%02d" % min + ":" + "%02d" % sec


def isint(str):
    """Return True if the string is an integer"""
    if not str:
        return False
    try:
        num = int(str)
    except:
        return False

    return True


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
    mstring = needledtag1=143432,needledtag2=143432
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
