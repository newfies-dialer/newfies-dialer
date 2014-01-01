# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils import timezone
from appointment.models.rules import Rule
from appointment.models.calendars import Calendar
from appointment.models.users import CalendarUser
from appointment.utils import OccurrenceReplacer
from appointment.constants import EVENT_STATUS
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.utils.timezone import utc
import jsonfield
import pytz


class Event(models.Model):
    """
    This model stores meta data for a event
    """
    title = models.CharField(verbose_name=_("label"), max_length=255)
    description = models.TextField(verbose_name=_("description"), null=True, blank=True)
    start = models.DateTimeField(default=(lambda: datetime.utcnow().replace(tzinfo=utc)),
                                 verbose_name=_("start"))
    end = models.DateTimeField(default=(lambda: datetime.utcnow().replace(tzinfo=utc) + relativedelta(hours=+1)),
                               verbose_name=_("end"),
                               help_text=_("Must be later than the start"))
    creator = models.ForeignKey(CalendarUser, null=False, blank=False,
                                verbose_name=_("calendar user"), related_name='creator')
    created_on = models.DateTimeField(verbose_name=_("created on"), default=timezone.now)
    end_recurring_period = models.DateTimeField(verbose_name=_("end recurring period"),
                                                null=True, blank=True,
                                                default=(lambda: datetime.utcnow().replace(tzinfo=utc) + relativedelta(months=+1)),
                                                help_text=_("Used if the event recurs"))
    rule = models.ForeignKey(Rule, null=True, blank=True,
                             verbose_name=_("rule"), help_text=_("Recuring rules"))
    calendar = models.ForeignKey(Calendar, null=False, blank=False)

    notify_count = models.IntegerField(verbose_name=_("notify count"),
                                       null=True, blank=True, default=0)
    status = models.IntegerField(choices=list(EVENT_STATUS),
                                 default=EVENT_STATUS.PENDING,
                                 verbose_name=_("status"), blank=True, null=True)
    data = jsonfield.JSONField(null=True, blank=True, verbose_name=_('additional data (JSON)'),
                               help_text=_("data in JSON format, e.g. {\"cost\": \"40 euro\"}"))
    # Keep a trace of the original event of all occurences
    parent_event = models.ForeignKey('self', null=True, blank=True, related_name="parent event")
    # Occurence count, this is an increment that will add 1 on the new event created
    # This helps to know that an event is the nth created
    occ_count = models.IntegerField(null=True, blank=True, default=0,
                                    verbose_name=_("occurrence count"))

    class Meta:
        permissions = (
            ("view_event", _('can see Event list')),
        )
        verbose_name = _('event')
        verbose_name_plural = _('events')
        app_label = "appointment"

    def __unicode__(self):
        date_format = u'%s' % ugettext("DATE_FORMAT")
        return '%(title)s: %(start)s' % {
            'title': self.title,
            'start': date(self.start, date_format),
        }

    def get_absolute_url(self):
        return reverse('event', args=[self.id])

    def get_occurrences(self, start, end):
        """
        >>> rule = Rule(frequency="MONTHLY", name="Monthly")
        >>> rule.save()
        >>> event = Event(rule=rule, start=datetime.datetime(2008,1,1,tzinfo=pytz.utc), end=datetime.datetime(2008,1,2))
        >>> event.rule
        <Rule: Monthly>
        >>> occurrences = event.get_occurrences(datetime.datetime(2008,1,24), datetime.datetime(2008,3,2))
        >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
        ['2008-02-01 00:00:00+00:00 to 2008-02-02 00:00:00+00:00', '2008-03-01 00:00:00+00:00 to 2008-03-02 00:00:00+00:00']

        Ensure that if an event has no rule, that it appears only once.

        >>> event = Event(start=datetime.datetime(2008,1,1,8,0), end=datetime.datetime(2008,1,1,9,0))
        >>> occurrences = event.get_occurrences(datetime.datetime(2013,1,24), datetime.datetime(2014,3,2))
        >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
        []
        """
        persisted_occurrences = self.occurrence_set.all()
        occ_replacer = OccurrenceReplacer(persisted_occurrences)
        occurrences = self._get_occurrence_list(start, end)
        final_occurrences = []
        for occ in occurrences:
            # replace occurrences with their persisted counterparts
            if occ_replacer.has_occurrence(occ):
                p_occ = occ_replacer.get_occurrence(occ)
                # ...but only if they are within this period
                if p_occ.start < end and p_occ.end >= start:
                    final_occurrences.append(p_occ)
            else:
                final_occurrences.append(occ)
        # then add persisted occurrences which originated outside of this period but now
        # fall within it
        final_occurrences += occ_replacer.get_additional_occurrences(start, end)
        return final_occurrences

    def get_next_occurrence(self):
        """
        TODO: implement this

        >>> rule = Rule(frequency="MONTHLY", name="Monthly")
        >>> rule.save()
        >>> event = Event(rule=rule, start=datetime.datetime(2008,1,1,tzinfo=pytz.utc), end=datetime.datetime(2008,1,2))
        >>> event.rule
        <Rule: Monthly>
        >>> event.get_next_occurrence()
        2008-02-02 00:00:00+00:00
        """
        start = datetime.utcnow().replace(tzinfo=utc)
        for occ in self.get_rrule_object():
            if occ.replace(tzinfo=None) > start:
                return occ  # return the next occurent

    def copy_event(self, next_occurrence):
        """create new event with next occurrence"""

        if self.parent_event:
            parent_event = self.parent_event
        else:
            parent_event = self

        #find the new event end
        event_end = next_occurrence + (self.end - self.start)

        new_event = Event.objects.create(
            start=next_occurrence,
            end=event_end,
            title=self.title,
            description=self.description,
            creator=self.creator,
            rule=self.rule,
            end_recurring_period=self.end_recurring_period,
            calendar=self.calendar,
            notify_count=self.notify_count,
            data=self.data,
            # implemented parent_event & occ_count
            parent_event=parent_event,
            occ_count=self.occ_count + 1,
        )

        return new_event

    def update_last_child_status(self, status):
        """we will search for the last created child of an event and update his status
        to the status value

        Note for the integrators: We can pause an event for 12hours but after that we will have to
        stop and create the new event.
        """
        obj_events = Event.objects.filter(parent_event=self).order_by('-created_on')
        if obj_events:
            obj_events[0].status = status
            obj_events[0].save()

    def get_list_child(self):
        """we will list childs of an event"""
        obj_events = Event.objects.filter(parent_event=self).order_by('created_on')
        return obj_events

    def get_rrule_object(self):
        if self.rule is not None:
            params = self.rule.get_params()
            frequency = 'rrule.%s' % self.rule.frequency
            return rrule.rrule(eval(frequency), dtstart=self.start, **params)
        else:
            return []

    def _create_occurrence(self, start, end=None):
        if end is None:
            end = start + (self.end - self.start)
        return Occurrence(event=self, start=start, end=end, original_start=start, original_end=end)

    def get_occurrence(self, date):
        if timezone.is_naive(date):
            date = timezone.make_aware(date, timezone.utc)
        rule = self.get_rrule_object()
        if rule:
            next_occurrence = rule.after(date, inc=True)
        else:
            next_occurrence = self.start
        if next_occurrence == date:
            try:
                return Occurrence.objects.get(event=self, original_start=date)
            except Occurrence.DoesNotExist:
                return self._create_occurrence(next_occurrence)

    def _get_occurrence_list(self, start, end):
        """
        returns a list of occurrences for this event from start to end.
        """
        difference = (self.end - self.start)
        if self.rule is not None:
            occurrences = []
            if self.end_recurring_period and self.end_recurring_period < end:
                end = self.end_recurring_period
            rule = self.get_rrule_object()
            o_starts = rule.between(start - difference, end - difference, inc=True)
            for o_start in o_starts:
                o_end = o_start + difference
                occurrences.append(self._create_occurrence(o_start, o_end))
            return occurrences
        else:
            # check if event is in the period
            if self.start < end and self.end > start:
                return [self._create_occurrence(self.start)]
            else:
                return []

    def _occurrences_after_generator(self, after=None, tzinfo=pytz.utc):
        """
        returns a generator that produces unpresisted occurrences after the
        datetime ``after``.
        """

        if after is None:
            after = timezone.now()
        rule = self.get_rrule_object()
        if rule is None:
            if self.end > after:
                yield self._create_occurrence(self.start, self.end)
            raise StopIteration
        date_iter = iter(rule)
        difference = self.end - self.start
        while True:
            o_start = date_iter.next()
            if o_start > self.end_recurring_period:
                raise StopIteration
            o_end = o_start + difference
            if o_end > after:
                yield self._create_occurrence(o_start, o_end)

    def occurrences_after(self, after=None):
        """
        returns a generator that produces occurrences after the datetime
        ``after``.  Includes all of the persisted Occurrences.
        """
        occ_replacer = OccurrenceReplacer(self.occurrence_set.all())
        generator = self._occurrences_after_generator(after)
        while True:
            next = generator.next()
            yield occ_replacer.get_occurrence(next)


