# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DialerSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='settings name', max_length=50, null=True, verbose_name='name')),
                ('max_frequency', models.IntegerField(default=b'100', help_text='maximum calls per minute', null=True, verbose_name='max frequency', blank=True)),
                ('callmaxduration', models.IntegerField(default=b'1800', help_text='maximum call duration in seconds (1800 = 30 Minutes)', null=True, verbose_name='max Call Duration', blank=True)),
                ('maxretry', models.IntegerField(default=b'3', help_text='maximum retries per user.', null=True, verbose_name='max retries', blank=True)),
                ('max_calltimeout', models.IntegerField(default=b'45', help_text='maximum call timeout in seconds', null=True, verbose_name='timeout on call', blank=True)),
                ('max_cpg', models.IntegerField(default=100, help_text='maximum number of campaigns', verbose_name='maximum number of campaigns')),
                ('max_subr_cpg', models.IntegerField(default=100000, help_text='maximum subscribers per campaign. Unlimited if the value equal 0', verbose_name='maximum subscribers per campaign')),
                ('max_contact', models.IntegerField(default=1000000, help_text='maximum number of contacts per user. Unlimited if the value equal 0', verbose_name='maximum number of contacts')),
                ('blacklist', models.TextField(default=b'', help_text="use regular expressions to blacklist phone numbers. For example, '^[2-4][1]+' will prevent all phone numbers starting with 2,3 or 4 and followed by 1 being called.", null=True, verbose_name='blacklist', blank=True)),
                ('whitelist', models.TextField(default=b'', help_text='use regular expressions to whitelist phone numbers', null=True, verbose_name='whitelist', blank=True)),
                ('sms_max_frequency', models.IntegerField(default=b'100', help_text='Maximum SMS per minute', null=True, verbose_name='Max frequency', blank=True)),
                ('sms_maxretry', models.IntegerField(default=b'3', help_text='Maximum SMS retries per user.', null=True, verbose_name='Max Retries', blank=True)),
                ('sms_max_number_campaign', models.IntegerField(default=10, help_text='Maximum number of SMS campaigns', verbose_name='Max SMS campaigns')),
                ('sms_max_number_subscriber_campaign', models.IntegerField(default=10000, help_text='Maximum subscribers per SMS campaign', verbose_name='Max subscribers of SMS campaigns')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'dialer_setting',
                'verbose_name': 'dialer setting',
                'verbose_name_plural': 'dialer settings',
            },
            bases=(models.Model,),
        ),
    ]
