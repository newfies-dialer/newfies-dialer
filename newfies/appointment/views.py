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

# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.template.context import RequestContext
from appointment.models.calendars import Calendar
from appointment.models.events import Event
from appointment.models.alarms import Alarm
from appointment.constants import CALENDAR_USER_COLUMN_NAME, CALENDAR_COLUMN_NAME, \
    EVENT_COLUMN_NAME, ALARM_COLUMN_NAME, CALENDAR_SETTING_COLUMN_NAME
from appointment.forms import CalendarUserChangeDetailExtendForm, \
    CalendarUserNameChangeForm, CalendarForm, EventForm, AlarmForm, \
    CalendarSettingForm, EventSearchForm, CalendarUserPasswordChangeForm, \
    CalendarUserCreationForm
from user_profile.models import CalendarUserProfile, CalendarUser
from calendar_settings.models import CalendarSetting
from appointment.function_def import get_calendar_user_id_list
from user_profile.models import Manager
from django_lets_go.common_functions import ceil_strdate, getvar, \
    get_pagination_vars, unset_session_var
from datetime import datetime
from django.utils.timezone import utc


redirect_url_to_calendar_user_list = '/module/calendar_user/'
redirect_url_to_calendar_setting_list = '/module/calendar_setting/'
redirect_url_to_calendar_list = '/module/calendar/'
redirect_url_to_event_list = '/module/event/'
redirect_url_to_alarm_list = '/module/alarm/'


@permission_required('appointment.view_calendar_user', login_url='/')
@login_required
def calendar_user_list(request):
    """CalendarUser list for the logged in Manager

    **Attributes**:

        * ``template`` - appointment/calendar_user/list.html

    **Logic Description**:

        * List all calendar_user which belong to the logged in manager.
    """
    sort_col_field_list = ['user', 'updated_date']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    calendar_user_list = CalendarUserProfile.objects.filter(manager=request.user).order_by(pag_vars['sort_order'])
    data = {
        'msg': request.session.get('msg'),
        'calendar_user_list': calendar_user_list,
        'total_calendar_user': calendar_user_list.count(),
        'CALENDAR_USER_COLUMN_NAME': CALENDAR_USER_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('appointment/calendar_user/list.html', data,
                              context_instance=RequestContext(request))


@permission_required('appointment.add_calendaruserprofile', login_url='/')
@login_required
def calendar_user_add(request):
    """Add new calendar user for the logged in manager

    **Attributes**:

        * ``form`` - CalendarUserCreationForm
        * ``template`` - appointment/calendar_user/change.html

    **Logic Description**:

        * Add a new calendar user which will belong to the logged in manager
          via the UserCreationForm & get redirected to the calendar user list
    """
    form = CalendarUserCreationForm(request.user, request.POST or None)
    if form.is_valid():
        calendar_user = form.save()
        calendar_user_profile = CalendarUserProfile.objects.create(
            user=calendar_user,
            manager=Manager.objects.get(username=request.user),
            calendar_setting_id=request.POST['calendar_setting_id']
        )
        request.session["msg"] = _('"%(name)s" added as calendar user.') % {'name': request.POST['username']}
        return HttpResponseRedirect(redirect_url_to_calendar_user_list + '%s/' % str(calendar_user_profile.id))

    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('appointment/calendar_user/change.html', data, context_instance=RequestContext(request))


@permission_required('appointment.delete_calendaruserprofile', login_url='/')
@login_required
def calendar_user_del(request, object_id):
    """Delete a calendar_user for a logged in manager

    **Attributes**:

        * ``object_id`` - Selected calendar_user object
        * ``object_list`` - Selected calendar_user objects

    **Logic Description**:

        * Delete calendar_user from a calendar_user list.
    """
    if int(object_id) != 0:
        # When object_id is not 0
        # 1) delete calendar_user profile & calendar_user
        calendar_user_profile = get_object_or_404(CalendarUserProfile, pk=object_id, manager_id=request.user.id)
        calendar_user = CalendarUser.objects.get(pk=calendar_user_profile.user_id)

        request.session["msg"] = _('"%(name)s" is deleted.') % {'name': calendar_user}
        calendar_user.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])
        try:
            # 1) delete all calendar users belonging to a managers
            calendar_user_list = CalendarUserProfile.objects\
                .filter(manager_id=request.user.id).extra(where=['id IN (%s)' % values])

            if calendar_user_list:
                user_list = calendar_user_list.values_list('user_id', flat=True)
                calendar_users = CalendarUser.objects.filter(pk__in=user_list)
                request.session["msg"] = _('%(count)s calendar user(s) are deleted.') % \
                    {'count': calendar_user_list.count()}
                calendar_users.delete()
        except:
            raise Http404

    return HttpResponseRedirect(redirect_url_to_calendar_user_list)


