# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gateway',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='gateway name', unique=True, max_length=255, verbose_name='name')),
                ('status', models.IntegerField(default=1, null=True, verbose_name='gateway status', blank=True, choices=[(1, 'active'), (0, 'inactive')])),
                ('description', models.TextField(help_text='gateway provider notes', verbose_name='description', blank=True)),
                ('addprefix', models.CharField(max_length=60, verbose_name='add prefix', blank=True)),
                ('removeprefix', models.CharField(max_length=60, verbose_name='remove prefix', blank=True)),
                ('gateways', models.CharField(help_text='Gateway string to dial, ie "sofia/gateway/myprovider/"', max_length=500, verbose_name='gateways')),
                ('gateway_codecs', models.CharField(help_text='codec string as needed by FS, ie "PCMA,PCMU"', max_length=500, verbose_name='gateway codecs', blank=True)),
                ('gateway_timeouts', models.CharField(help_text='timeout in seconds, ie "10"', max_length=500, verbose_name='gateway timeouts', blank=True)),
                ('gateway_retries', models.CharField(help_text='"2,1", # retry String for Gateways separated by comma, on how many times each gateway should be retried', max_length=500, verbose_name='gateway retries', blank=True)),
                ('originate_dial_string', models.CharField(help_text='add channels variables : http://wiki.freeswitch.org/wiki/Channel_Variables, ie: bridge_early_media=true,hangup_after_bridge=true', max_length=500, verbose_name='originate dial string', blank=True)),
                ('secondused', models.IntegerField(null=True, verbose_name='second used', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('addparameter', models.CharField(max_length=360, verbose_name='add parameter', blank=True)),
                ('count_call', models.IntegerField(null=True, verbose_name='call count', blank=True)),
                ('count_in_use', models.IntegerField(null=True, verbose_name='count in use', blank=True)),
                ('maximum_call', models.IntegerField(null=True, verbose_name='max concurrent calls', blank=True)),
                ('failover', models.ForeignKey(related_name=b'Failover Gateway', blank=True, to='dialer_gateway.Gateway', help_text='select gateway', null=True)),
            ],
            options={
                'db_table': 'dialer_gateway',
                'verbose_name': 'dialer gateway',
                'verbose_name_plural': 'dialer gateways',
            },
            bases=(models.Model,),
        ),
    ]
