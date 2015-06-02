# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='confirm_key',
            field=models.CharField(max_length=1, null=True, verbose_name='confirm key', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='confirm_script',
            field=models.CharField(help_text='Example: Please pull up the file {filenumber} for this call', max_length=1000, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section_template',
            name='confirm_key',
            field=models.CharField(max_length=1, null=True, verbose_name='confirm key', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section_template',
            name='confirm_script',
            field=models.CharField(help_text='Example: Please pull up the file {filenumber} for this call', max_length=1000, null=True, blank=True),
            preserve_default=True,
        ),
    ]