@permission_required('appointment.change_calendaruserprofile', login_url='/')
@login_required
def calendar_user_change(request, object_id):
    """Update/Delete calendar user for the logged in manager

    **Attributes**:

        * ``object_id`` - Selected calendar_user object
        * ``form`` - CalendarUserChangeDetailExtendForm, CalendarUserNameChangeForm
        * ``template`` - appointment/calendar_user/change.html

    **Logic Description**:

        * Update/delete selected calendar user from the calendar_user list
          via CalendarUserChangeDetailExtendForm & get redirected to calendar_user list
    """
    calendar_user_profile = get_object_or_404(CalendarUserProfile, pk=object_id, manager_id=request.user.id)
    calendar_user_userdetail = get_object_or_404(CalendarUser, pk=calendar_user_profile.user_id)

    calendar_user_profile_form = CalendarUserChangeDetailExtendForm(
        request.user, request.POST or None, instance=calendar_user_profile)
    calendar_user_username_form = CalendarUserNameChangeForm(
        request.POST or None,
        initial={'username': calendar_user_userdetail.username,
                 'password': calendar_user_userdetail.password},
        instance=calendar_user_userdetail)

    if calendar_user_username_form.is_valid():
        if request.POST.get('delete'):
            calendar_user_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_calendar_user_list)
        else:
            # Save calendar_user username
            calendar_user_username_form.save()

            if calendar_user_profile_form.is_valid():
                calendar_user_profile_form.save()
                request.session["msg"] = _('"%(name)s" is updated.') % {'name': calendar_user_profile.user}
                return HttpResponseRedirect(redirect_url_to_calendar_user_list)
    data = {
        'calendar_user_profile_form': calendar_user_profile_form,
        'calendar_user_username_form': calendar_user_username_form,
        'action': 'update',
    }
    return render_to_response('appointment/calendar_user/change.html', data, context_instance=RequestContext(request))


