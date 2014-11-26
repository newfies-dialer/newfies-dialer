# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DNC',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Enter a DNC list name', max_length=50, null=True, verbose_name='name')),
                ('description', models.TextField(help_text='DNC notes', null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(related_name='DNC owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dnc_list',
                'verbose_name': 'Do Not Call list',
                'verbose_name_plural': 'Do Not Call lists',
                'permissions': (('view_dnc', 'can see Do Not Call list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DNCContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=120, verbose_name='phone number', db_index=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('dnc', models.ForeignKey(verbose_name='Do Not Call List', to='dnc.DNC')),
            ],
            options={
                'db_table': 'dnc_contact',
                'verbose_name': 'Do Not Call contact',
                'verbose_name_plural': 'Do Not Call contacts',
                'permissions': (('view_dnc_contact', 'can see Do Not Call contact'),),
            },
            bases=(models.Model,),
        ),
    ]
