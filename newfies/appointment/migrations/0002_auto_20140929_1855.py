# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('mod_sms', '0001_initial'),
        ('survey', '0001_initial'),
        ('audiofield', '__first__'),
        ('dialer_cdr', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mod_mailer', '0001_initial'),
        ('appointment', '0001_initial'),
        ('auth', '0002_calendaruser_manager_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendarsetting',
            name='survey',
            field=models.ForeignKey(related_name=b'calendar_survey', verbose_name='sealed survey', to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calendarsetting',
            name='user',
            field=models.ForeignKey(related_name=b'manager_user', verbose_name='manager', to=settings.AUTH_USER_MODEL, help_text='select manager'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calendarsetting',
            name='voicemail_audiofile',
            field=models.ForeignKey(verbose_name='voicemail audio file', blank=True, to='audiofield.AudioFile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='calendar',
            name='user',
            field=models.ForeignKey(related_name=b'calendar user', blank=True, to='auth.CalendarUser', help_text='select user', null=True, verbose_name='calendar user'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarmrequest',
            name='alarm',
            field=models.ForeignKey(related_name=b'request_alarm', blank=True, to='appointment.Alarm', help_text='select alarm', null=True, verbose_name='alarm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarmrequest',
            name='callrequest',
            field=models.ForeignKey(related_name=b'callrequest_alarm', blank=True, to='dialer_cdr.Callrequest', help_text='select call request', null=True, verbose_name='Call Request'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='event',
            field=models.ForeignKey(related_name=b'event', verbose_name='related to event', to='appointment.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='mail_template',
            field=models.ForeignKey(related_name=b'mail template', verbose_name='mail', blank=True, to='mod_mailer.MailTemplate', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='sms_template',
            field=models.ForeignKey(related_name=b'sms template', verbose_name='SMS', blank=True, to='mod_sms.SMSTemplate', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='survey',
            field=models.ForeignKey(related_name=b'survey', verbose_name='survey', blank=True, to='survey.Survey', null=True),
            preserve_default=True,
        ),
    ]
