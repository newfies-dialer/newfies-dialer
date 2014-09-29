# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MailSpooler',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact_email', models.EmailField(max_length=75, verbose_name='contact email')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('parameter', models.CharField(max_length=1000, null=True, verbose_name='parameter', blank=True)),
                ('mailspooler_type', models.IntegerField(default=1, null=True, verbose_name='type', blank=True, choices=[(3, 'FAILURE'), (4, 'IN_PROCESS'), (1, 'PENDING'), (2, 'SENT')])),
            ],
            options={
                'verbose_name': 'mail spooler',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(help_text='mail template name', max_length=75, verbose_name='label')),
                ('template_key', models.CharField(help_text='unique name used to pick some template for recurring action, such as activation or warning', unique=True, max_length=30, verbose_name='template key')),
                ('from_email', models.EmailField(help_text='sender email', max_length=75, verbose_name='from_email')),
                ('from_name', models.CharField(help_text='sender name', max_length=75, verbose_name='from_name')),
                ('subject', models.CharField(help_text='email subject', max_length=200, verbose_name='subject')),
                ('message_plaintext', models.TextField(help_text='plain text version of the email', max_length=5000, verbose_name='message plaintext')),
                ('message_html', models.TextField(help_text='HTML version of the Email', max_length=5000, verbose_name='message_html')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Mail template',
                'verbose_name_plural': 'Mail templates',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='mailspooler',
            name='mailtemplate',
            field=models.ForeignKey(verbose_name='mail template', to='mod_mailer.MailTemplate'),
            preserve_default=True,
        ),
    ]
