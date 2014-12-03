# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import django_countries.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact', models.CharField(max_length=90, verbose_name='contact number')),
                ('status', models.IntegerField(default=1, null=True, verbose_name='status', blank=True, choices=[(1, 'active'), (0, 'inactive')])),
                ('last_name', models.CharField(max_length=120, null=True, verbose_name='last name', blank=True)),
                ('first_name', models.CharField(max_length=120, null=True, verbose_name='first name', blank=True)),
                ('email', models.EmailField(max_length=75, null=True, verbose_name='email', blank=True)),
                ('address', models.CharField(max_length=250, null=True, verbose_name='address', blank=True)),
                ('city', models.CharField(max_length=120, null=True, verbose_name='city', blank=True)),
                ('state', models.CharField(max_length=120, null=True, verbose_name='state', blank=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='country')),
                ('unit_number', models.CharField(max_length=50, null=True, verbose_name='unit number', blank=True)),
                ('additional_vars', jsonfield.fields.JSONField(help_text='enter the list of parameters in JSON format, e.g. {"age": "32"}', null=True, verbose_name='additional parameters (JSON)', blank=True)),
                ('description', models.TextField(null=True, verbose_name='notes', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'dialer_contact',
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
                'permissions': (('view_contact', 'can see contact'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Phonebook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=90, verbose_name='name')),
                ('description', models.TextField(help_text='phonebook notes', null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(related_name='Phonebook owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'dialer_phonebook',
                'verbose_name': 'phonebook',
                'verbose_name_plural': 'phonebooks',
                'permissions': (('view_phonebook', 'can see phonebook'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='contact',
            name='phonebook',
            field=models.ForeignKey(verbose_name='phonebook', to='dialer_contact.Phonebook'),
            preserve_default=True,
        ),
    ]
