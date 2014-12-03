# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dialer_gateway', '__first__'),
        ('survey', '0001_initial'),
        ('audiofield', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=80, verbose_name='label')),
                ('callerid', models.CharField(help_text='outbound Caller ID', max_length=80, verbose_name='Caller ID Number')),
                ('caller_name', models.CharField(help_text='outbound caller-Name', max_length=80, verbose_name='caller name', blank=True)),
                ('call_timeout', models.IntegerField(default=b'60', help_text='call timeout', verbose_name='call timeout')),
                ('voicemail', models.BooleanField(default=False, verbose_name='voicemail detection')),
                ('amd_behavior', models.IntegerField(default=1, null=True, verbose_name='detection behaviour', blank=True, choices=[(1, 'ALWAYS PLAY MESSAGE'), (2, 'PLAY MESSAGE TO HUMAN ONLY'), (3, 'LEAVE MESSAGE TO VOICEMAIL ONLY')])),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('aleg_gateway', models.ForeignKey(verbose_name='a-leg gateway', to='dialer_gateway.Gateway', help_text='select gateway to use')),
                ('sms_gateway', models.ForeignKey(related_name='sms_gateway', verbose_name='SMS gateway', to='sms.Gateway', help_text='select SMS gateway')),
                ('survey', models.ForeignKey(related_name='calendar_survey', verbose_name='sealed survey', to='survey.Survey')),
                ('user', models.ForeignKey(related_name='manager_user', verbose_name='manager', to=settings.AUTH_USER_MODEL, help_text='select manager')),
                ('voicemail_audiofile', models.ForeignKey(verbose_name='voicemail audio file', blank=True, to='audiofield.AudioFile', null=True)),
            ],
            options={
                'db_table': 'calendar_setting',
                'verbose_name': 'Calender setting',
                'verbose_name_plural': 'calendar settings',
                'permissions': (('view_calendarsetting', 'can see Calendar Setting list'),),
            },
            bases=(models.Model,),
        ),
    ]