class Occurrence(models.Model):
    event = models.ForeignKey(Event, verbose_name=_("event"))
    title = models.CharField(_("title"), max_length=255, blank=True, null=True)
    description = models.TextField(_("description"), blank=True, null=True)
    start = models.DateTimeField(_("start"))
    end = models.DateTimeField(_("end"))
    cancelled = models.BooleanField(_("cancelled"), default=False)
    original_start = models.DateTimeField(_("original start"))
    original_end = models.DateTimeField(_("original end"))

    class Meta:
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")
        app_label = "appointment"

    def __init__(self, *args, **kwargs):
        super(Occurrence, self).__init__(*args, **kwargs)
        #if self.title is None:
        #    self.title = self.event.title
        #if self.description is None:
        #    self.description = self.event.description

    def moved(self):
        return self.original_start != self.start or self.original_end != self.end
    moved = property(moved)

    def move(self, new_start, new_end):
        self.start = new_start
        self.end = new_end
        self.save()

    def cancel(self):
        self.cancelled = True
        self.save()

    def uncancel(self):
        self.cancelled = False
        self.save()

    def get_absolute_url(self):
        if self.pk is not None:
            return reverse('occurrence', kwargs={'occurrence_id': self.pk,
                'event_id': self.event.id})
        return reverse('occurrence_by_date', kwargs={
            'event_id': self.event.id,
            'year': self.start.year,
            'month': self.start.month,
            'day': self.start.day,
            'hour': self.start.hour,
            'minute': self.start.minute,
            'second': self.start.second,
        })

    def get_cancel_url(self):
        if self.pk is not None:
            return reverse('cancel_occurrence', kwargs={'occurrence_id': self.pk,
                'event_id': self.event.id})
        return reverse('cancel_occurrence_by_date', kwargs={
            'event_id': self.event.id,
            'year': self.start.year,
            'month': self.start.month,
            'day': self.start.day,
            'hour': self.start.hour,
            'minute': self.start.minute,
            'second': self.start.second,
        })

    def get_edit_url(self):
        if self.pk is not None:
            return reverse('edit_occurrence', kwargs={'occurrence_id': self.pk,
                'event_id': self.event.id})
        return reverse('edit_occurrence_by_date', kwargs={
            'event_id': self.event.id,
            'year': self.start.year,
            'month': self.start.month,
            'day': self.start.day,
            'hour': self.start.hour,
            'minute': self.start.minute,
            'second': self.start.second,
        })

    def __unicode__(self):
        return ugettext("%(start)s to %(end)s") % {
            'start': self.start,
            'end': self.end,
        }

    def __cmp__(self, other):
        rank = cmp(self.start, other.start)
        if rank == 0:
            return cmp(self.end, other.end)
        return rank

    def __eq__(self, other):
        return self.original_start == other.original_start and self.original_end == other.original_end
