# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dialer_campaign.models


class Migration(migrations.Migration):

    dependencies = [
        ('dialer_campaign', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='stoppeddate',
            field=models.DateTimeField(default=dialer_campaign.models.set_expirationdate, verbose_name='stopped'),
            preserve_default=True,
        ),
    ]
