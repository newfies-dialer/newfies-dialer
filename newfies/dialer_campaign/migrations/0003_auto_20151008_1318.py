# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialer_campaign', '0002_campaign_stoppeddate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='calltimeout',
            field=models.IntegerField(default=b'45', help_text='dialing timeout in seconds', null=True, verbose_name='timeout on dialing', blank=True),
            preserve_default=True,
        ),
    ]
