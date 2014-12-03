# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mod_sms.models


class Migration(migrations.Migration):

    dependencies = [
        ('mod_sms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='smscampaign',
            name='stoppeddate',
            field=models.DateTimeField(default=mod_sms.models.set_expirationdate, verbose_name='stopped'),
            preserve_default=True,
        ),
    ]
