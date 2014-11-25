# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_settings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarsetting',
            name='callerid',
            field=models.CharField(help_text='outbound Caller ID', max_length=80, null=True, verbose_name='Caller ID Number', blank=True),
            preserve_default=True,
        ),
    ]
