# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_auto_20150601_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='api_url',
            field=models.URLField(help_text='URL that will be used to perform an API request', max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section_template',
            name='api_url',
            field=models.URLField(help_text='URL that will be used to perform an API request', max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='section',
            name='type',
            field=models.IntegerField(default=1, max_length=20, verbose_name='section type', choices=[(11, 'API'), (6, 'CALL TRANSFER'), (4, 'CAPTURE DIGITS'), (8, 'CONFERENCE'), (9, 'DNC'), (7, 'HANGUP'), (2, 'MULTI-CHOICE'), (1, 'PLAY MESSAGE'), (3, 'RATING QUESTION'), (5, 'RECORD MESSAGE'), (10, 'SMS')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='section_template',
            name='type',
            field=models.IntegerField(default=1, max_length=20, verbose_name='section type', choices=[(11, 'API'), (6, 'CALL TRANSFER'), (4, 'CAPTURE DIGITS'), (8, 'CONFERENCE'), (9, 'DNC'), (7, 'HANGUP'), (2, 'MULTI-CHOICE'), (1, 'PLAY MESSAGE'), (3, 'RATING QUESTION'), (5, 'RECORD MESSAGE'), (10, 'SMS')]),
            preserve_default=True,
        ),
    ]
