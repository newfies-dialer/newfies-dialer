# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialer_campaign', '0003_auto_20151008_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='record_bleg',
            field=models.BooleanField(default=False, help_text='enable recording of the transferred leg of the call', verbose_name='record b-leg'),
            preserve_default=True,
        ),
    ]
