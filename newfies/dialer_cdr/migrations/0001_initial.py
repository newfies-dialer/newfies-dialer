# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dialer_cdr.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dialer_campaign', '0001_initial'),
        ('country_dialcode', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dialer_gateway', '__first__'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Callrequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_uuid', models.CharField(default=dialer_cdr.models.str_uuid1, max_length=120, blank=True, null=True, verbose_name='RequestUUID', db_index=True)),
                ('aleg_uuid', models.CharField(help_text='a-leg call-ID', max_length=120, null=True, blank=True)),
                ('call_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('call_type', models.IntegerField(default=1, null=True, verbose_name='call request type', blank=True, choices=[(1, 'ALLOW RETRY'), (2, 'CANNOT RETRY'), (3, 'RETRY DONE')])),
                ('status', models.IntegerField(default=1, choices=[(5, 'abort'), (7, 'calling'), (2, 'failure'), (6, 'pause'), (1, 'pending'), (3, 'retry'), (4, 'success')], blank=True, null=True, verbose_name='status', db_index=True)),
                ('callerid', models.CharField(help_text='outbound Caller ID', max_length=80, verbose_name='Caller ID Number', blank=True)),
                ('caller_name', models.CharField(help_text='outbound caller-Name', max_length=80, verbose_name='caller name', blank=True)),
                ('phone_number', models.CharField(max_length=80, verbose_name='phone number')),
                ('timeout', models.IntegerField(default=30, verbose_name='time out', blank=True)),
                ('timelimit', models.IntegerField(default=3600, verbose_name='time limit', blank=True)),
                ('extra_dial_string', models.CharField(max_length=500, verbose_name='extra dial string', blank=True)),
                ('object_id', models.PositiveIntegerField(verbose_name='application')),
                ('completed', models.BooleanField(default=False, verbose_name='call completed')),
                ('extra_data', models.CharField(help_text='define the additional data to pass to the application', max_length=120, verbose_name='extra data', blank=True)),
                ('num_attempt', models.IntegerField(default=0)),
                ('last_attempt_time', models.DateTimeField(null=True, blank=True)),
                ('result', models.CharField(max_length=180, blank=True)),
                ('hangup_cause', models.CharField(max_length=80, blank=True)),
                ('alarm_request_id', models.IntegerField(default=0, null=True, verbose_name='alarm request id', blank=True)),
                ('aleg_gateway', models.ForeignKey(blank=True, to='dialer_gateway.Gateway', help_text='select gateway', null=True, verbose_name='a-leg gateway')),
                ('campaign', models.ForeignKey(blank=True, to='dialer_campaign.Campaign', help_text='select Campaign', null=True)),
                ('content_type', models.ForeignKey(verbose_name='type', to='contenttypes.ContentType')),
                ('parent_callrequest', models.ForeignKey(blank=True, to='dialer_cdr.Callrequest', null=True)),
                ('subscriber', models.ForeignKey(blank=True, to='dialer_campaign.Subscriber', help_text='subscriber related to this call request', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dialer_callrequest',
                'verbose_name': 'call request',
                'verbose_name_plural': 'call requests',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VoIPCall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_uuid', models.CharField(default=dialer_cdr.models.str_uuid1, max_length=120, null=True, verbose_name='RequestUUID', blank=True)),
                ('callid', models.CharField(help_text='VoIP call-ID', max_length=120)),
                ('callerid', models.CharField(max_length=120, verbose_name='CallerID')),
                ('phone_number', models.CharField(help_text='the international number of the recipient, without the leading +', max_length=120, null=True, verbose_name='phone number', blank=True)),
                ('starting_date', models.DateTimeField(auto_now_add=True, verbose_name='starting date', db_index=True)),
                ('duration', models.IntegerField(null=True, verbose_name='duration', blank=True)),
                ('billsec', models.IntegerField(null=True, verbose_name='bill sec', blank=True)),
                ('progresssec', models.IntegerField(null=True, verbose_name='progress sec', blank=True)),
                ('answersec', models.IntegerField(null=True, verbose_name='answer sec', blank=True)),
                ('waitsec', models.IntegerField(null=True, verbose_name='wait sec', blank=True)),
                ('disposition', models.CharField(blank=True, max_length=40, null=True, verbose_name='disposition', choices=[(b'ANSWER', 'ANSWER'), (b'BUSY', 'BUSY'), (b'CANCEL', 'CANCEL'), (b'CONGESTION', 'CONGESTION'), (b'FAILED', 'FAILED'), (b'NOANSWER', 'NOANSWER')])),
                ('hangup_cause', models.CharField(max_length=40, null=True, verbose_name='hangup cause', blank=True)),
                ('hangup_cause_q850', models.CharField(max_length=10, null=True, blank=True)),
                ('leg_type', models.SmallIntegerField(default=1, null=True, verbose_name='leg', blank=True, choices=[(1, 'A-Leg'), (2, 'B-Leg')])),
                ('amd_status', models.SmallIntegerField(default=1, null=True, verbose_name='AMD Status', blank=True, choices=[(2, 'MACHINE'), (1, 'PERSON'), (3, 'UNSURE')])),
                ('callrequest', models.ForeignKey(verbose_name='callrequest', blank=True, to='dialer_cdr.Callrequest', null=True)),
                ('dialcode', models.ForeignKey(blank=True, to='country_dialcode.Prefix', help_text='select prefix', null=True, verbose_name='destination')),
                ('used_gateway', models.ForeignKey(verbose_name='used gateway', blank=True, to='dialer_gateway.Gateway', null=True)),
                ('user', models.ForeignKey(related_name='Call Sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dialer_cdr',
                'verbose_name': 'VoIP call',
                'verbose_name_plural': 'VoIP calls',
                'permissions': (('view_call_detail_report', 'can see call detail report'),),
            },
            bases=(models.Model,),
        ),
    ]
