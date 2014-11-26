# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_countries.fields
import django_lets_go.language_field
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('dialer_settings', '0001_initial'),
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dialer_gateway', '__first__'),
        ('calendar_settings', '0001_initial'),
    ]

    operations = [
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
                ('calendar_setting', models.ForeignKey(verbose_name='calendar settings', to='calendar_settings.CalendarSetting')),
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
            name='UserProfile',
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
                ('dialersetting', models.ForeignKey(verbose_name='dialer settings', blank=True, to='dialer_settings.DialerSetting', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
                ('userprofile_gateway', models.ManyToManyField(to='dialer_gateway.Gateway', verbose_name='gateway')),
            ],
            options={
                'db_table': 'user_profile',
                'verbose_name': 'user profile',
                'verbose_name_plural': 'user profiles',
                'permissions': (('view_api_explorer', 'can see API-Explorer'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalendarUser',
            fields=[
            ],
            options={
                'verbose_name': 'calendar user',
                'proxy': True,
                'verbose_name_plural': 'calendar users',
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
            ],
            options={
                'verbose_name': 'manager',
                'proxy': True,
                'verbose_name_plural': 'managers',
            },
            bases=('auth.user',),
        ),
        migrations.AddField(
            model_name='calendaruserprofile',
            name='manager',
            field=models.ForeignKey(related_name='manager_of_calendar_user', verbose_name='manager', to='user_profile.Manager', help_text='select manager'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
            ],
            options={
                'verbose_name': 'admin',
                'proxy': True,
                'verbose_name_plural': 'admins',
            },
            bases=('auth.user',),
        ),
    ]
