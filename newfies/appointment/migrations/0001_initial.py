# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import appointment.models.events
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mod_mailer', '0001_initial'),
        ('survey', '0001_initial'),
        ('mod_sms', '0001_initial'),
        ('dialer_cdr', '0001_initial'),
        ('auth', '0002_calendaruser_manager_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alarm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alarm_phonenumber', models.CharField(max_length=50, null=True, verbose_name='notify to phone number', blank=True)),
                ('alarm_email', models.EmailField(max_length=75, null=True, verbose_name='notify to email', blank=True)),
                ('daily_start', models.TimeField(default=b'00:00:00', verbose_name='daily start')),
                ('daily_stop', models.TimeField(default=b'23:59:59', verbose_name='daily stop')),
                ('advance_notice', models.IntegerField(default=0, help_text='Seconds to start processing an alarm before the alarm date/time', verbose_name='advance notice')),
                ('maxretry', models.IntegerField(default=0, help_text='number of retries', verbose_name='max retry')),
                ('retry_delay', models.IntegerField(default=0, help_text='Seconds to wait between retries', verbose_name='retry delay')),
                ('num_attempt', models.IntegerField(default=0, verbose_name='number of attempts')),
                ('method', models.IntegerField(default=1, verbose_name='method', choices=[(1, 'CALL'), (3, 'EMAIL'), (2, 'SMS')])),
                ('date_start_notice', models.DateTimeField(default=django.utils.timezone.now, verbose_name='alarm date')),
                ('status', models.IntegerField(default=1, verbose_name='status', choices=[(3, 'FAILURE'), (2, 'IN_PROCESS'), (1, 'PENDING'), (4, 'RETRY'), (5, 'SUCCESS')])),
                ('result', models.IntegerField(default=0, null=True, verbose_name='result', blank=True, choices=[(2, 'CANCELLED'), (1, 'CONFIRMED'), (0, 'NO RESULT'), (3, 'RESCHEDULED')])),
                ('url_cancel', models.CharField(max_length=250, null=True, verbose_name='URL cancel', blank=True)),
                ('url_confirm', models.CharField(max_length=250, null=True, verbose_name='URL confirm', blank=True)),
                ('phonenumber_transfer', models.CharField(max_length=50, null=True, verbose_name='phone number transfer', blank=True)),
                ('phonenumber_sms_failure', models.CharField(max_length=50, null=True, verbose_name='phone number SMS failure', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
            ],
            options={
                'verbose_name': 'alarm',
                'verbose_name_plural': 'alarms',
                'permissions': (('view_alarm', 'can see Alarm list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlarmRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(help_text='date when the alarm will be scheduled', verbose_name='date')),
                ('status', models.IntegerField(default=1, null=True, verbose_name='status', blank=True, choices=[(3, 'FAILURE'), (2, 'IN PROCESS'), (1, 'PENDING'), (4, 'RETRY'), (5, 'SUCCESS')])),
                ('callstatus', models.IntegerField(default=0, null=True, blank=True)),
                ('duration', models.IntegerField(default=0, null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('alarm', models.ForeignKey(related_name='request_alarm', blank=True, to='appointment.Alarm', help_text='select alarm', null=True, verbose_name='alarm')),
                ('callrequest', models.ForeignKey(related_name='callrequest_alarm', blank=True, to='dialer_cdr.Callrequest', help_text='select call request', null=True, verbose_name='Call Request')),
            ],
            options={
                'verbose_name': 'alarm request',
                'verbose_name_plural': 'alarm requests',
                'permissions': (('view_alarm_request', 'can see Alarm request list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('max_concurrent', models.IntegerField(default=0, help_text='Max concurrent is not implemented', null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('user', models.ForeignKey(related_name='calendar user', blank=True, to='auth.CalendarUser', help_text='select user', null=True, verbose_name='calendar user')),
            ],
            options={
                'verbose_name': 'calendar',
                'verbose_name_plural': 'calendars',
                'permissions': (('view_calendar', 'Can see Calendar list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='label')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='start')),
                ('end', models.DateTimeField(default=appointment.models.events.set_end, help_text='Must be later than the start', verbose_name='end')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('end_recurring_period', models.DateTimeField(default=appointment.models.events.set_end_recurring_period, help_text='Used if the event recurs', null=True, verbose_name='end recurring period', blank=True)),
                ('notify_count', models.IntegerField(default=0, null=True, verbose_name='notify count', blank=True)),
                ('status', models.IntegerField(default=1, null=True, verbose_name='status', blank=True, choices=[(2, 'COMPLETED'), (3, 'PAUSED'), (1, 'PENDING')])),
                ('data', jsonfield.fields.JSONField(help_text='data in JSON format, e.g. {"cost": "40 euro"}', null=True, verbose_name='additional data (JSON)', blank=True)),
                ('occ_count', models.IntegerField(default=0, null=True, verbose_name='occurrence count', blank=True)),
                ('calendar', models.ForeignKey(to='appointment.Calendar')),
                ('creator', models.ForeignKey(related_name='creator', verbose_name='calendar user', to='auth.CalendarUser')),
                ('parent_event', models.ForeignKey(related_name='parent event', blank=True, to='appointment.Event', null=True)),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
                'permissions': (('view_event', 'can see Event list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, null=True, verbose_name='title', blank=True)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('start', models.DateTimeField(verbose_name='start')),
                ('end', models.DateTimeField(verbose_name='end')),
                ('cancelled', models.BooleanField(default=False, verbose_name='cancelled')),
                ('original_start', models.DateTimeField(verbose_name='original start')),
                ('original_end', models.DateTimeField(verbose_name='original end')),
                ('event', models.ForeignKey(verbose_name='event', to='appointment.Event')),
            ],
            options={
                'verbose_name': 'occurrence',
                'verbose_name_plural': 'occurrences',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('frequency', models.CharField(max_length=10, verbose_name='frequency', choices=[(b'YEARLY', 'Yearly'), (b'MONTHLY', 'Monthly'), (b'WEEKLY', 'Weekly'), (b'DAILY', 'Daily'), (b'HOURLY', 'Hourly'), (b'MINUTELY', 'Minutely'), (b'SECONDLY', 'Secondly')])),
                ('params', models.TextField(help_text='example : count:1;bysecond:3;', null=True, verbose_name='params', blank=True)),
            ],
            options={
                'verbose_name': 'rule',
                'verbose_name_plural': 'rules',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='rule',
            field=models.ForeignKey(blank=True, to='appointment.Rule', help_text='Recuring rules', null=True, verbose_name='rule'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='event',
            field=models.ForeignKey(related_name='event', verbose_name='related to event', to='appointment.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='mail_template',
            field=models.ForeignKey(related_name='mail template', verbose_name='mail', blank=True, to='mod_mailer.MailTemplate', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='sms_template',
            field=models.ForeignKey(related_name='sms template', verbose_name='SMS', blank=True, to='mod_sms.SMSTemplate', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='survey',
            field=models.ForeignKey(related_name='survey', verbose_name='survey', blank=True, to='survey.Survey', null=True),
            preserve_default=True,
        ),
    ]
