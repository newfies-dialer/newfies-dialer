# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dialer_cdr', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callrequest',
            name='timeout',
            field=models.IntegerField(default=30, verbose_name='dialing time out', blank=True),
            preserve_default=True,
        ),
    ]
