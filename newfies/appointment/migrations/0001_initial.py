# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import appointment.models.events
import django_countries.fields
import django.utils.timezone
from django.conf import settings
import django_lets_go.language_field


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0001_initial'),
        ('dialer_gateway', '0001_initial'),
        ('survey', '0001_initial'),
        ('mod_sms', '0001_initial'),
        ('dialer_cdr', '0001_initial'),
        ('mod_mailer', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('audiofield', '__first__'),
        ('auth', '0002_calendaruser_manager_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alarm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alarm_phonenumber', models.CharField(max_length=50, null=True, verbose_name='notify to phone number', blank=True)),
                ('alarm_email', models.EmailField(max_length=75, null=True, verbose_name='notify to email', blank=True)),
                ('daily_start', models.TimeField(default=b'00:00:00', verbose_name='daily start')),
                ('daily_stop', models.TimeField(default=b'23:59:59', verbose_name='daily stop')),
                ('advance_notice', models.IntegerField(default=0, help_text='Seconds to start processing an alarm before the alarm date/time', verbose_name='advance notice')),
                ('maxretry', models.IntegerField(default=0, help_text='number of retries', verbose_name='max retry')),
                ('retry_delay', models.IntegerField(default=0, help_text='Seconds to wait between retries', verbose_name='retry delay')),
                ('num_attempt', models.IntegerField(default=0, verbose_name='number of attempts')),
                ('method', models.IntegerField(default=1, verbose_name='method', choices=[(1, 'CALL'), (3, 'EMAIL'), (2, 'SMS')])),
                ('date_start_notice', models.DateTimeField(default=django.utils.timezone.now, verbose_name='alarm date')),
                ('status', models.IntegerField(default=1, verbose_name='status', choices=[(3, 'FAILURE'), (2, 'IN_PROCESS'), (1, 'PENDING'), (4, 'RETRY'), (5, 'SUCCESS')])),
                ('result', models.IntegerField(default=0, null=True, verbose_name='result', blank=True, choices=[(2, 'CANCELLED'), (1, 'CONFIRMED'), (0, 'NO RESULT'), (3, 'RESCHEDULED')])),
                ('url_cancel', models.CharField(max_length=250, null=True, verbose_name='URL cancel', blank=True)),
                ('url_confirm', models.CharField(max_length=250, null=True, verbose_name='URL confirm', blank=True)),
                ('phonenumber_transfer', models.CharField(max_length=50, null=True, verbose_name='phone number transfer', blank=True)),
                ('phonenumber_sms_failure', models.CharField(max_length=50, null=True, verbose_name='phone number SMS failure', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
            ],
            options={
                'verbose_name': 'alarm',
                'verbose_name_plural': 'alarms',
                'permissions': (('view_alarm', 'can see Alarm list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlarmRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(help_text='date when the alarm will be scheduled', verbose_name='date')),
                ('status', models.IntegerField(default=1, null=True, verbose_name='status', blank=True, choices=[(3, 'FAILURE'), (2, 'IN PROCESS'), (1, 'PENDING'), (4, 'RETRY'), (5, 'SUCCESS')])),
                ('callstatus', models.IntegerField(default=0, null=True, blank=True)),
                ('duration', models.IntegerField(default=0, null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('alarm', models.ForeignKey(related_name=b'request_alarm', blank=True, to='appointment.Alarm', help_text='select alarm', null=True, verbose_name='alarm')),
                ('callrequest', models.ForeignKey(related_name=b'callrequest_alarm', blank=True, to='dialer_cdr.Callrequest', help_text='select call request', null=True, verbose_name='Call Request')),
            ],
            options={
                'verbose_name': 'alarm request',
                'verbose_name_plural': 'alarm requests',
                'permissions': (('view_alarm_request', 'can see Alarm request list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('max_concurrent', models.IntegerField(default=0, help_text='Max concurrent is not implemented', null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('user', models.ForeignKey(related_name=b'calendar user', blank=True, to='auth.CalendarUser', help_text='select user', null=True, verbose_name='calendar user')),
            ],
            options={
                'verbose_name': 'calendar',
                'verbose_name_plural': 'calendars',
                'permissions': (('view_calendar', 'Can see Calendar list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalendarSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=80, verbose_name='label')),
                ('callerid', models.CharField(help_text='outbound Caller ID', max_length=80, verbose_name='Caller ID Number')),
                ('caller_name', models.CharField(help_text='outbound caller-Name', max_length=80, verbose_name='caller name', blank=True)),
                ('call_timeout', models.IntegerField(default=b'60', help_text='call timeout', verbose_name='call timeout')),
                ('voicemail', models.BooleanField(default=False, verbose_name='voicemail detection')),
                ('amd_behavior', models.IntegerField(default=1, null=True, verbose_name='detection behaviour', blank=True, choices=[(1, 'ALWAYS PLAY MESSAGE'), (2, 'PLAY MESSAGE TO HUMAN ONLY'), (3, 'LEAVE MESSAGE TO VOICEMAIL ONLY')])),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('aleg_gateway', models.ForeignKey(verbose_name='a-leg gateway', to='dialer_gateway.Gateway', help_text='select gateway to use')),
                ('sms_gateway', models.ForeignKey(related_name=b'sms_gateway', verbose_name='SMS gateway', to='sms.Gateway', help_text='select SMS gateway')),
                ('survey', models.ForeignKey(related_name=b'calendar_survey', verbose_name='sealed survey', to='survey.Survey')),
                ('user', models.ForeignKey(related_name=b'manager_user', verbose_name='manager', to=settings.AUTH_USER_MODEL, help_text='select manager')),
                ('voicemail_audiofile', models.ForeignKey(verbose_name='voicemail audio file', blank=True, to='audiofield.AudioFile', null=True)),
            ],
            options={
                'db_table': 'calendar_setting',
                'verbose_name': 'Calender setting',
                'verbose_name_plural': 'calendar settings',
                'permissions': (('view_calendarsetting', 'can see Calendar Setting list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalendarUserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(max_length=200, null=True, verbose_name='address', blank=True)),
                ('city', models.CharField(max_length=120, null=True, verbose_name='city', blank=True)),
                ('state', models.CharField(max_length=120, null=True, verbose_name='state', blank=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='country')),
                ('zip_code', models.CharField(max_length=120, null=True, verbose_name='zip code', blank=True)),
                ('phone_no', models.CharField(max_length=90, null=True, verbose_name='phone number', blank=True)),
                ('fax', models.CharField(max_length=90, null=True, verbose_name='fax Number', blank=True)),
                ('company_name', models.CharField(max_length=90, null=True, verbose_name='company name', blank=True)),
                ('company_website', models.URLField(max_length=90, null=True, verbose_name='company website', blank=True)),
                ('language', django_lets_go.language_field.LanguageField(blank=True, max_length=2, null=True, verbose_name='language', choices=[(b'aa', 'Afar'), (b'ab', 'Abkhazian'), (b'af', 'Afrikaans'), (b'ak', 'Akan'), (b'sq', 'Albanian'), (b'am', 'Amharic'), (b'ar', 'Arabic'), (b'an', 'Aragonese'), (b'hy', 'Armenian'), (b'as', 'Assamese'), (b'av', 'Avaric'), (b'ae', 'Avestan'), (b'ay', 'Aymara'), (b'az', 'Azerbaijani'), (b'ba', 'Bashkir'), (b'bm', 'Bambara'), (b'eu', 'Basque'), (b'be', 'Belarusian'), (b'bn', 'Bengali'), (b'bh', 'Bihari languages'), (b'bi', 'Bislama'), (b'bo', 'Tibetan'), (b'bs', 'Bosnian'), (b'br', 'Breton'), (b'bg', 'Bulgarian'), (b'my', 'Burmese'), (b'ca', 'Catalan; Valencian'), (b'cs', 'Czech'), (b'ch', 'Chamorro'), (b'ce', 'Chechen'), (b'zh', 'Chinese'), (b'cu', 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic'), (b'cv', 'Chuvash'), (b'kw', 'Cornish'), (b'co', 'Corsican'), (b'cr', 'Cree'), (b'cy', 'Welsh'), (b'cs', 'Czech'), (b'da', 'Danish'), (b'de', 'German'), (b'dv', 'Divehi; Dhivehi; Maldivian'), (b'nl', 'Dutch; Flemish'), (b'dz', 'Dzongkha'), (b'el', 'Greek, Modern (1453-)'), (b'en', 'English'), (b'eo', 'Esperanto'), (b'et', 'Estonian'), (b'eu', 'Basque'), (b'ee', 'Ewe'), (b'fo', 'Faroese'), (b'fa', 'Persian'), (b'fj', 'Fijian'), (b'fi', 'Finnish'), (b'fr', 'French'), (b'fr', 'French'), (b'fy', 'Western Frisian'), (b'ff', 'Fulah'), (b'ka', 'Georgian'), (b'de', 'German'), (b'gd', 'Gaelic; Scottish Gaelic'), (b'ga', 'Irish'), (b'gl', 'Galician'), (b'gv', 'Manx'), (b'el', 'Greek, Modern (1453-)'), (b'gn', 'Guarani'), (b'gu', 'Gujarati'), (b'ht', 'Haitian; Haitian Creole'), (b'ha', 'Hausa'), (b'he', 'Hebrew'), (b'hz', 'Herero'), (b'hi', 'Hindi'), (b'ho', 'Hiri Motu'), (b'hr', 'Croatian'), (b'hu', 'Hungarian'), (b'hy', 'Armenian'), (b'ig', 'Igbo'), (b'is', 'Icelandic'), (b'io', 'Ido'), (b'ii', 'Sichuan Yi; Nuosu'), (b'iu', 'Inuktitut'), (b'ie', 'Interlingue; Occidental'), (b'ia', 'Interlingua (International Auxiliary Language Association)'), (b'id', 'Indonesian'), (b'ik', 'Inupiaq'), (b'is', 'Icelandic'), (b'it', 'Italian'), (b'jv', 'Javanese'), (b'ja', 'Japanese'), (b'kl', 'Kalaallisut; Greenlandic'), (b'kn', 'Kannada'), (b'ks', 'Kashmiri'), (b'ka', 'Georgian'), (b'kr', 'Kanuri'), (b'kk', 'Kazakh'), (b'km', 'Central Khmer'), (b'ki', 'Kikuyu; Gikuyu'), (b'rw', 'Kinyarwanda'), (b'ky', 'Kirghiz; Kyrgyz'), (b'kv', 'Komi'), (b'kg', 'Kongo'), (b'ko', 'Korean'), (b'kj', 'Kuanyama; Kwanyama'), (b'ku', 'Kurdish'), (b'lo', 'Lao'), (b'la', 'Latin'), (b'lv', 'Latvian'), (b'li', 'Limburgan; Limburger; Limburgish'), (b'ln', 'Lingala'), (b'lt', 'Lithuanian'), (b'lb', 'Luxembourgish; Letzeburgesch'), (b'lu', 'Luba-Katanga'), (b'lg', 'Ganda'), (b'mk', 'Macedonian'), (b'mh', 'Marshallese'), (b'ml', 'Malayalam'), (b'mi', 'Maori'), (b'mr', 'Marathi'), (b'ms', 'Malay'), (b'mk', 'Macedonian'), (b'mg', 'Malagasy'), (b'mt', 'Maltese'), (b'mn', 'Mongolian'), (b'mi', 'Maori'), (b'ms', 'Malay'), (b'my', 'Burmese'), (b'na', 'Nauru'), (b'nv', 'Navajo; Navaho'), (b'nr', 'Ndebele, South; South Ndebele'), (b'nd', 'Ndebele, North; North Ndebele'), (b'ng', 'Ndonga'), (b'ne', 'Nepali'), (b'nl', 'Dutch; Flemish'), (b'nn', 'Norwegian Nynorsk; Nynorsk, Norwegian'), (b'nb', 'Bokmal, Norwegian; Norwegian Bokmal'), (b'no', 'Norwegian'), (b'ny', 'Chichewa; Chewa; Nyanja'), (b'oc', 'Occitan (post 1500)'), (b'oj', 'Ojibwa'), (b'or', 'Oriya'), (b'om', 'Oromo'), (b'os', 'Ossetian; Ossetic'), (b'pa', 'Panjabi; Punjabi'), (b'fa', 'Persian'), (b'pi', 'Pali'), (b'pl', 'Polish'), (b'pt', 'Portuguese'), (b'ps', 'Pushto; Pashto'), (b'qu', 'Quechua'), (b'rm', 'Romansh'), (b'ro', 'Romanian; Moldavian; Moldovan'), (b'ro', 'Romanian; Moldavian; Moldovan'), (b'rn', 'Rundi'), (b'ru', 'Russian'), (b'sg', 'Sango'), (b'sa', 'Sanskrit'), (b'si', 'Sinhala; Sinhalese'), (b'sk', 'Slovak'), (b'sk', 'Slovak'), (b'sl', 'Slovenian'), (b'se', 'Northern Sami'), (b'sm', 'Samoan'), (b'sn', 'Shona'), (b'sd', 'Sindhi'), (b'so', 'Somali'), (b'st', 'Sotho, Southern'), (b'es', 'Spanish; Castilian'), (b'sq', 'Albanian'), (b'sc', 'Sardinian'), (b'sr', 'Serbian'), (b'ss', 'Swati'), (b'su', 'Sundanese'), (b'sw', 'Swahili'), (b'sv', 'Swedish'), (b'ty', 'Tahitian'), (b'ta', 'Tamil'), (b'tt', 'Tatar'), (b'te', 'Telugu'), (b'tg', 'Tajik'), (b'tl', 'Tagalog'), (b'th', 'Thai'), (b'bo', 'Tibetan'), (b'ti', 'Tigrinya'), (b'to', 'Tonga (Tonga Islands)'), (b'tn', 'Tswana'), (b'ts', 'Tsonga'), (b'tk', 'Turkmen'), (b'tr', 'Turkish'), (b'tw', 'Twi'), (b'ug', 'Uighur; Uyghur'), (b'uk', 'Ukrainian'), (b'ur', 'Urdu'), (b'uz', 'Uzbek'), (b've', 'Venda'), (b'vi', 'Vietnamese'), (b'vo', 'Volapuk'), (b'cy', 'Welsh'), (b'wa', 'Walloon'), (b'wo', 'Wolof'), (b'xh', 'Xhosa'), (b'yi', 'Yiddish'), (b'yo', 'Yoruba'), (b'za', 'Zhuang; Chuang'), (b'zh', 'Chinese'), (b'zu', 'Zulu')])),
                ('note', models.CharField(max_length=250, null=True, verbose_name='note', blank=True)),
                ('accountcode', models.PositiveIntegerField(null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('calendar_setting', models.ForeignKey(verbose_name='calendar settings', to='appointment.CalendarSetting')),
                ('manager', models.ForeignKey(related_name=b'manager_of_calendar_user', verbose_name='manager', to='auth.Manager', help_text='select manager')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'calendar_user_profile',
                'verbose_name': 'calendar user profile',
                'verbose_name_plural': 'calendar user profiles',
                'permissions': (('view_calendar_user', 'can see Calendar User list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='label')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='start')),
                ('end', models.DateTimeField(default=appointment.models.events.set_end, help_text='Must be later than the start', verbose_name='end')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created on')),
                ('end_recurring_period', models.DateTimeField(default=appointment.models.events.set_end_recurring_period, help_text='Used if the event recurs', null=True, verbose_name='end recurring period', blank=True)),
                ('notify_count', models.IntegerField(default=0, null=True, verbose_name='notify count', blank=True)),
                ('status', models.IntegerField(default=1, null=True, verbose_name='status', blank=True, choices=[(2, 'COMPLETED'), (3, 'PAUSED'), (1, 'PENDING')])),
                ('data', jsonfield.fields.JSONField(help_text='data in JSON format, e.g. {"cost": "40 euro"}', null=True, verbose_name='additional data (JSON)', blank=True)),
                ('occ_count', models.IntegerField(default=0, null=True, verbose_name='occurrence count', blank=True)),
                ('calendar', models.ForeignKey(to='appointment.Calendar')),
                ('creator', models.ForeignKey(related_name=b'creator', verbose_name='calendar user', to='auth.CalendarUser')),
                ('parent_event', models.ForeignKey(related_name=b'parent event', blank=True, to='appointment.Event', null=True)),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
                'permissions': (('view_event', 'can see Event list'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, null=True, verbose_name='title', blank=True)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('start', models.DateTimeField(verbose_name='start')),
                ('end', models.DateTimeField(verbose_name='end')),
                ('cancelled', models.BooleanField(default=False, verbose_name='cancelled')),
                ('original_start', models.DateTimeField(verbose_name='original start')),
                ('original_end', models.DateTimeField(verbose_name='original end')),
                ('event', models.ForeignKey(verbose_name='event', to='appointment.Event')),
            ],
            options={
                'verbose_name': 'occurrence',
                'verbose_name_plural': 'occurrences',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('frequency', models.CharField(max_length=10, verbose_name='frequency', choices=[(b'YEARLY', 'Yearly'), (b'MONTHLY', 'Monthly'), (b'WEEKLY', 'Weekly'), (b'DAILY', 'Daily'), (b'HOURLY', 'Hourly'), (b'MINUTELY', 'Minutely'), (b'SECONDLY', 'Secondly')])),
                ('params', models.TextField(help_text='example : count:1;bysecond:3;', null=True, verbose_name='params', blank=True)),
            ],
            options={
                'verbose_name': 'rule',
                'verbose_name_plural': 'rules',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='rule',
            field=models.ForeignKey(blank=True, to='appointment.Rule', help_text='Recuring rules', null=True, verbose_name='rule'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='event',
            field=models.ForeignKey(related_name=b'event', verbose_name='related to event', to='appointment.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='mail_template',
            field=models.ForeignKey(related_name=b'mail template', verbose_name='mail', blank=True, to='mod_mailer.MailTemplate', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='sms_template',
            field=models.ForeignKey(related_name=b'sms template', verbose_name='SMS', blank=True, to='mod_sms.SMSTemplate', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alarm',
            name='survey',
            field=models.ForeignKey(related_name=b'survey', verbose_name='survey', blank=True, to='survey.Survey', null=True),
            preserve_default=True,
        ),
    ]