@login_required
def calendar_user_change_pw(request, object_id):
    """
    CalendarUser Detail change

    **Attributes**:

        * ``form`` - CalendarUserPasswordChangeForm
        * ``template`` - 'appointment/calendar_user/change_password.html',
             'frontend/registration/user_detail_change.html'

    **Logic Description**:

        * Reset calendar_user password.
    """
    calendar_user_userdetail = get_object_or_404(CalendarUser, pk=object_id)
    calendar_user_username = calendar_user_userdetail.username

    user_password_form = CalendarUserPasswordChangeForm(calendar_user_userdetail, request.POST or None)
    if user_password_form.is_valid():
        user_password_form.save()
        request.session["msg"] = _('%s password has been changed.' % calendar_user_username)
        return HttpResponseRedirect(redirect_url_to_calendar_user_list)

    data = {
        'calendar_user_username': calendar_user_username,
        'user_password_form': user_password_form,
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('appointment/calendar_user/change_password.html',
                              data, context_instance=RequestContext(request))


@permission_required('appointment.view_calendar', login_url='/')
@login_required
def calendar_list(request):
    """Calendar list for the logged in user

    **Attributes**:

        * ``template`` - appointment/calendar/list.html

    **Logic Description**:

        * List all calendars which belong to the logged in user.
    """
    sort_col_field_list = ['id', 'name', 'user', 'max_concurrent', 'created_date']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    calendar_user_id_list = get_calendar_user_id_list(request.user)
    calendar_list = Calendar.objects.filter(user_id__in=calendar_user_id_list).order_by(pag_vars['sort_order'])

    data = {
        'msg': request.session.get('msg'),
        'calendar_list': calendar_list,
        'total_calendar': calendar_list.count(),
        'CALENDAR_COLUMN_NAME': CALENDAR_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('appointment/calendar/list.html', data, context_instance=RequestContext(request))


@permission_required('appointment.add_calendar', login_url='/')
@login_required
def calendar_add(request):
    """Add a new calendar for the logged in user

    **Attributes**:

        * ``form`` - CalendarForm
        * ``template`` - appointment/calendar/change.html

    **Logic Description**:

        * Add new contact belonging to the logged in user
          via ContactForm & get redirected to the contact list
    """
    form = CalendarForm(request.user, request.POST or None)
    # Add contact
    if form.is_valid():
        form.save()
        request.session["msg"] = _('"%s" is added') % request.POST['name']
        return HttpResponseRedirect(redirect_url_to_calendar_list)

    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('appointment/calendar/change.html', data, context_instance=RequestContext(request))


@permission_required('appointment.delete_calendar', login_url='/')
@login_required
def calendar_del(request, object_id):
    """Delete calendar for the logged in user

    **Attributes**:

        * ``object_id`` - Selected calendar object
        * ``object_list`` - Selected calendar objects

    **Logic Description**:

        * Delete selected calendar from the calendar list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        calendar = get_object_or_404(Calendar, pk=object_id)

        # Delete Calendar
        request.session["msg"] = _('"%s" is deleted.') % calendar.name
        calendar.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            calendar_list = Calendar.objects.extra(where=['id IN (%s)' % values])
            if calendar_list:
                request.session["msg"] = _('%s calendar(s) are deleted.') % calendar_list.count()
                calendar_list.delete()
        except:
            raise Http404
    return HttpResponseRedirect(redirect_url_to_calendar_list)


@permission_required('appointment.change_calendar', login_url='/')
@login_required
def calendar_change(request, object_id):
    """Update/Delete calendar for the logged in user

    **Attributes**:

        * ``object_id`` - Selected calendar object
        * ``form`` - CalendarForm
        * ``template`` - appointment/calendar/change.html

    **Logic Description**:

        * Update/delete selected calendar from the calendar list
          via CalendarForm & get redirected to the calendar list
    """
    calendar = get_object_or_404(Calendar, pk=object_id)
    form = CalendarForm(request.user, request.POST or None, instance=calendar)
    if form.is_valid():
        # Delete calendar
        if request.POST.get('delete'):
            calendar_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_calendar_list)
        else:
            # Update calendar
            form.save()
            request.session["msg"] = _('"%s" is updated.') % request.POST['name']
            return HttpResponseRedirect(redirect_url_to_calendar_list)

    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response('appointment/calendar/change.html', data, context_instance=RequestContext(request))


@permission_required('appointment.view_calendarsetting', login_url='/')
@login_required
def calendar_setting_list(request):
    """Calendar setting list for the logged in user

    **Attributes**:

        * ``template`` - appointment/calendar_setting/list.html

    **Logic Description**:

        * List all calendar settings which belong to the logged in user.
    """
    sort_col_field_list = ['id', 'label', 'callerid', 'caller_name', 'call_timeout',
                           'survey', 'aleg_gateway', 'sms_gateway']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    calendar_setting_list = CalendarSetting.objects.filter(user=request.user).order_by(pag_vars['sort_order'])
    data = {
        'msg': request.session.get('msg'),
        'calendar_setting_list': calendar_setting_list,
        'total_calendar_setting': calendar_setting_list.count(),
        'CALENDAR_SETTING_COLUMN_NAME': CALENDAR_SETTING_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('appointment/calendar_setting/list.html', data, context_instance=RequestContext(request))


@permission_required('appointment.add_calendarsetting', login_url='/')
@login_required
def calendar_setting_add(request):
    """Add a new calendar setting for the logged in user

    **Attributes**:

        * ``form`` - CalendarSettingForm
        * ``template`` - appointment/calendar_setting/change.html

    **Logic Description**:

        * Add new calendar_setting belonging to the logged in user
          via ContactSettingForm & get redirected to the calendar_setting list
    """
    form = CalendarSettingForm(request.user, request.POST or None)
    # Add calendar_setting
    if form.is_valid():
        obj = form.save(user=request.user)
        request.session["msg"] = _('"%s" is added') % obj
        return HttpResponseRedirect(redirect_url_to_calendar_setting_list)
    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('appointment/calendar_setting/change.html',
                              data, context_instance=RequestContext(request))


@permission_required('appointment.delete_calendarsetting', login_url='/')
@login_required
def calendar_setting_del(request, object_id):
    """Delete calendar_setting for the logged in user

    **Attributes**:

        * ``object_id`` - Selected calendar_setting object
        * ``object_list`` - Selected calendar_setting objects

    **Logic Description**:

        * Delete selected calendar_setting from the calendar_setting list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        calendar_setting = get_object_or_404(CalendarSetting, pk=object_id)

        # Delete calendar_setting
        request.session["msg"] = _('"%s" is deleted.') % calendar_setting
        calendar_setting.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            calendar_setting = CalendarSetting.objects.extra(where=['id IN (%s)' % values])
            if calendar_setting:
                request.session["msg"] = _('%s calendar setting(s) are deleted.') % calendar_setting.count()
                calendar_setting.delete()
        except:
            raise Http404
    return HttpResponseRedirect(redirect_url_to_calendar_setting_list)


@permission_required('appointment.change_calendarsetting', login_url='/')
@login_required
def calendar_setting_change(request, object_id):
    """Update/Delete calendar_setting for the logged in user

    **Attributes**:

        * ``object_id`` - Selected calendar_setting object
        * ``form`` - CalendarSettingForm
        * ``template`` - appointment/calendar_setting/change.html

    **Logic Description**:

        * Update/delete selected calendar_setting from the calendar_setting list
          via CalendarSettingForm & get redirected to the calendar_setting list
    """
    calendar_setting = get_object_or_404(CalendarSetting, pk=object_id)

    form = CalendarSettingForm(request.user, request.POST or None, instance=calendar_setting)
    if form.is_valid():
        # Delete calendar_setting
        if request.POST.get('delete'):
            calendar_setting_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_calendar_setting_list)
        else:
            obj = form.save()
            request.session["msg"] = _('"%s" is updated.') % obj
            return HttpResponseRedirect(redirect_url_to_calendar_setting_list)

    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response('appointment/calendar_setting/change.html',
                              data, context_instance=RequestContext(request))


@permission_required('appointment.view_event', login_url='/')
@login_required
def event_list(request):
    """Event list for the logged in user

    **Attributes**:

        * ``template`` - appointment/event/list.html

    **Logic Description**:

        * List all events which belong to the logged in user.
    """
    today = datetime.utcnow().replace(tzinfo=utc)
    form = EventSearchForm(request.user, request.POST or None, initial={'start': today.strftime('%Y-%m-%d %H:%M')})
    sort_col_field_list = ['id', 'start', 'end', 'title', 'calendar', 'status', 'created_on']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')

    start_date = ''
    calendar_id = ''
    calendar_user_id = ''
    post_var_with_page = 0
    if form.is_valid():
        field_list = ['start_date', 'calendar_id', 'calendar_user_id']
        unset_session_var(request, field_list)

        start_date = getvar(request, 'start_date')
        start_date = ceil_strdate(str(start_date), 'start')
        converted_start_date = start_date.strftime('%Y-%m-%d')
        request.session['session_start_date'] = converted_start_date

        calendar_id = getvar(request, 'calendar_id', setsession=True)
        calendar_user_id = getvar(request, 'calendar_user_id', setsession=True)
        post_var_with_page = 1

    if request.GET.get('page') or request.GET.get('sort_by'):
        post_var_with_page = 1
        start_date = request.session.get('session_start_date')
        start_date = ceil_strdate(start_date, 'start')
        calendar_id = request.session.get('session_calendar_id')
        calendar_user_id = request.session.get('session_calendar_user_id')
        form = EventSearchForm(request.user, initial={'start_date': start_date.strftime('%Y-%m-%d %H:%M'),
                                                      'calendar_id': calendar_id,
                                                      'calendar_user_id': calendar_user_id,
                                                      })

    if post_var_with_page == 0:
        # default unset session var
        field_list = ['start_date', 'calendar_id', 'calendar_user_id']
        unset_session_var(request, field_list)

    kwargs = {}
    calendar_user_id_list = get_calendar_user_id_list(request.user)
    kwargs['calendar__user_id__in'] = calendar_user_id_list
    if start_date:
        kwargs['start__gte'] = start_date

    if calendar_id and int(calendar_id) != 0:
        kwargs['calendar_id'] = calendar_id

    if calendar_user_id and int(calendar_user_id) != 0:
        kwargs['creator_id'] = calendar_user_id

    all_event_list = Event.objects.filter(**kwargs).order_by(pag_vars['sort_order'])
    event_list = all_event_list[pag_vars['start_page']:pag_vars['end_page']]
    data = {
        'form': form,
        'msg': request.session.get('msg'),
        'all_event_list': all_event_list,
        'event_list': event_list,
        'total_event': all_event_list.count(),
        'EVENT_COLUMN_NAME': EVENT_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('appointment/event/list.html', data, context_instance=RequestContext(request))


@permission_required('appointment.add_event', login_url='/')
@login_required
def event_add(request):
    """Add a new event for the logged in user

    **Attributes**:

        * ``form`` - EventForm
        * ``template`` - appointment/event/change.html

    **Logic Description**:

        * Add new event belonging to the logged in user
          via EventForm & get redirected to the event list
    """
    form = EventForm(request.user, request.POST or None)
    # Add event
    if form.is_valid():
        form.save()
        request.session["msg"] = _('"%s" is added') % request.POST['title']
        return HttpResponseRedirect(redirect_url_to_event_list)
    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('appointment/event/change.html', data, context_instance=RequestContext(request))


@permission_required('appointment.delete_event', login_url='/')
@login_required
def event_del(request, object_id):
    """Delete event for the logged in user

    **Attributes**:

        * ``object_id`` - Selected event object
        * ``object_list`` - Selected event objects

    **Logic Description**:

        * Delete selected event from the event list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        event = get_object_or_404(Event, pk=object_id)

        # Delete Event
        request.session["msg"] = _('"%s" is deleted.') % event.title
        event.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            event_list = Event.objects.extra(where=['id IN (%s)' % values])
            if event_list:
                request.session["msg"] = _('%s event(s) are deleted.') % event_list.count()
                event_list.delete()
        except:
            raise Http404
    return HttpResponseRedirect(redirect_url_to_event_list)


@permission_required('appointment.change_event', login_url='/')
@login_required
def event_change(request, object_id):
    """Update/Delete event for the logged in user

    **Attributes**:

        * ``object_id`` - Selected event object
        * ``form`` - EventForm
        * ``template`` - appointment/event/change.html

    **Logic Description**:

        * Update/delete selected event from the event list
          via EventForm & get redirected to the event list
    """
    event = get_object_or_404(Event, pk=object_id)
    form = EventForm(request.user, request.POST or None, instance=event)
    if form.is_valid():
        # Delete event
        if request.POST.get('delete'):
            event_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_event_list)
        else:
            # Update event
            form.save()
            request.session["msg"] = _('"%s" is updated.') % request.POST['title']
            return HttpResponseRedirect(redirect_url_to_event_list)

    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response('appointment/event/change.html', data, context_instance=RequestContext(request))


@permission_required('appointment.view_alarm', login_url='/')
@login_required
def alarm_list(request):
    """Alarm list for the logged in user

    **Attributes**:

        * ``template`` - appointment/alarm/list.html

    **Logic Description**:

        * List all alarms which belong to the logged in user.
    """
    sort_col_field_list = ['id', 'alarm_phonenumber', 'alarm_email', 'daily_start',
                           'daily_stop', 'method', 'survey', 'event',
                           'date_start_notice', 'status']
    pag_vars = get_pagination_vars(request, sort_col_field_list, default_sort_field='id')
    calendar_user_id_list = get_calendar_user_id_list(request.user)
    alarm_list = Alarm.objects\
        .filter(event__calendar__user_id__in=calendar_user_id_list)\
        .order_by(pag_vars['sort_order'])
    data = {
        'msg': request.session.get('msg'),
        'alarm_list': alarm_list,
        'total_alarm': alarm_list.count(),
        'ALARM_COLUMN_NAME': ALARM_COLUMN_NAME,
        'col_name_with_order': pag_vars['col_name_with_order'],
    }
    request.session['msg'] = ''
    request.session['error_msg'] = ''
    return render_to_response('appointment/alarm/list.html', data, context_instance=RequestContext(request))


@permission_required('appointment.add_alarm', login_url='/')
@login_required
def alarm_add(request):
    """Add a new alarm for the logged in user

    **Attributes**:

        * ``form`` - AlarmForm
        * ``template`` - appointment/alarm/change.html

    **Logic Description**:

        * Add new alarm belonging to the logged in user
          via AlarmForm & get redirected to the alarm list
    """
    form = AlarmForm(request.user, request.POST or None)
    # Add alarm
    if form.is_valid():
        obj = form.save()
        request.session["msg"] = _('"%s" is added') % obj
        return HttpResponseRedirect(redirect_url_to_alarm_list)

    data = {
        'form': form,
        'action': 'add',
    }
    return render_to_response('appointment/alarm/change.html', data, context_instance=RequestContext(request))


@permission_required('appointment.delete_alarm', login_url='/')
@login_required
def alarm_del(request, object_id):
    """Delete alarm for the logged in user

    **Attributes**:

        * ``object_id`` - Selected alarm object
        * ``object_list`` - Selected alarm objects

    **Logic Description**:

        * Delete selected alarm from the alarm list
    """
    if int(object_id) != 0:
        # When object_id is not 0
        alarm = get_object_or_404(Alarm, pk=object_id)

        # Delete Event
        request.session["msg"] = _('"%s" is deleted.') % alarm.method
        alarm.delete()
    else:
        # When object_id is 0 (Multiple records delete)
        values = request.POST.getlist('select')
        values = ", ".join(["%s" % el for el in values])

        try:
            alarm_list = Alarm.objects.extra(where=['id IN (%s)' % values])
            if alarm_list:
                request.session["msg"] = _('%s alarm(s) are deleted.') % alarm_list.count()
                alarm_list.delete()
        except:
            raise Http404
    return HttpResponseRedirect(redirect_url_to_alarm_list)


@permission_required('appointment.change_alarm', login_url='/')
@login_required
def alarm_change(request, object_id):
    """Update/Delete alarm for the logged in user

    **Attributes**:

        * ``object_id`` - Selected alarm object
        * ``form`` - AlarmForm
        * ``template`` - appointment/alarm/change.html

    **Logic Description**:

        * Update/delete selected alarm from the alarm list
          via AlarmForm & get redirected to the alarm list
    """
    alarm = get_object_or_404(Alarm, pk=object_id)

    form = AlarmForm(request.user, request.POST or None, instance=alarm)
    if form.is_valid():
        # Delete alarm
        if request.POST.get('delete'):
            alarm_del(request, object_id)
            return HttpResponseRedirect(redirect_url_to_alarm_list)
        else:
            # Update alarm
            form.save()
            request.session["msg"] = _('"%s" is updated.') % alarm
            return HttpResponseRedirect(redirect_url_to_alarm_list)

    data = {
        'form': form,
        'action': 'update',
    }
    return render_to_response('appointment/alarm/change.html', data, context_instance=RequestContext(request))
