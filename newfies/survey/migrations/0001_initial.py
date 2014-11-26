# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_lets_go.language_field


class Migration(migrations.Migration):

    dependencies = [
        ('dialer_campaign', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('audiofield', '__first__'),
        ('dialer_cdr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branching',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keys', models.CharField(max_length=150, verbose_name='entered value', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'branching',
                'verbose_name_plural': 'branching',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Branching_template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keys', models.CharField(max_length=150, verbose_name='entered value', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'branching template',
                'verbose_name_plural': 'branching templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('response', models.CharField(max_length=150, verbose_name='response')),
                ('record_file', models.CharField(default=b'', max_length=200, verbose_name='record File', blank=True)),
                ('recording_duration', models.IntegerField(default=0, max_length=10, null=True, verbose_name='recording duration', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('callrequest', models.ForeignKey(related_name='survey_callrequest', blank=True, to='dialer_cdr.Callrequest', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResultAggregate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('response', models.CharField(max_length=150, verbose_name='response', db_index=True)),
                ('count', models.IntegerField(default=0, max_length=20, verbose_name='result count')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(default=1, editable=False, db_index=True)),
                ('type', models.IntegerField(default=1, max_length=20, verbose_name='section type', choices=[(6, 'CALL TRANSFER'), (4, 'CAPTURE DIGITS'), (8, 'CONFERENCE'), (9, 'DNC'), (7, 'HANGUP'), (2, 'MULTI-CHOICE'), (1, 'PLAY MESSAGE'), (3, 'RATING QUESTION'), (5, 'RECORD MESSAGE'), (10, 'SMS')])),
                ('question', models.CharField(help_text='Example: hotel service rating', max_length=500, verbose_name='question')),
                ('script', models.CharField(help_text='Example: Press a key between 1 to 5, press pound key when done or Hello {first_name} {last_name}, please press a key between 1 to 5', max_length=1000, null=True, blank=True)),
                ('retries', models.IntegerField(default=0, max_length=1, blank=True, help_text='retries until valid input', null=True, verbose_name='retries')),
                ('timeout', models.IntegerField(default=5, max_length=2, blank=True, help_text='timeout in seconds', null=True, verbose_name='timeout')),
                ('key_0', models.CharField(max_length=100, null=True, verbose_name='key 0', blank=True)),
                ('key_1', models.CharField(max_length=100, null=True, verbose_name='key 1', blank=True)),
                ('key_2', models.CharField(max_length=100, null=True, verbose_name='key 2', blank=True)),
                ('key_3', models.CharField(max_length=100, null=True, verbose_name='key 3', blank=True)),
                ('key_4', models.CharField(max_length=100, null=True, verbose_name='key 4', blank=True)),
                ('key_5', models.CharField(max_length=100, null=True, verbose_name='key 5', blank=True)),
                ('key_6', models.CharField(max_length=100, null=True, verbose_name='key 6', blank=True)),
                ('key_7', models.CharField(max_length=100, null=True, verbose_name='key 7', blank=True)),
                ('key_8', models.CharField(max_length=100, null=True, verbose_name='key 8', blank=True)),
                ('key_9', models.CharField(max_length=100, null=True, verbose_name='key 9', blank=True)),
                ('rating_laps', models.IntegerField(default=9, max_length=1, null=True, verbose_name='from 1 to X', blank=True)),
                ('validate_number', models.BooleanField(default=True, verbose_name='check validity')),
                ('number_digits', models.IntegerField(default=b'2', max_length=2, null=True, verbose_name='number of digits', blank=True)),
                ('min_number', models.BigIntegerField(default=0, max_length=50, null=True, verbose_name='minimum', blank=True)),
                ('max_number', models.BigIntegerField(default=99, max_length=50, null=True, verbose_name='maximum', blank=True)),
                ('phonenumber', models.CharField(max_length=50, null=True, verbose_name='Phone Number / SIP URI', blank=True)),
                ('conference', models.CharField(max_length=50, null=True, verbose_name='conference number', blank=True)),
                ('sms_text', models.CharField(help_text='text that will be send via SMS to the contact', max_length=200, null=True, blank=True)),
                ('completed', models.BooleanField(default=False, verbose_name='survey complete')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('section_template', models.IntegerField(default=0, max_length=10, null=True, verbose_name='section template ID', blank=True)),
                ('audiofile', models.ForeignKey(verbose_name='audio File', blank=True, to='audiofield.AudioFile', null=True)),
                ('invalid_audiofile', models.ForeignKey(related_name='survey_invalid_audiofile', verbose_name='audio invalid input', blank=True, to='audiofield.AudioFile', null=True)),
            ],
            options={
                'ordering': ['order', 'survey'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Section_template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(default=1, editable=False, db_index=True)),
                ('type', models.IntegerField(default=1, max_length=20, verbose_name='section type', choices=[(6, 'CALL TRANSFER'), (4, 'CAPTURE DIGITS'), (8, 'CONFERENCE'), (9, 'DNC'), (7, 'HANGUP'), (2, 'MULTI-CHOICE'), (1, 'PLAY MESSAGE'), (3, 'RATING QUESTION'), (5, 'RECORD MESSAGE'), (10, 'SMS')])),
                ('question', models.CharField(help_text='Example: hotel service rating', max_length=500, verbose_name='question')),
                ('script', models.CharField(help_text='Example: Press a key between 1 to 5, press pound key when done or Hello {first_name} {last_name}, please press a key between 1 to 5', max_length=1000, null=True, blank=True)),
                ('retries', models.IntegerField(default=0, max_length=1, blank=True, help_text='retries until valid input', null=True, verbose_name='retries')),
                ('timeout', models.IntegerField(default=5, max_length=2, blank=True, help_text='timeout in seconds', null=True, verbose_name='timeout')),
                ('key_0', models.CharField(max_length=100, null=True, verbose_name='key 0', blank=True)),
                ('key_1', models.CharField(max_length=100, null=True, verbose_name='key 1', blank=True)),
                ('key_2', models.CharField(max_length=100, null=True, verbose_name='key 2', blank=True)),
                ('key_3', models.CharField(max_length=100, null=True, verbose_name='key 3', blank=True)),
                ('key_4', models.CharField(max_length=100, null=True, verbose_name='key 4', blank=True)),
                ('key_5', models.CharField(max_length=100, null=True, verbose_name='key 5', blank=True)),
                ('key_6', models.CharField(max_length=100, null=True, verbose_name='key 6', blank=True)),
                ('key_7', models.CharField(max_length=100, null=True, verbose_name='key 7', blank=True)),
                ('key_8', models.CharField(max_length=100, null=True, verbose_name='key 8', blank=True)),
                ('key_9', models.CharField(max_length=100, null=True, verbose_name='key 9', blank=True)),
                ('rating_laps', models.IntegerField(default=9, max_length=1, null=True, verbose_name='from 1 to X', blank=True)),
                ('validate_number', models.BooleanField(default=True, verbose_name='check validity')),
                ('number_digits', models.IntegerField(default=b'2', max_length=2, null=True, verbose_name='number of digits', blank=True)),
                ('min_number', models.BigIntegerField(default=0, max_length=50, null=True, verbose_name='minimum', blank=True)),
                ('max_number', models.BigIntegerField(default=99, max_length=50, null=True, verbose_name='maximum', blank=True)),
                ('phonenumber', models.CharField(max_length=50, null=True, verbose_name='Phone Number / SIP URI', blank=True)),
                ('conference', models.CharField(max_length=50, null=True, verbose_name='conference number', blank=True)),
                ('sms_text', models.CharField(help_text='text that will be send via SMS to the contact', max_length=200, null=True, blank=True)),
                ('completed', models.BooleanField(default=False, verbose_name='survey complete')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('audiofile', models.ForeignKey(verbose_name='audio File', blank=True, to='audiofield.AudioFile', null=True)),
                ('invalid_audiofile', models.ForeignKey(related_name='survey_template_invalid_audiofile', verbose_name='audio invalid input', blank=True, to='audiofield.AudioFile', null=True)),
            ],
            options={
                'ordering': ['order', 'survey'],
                'abstract': False,
                'verbose_name': 'section template',
                'verbose_name_plural': 'section templates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=90, verbose_name='name')),
                ('tts_language', django_lets_go.language_field.LanguageField(default=b'en', choices=[(b'aa', 'Afar'), (b'ab', 'Abkhazian'), (b'af', 'Afrikaans'), (b'ak', 'Akan'), (b'sq', 'Albanian'), (b'am', 'Amharic'), (b'ar', 'Arabic'), (b'an', 'Aragonese'), (b'hy', 'Armenian'), (b'as', 'Assamese'), (b'av', 'Avaric'), (b'ae', 'Avestan'), (b'ay', 'Aymara'), (b'az', 'Azerbaijani'), (b'ba', 'Bashkir'), (b'bm', 'Bambara'), (b'eu', 'Basque'), (b'be', 'Belarusian'), (b'bn', 'Bengali'), (b'bh', 'Bihari languages'), (b'bi', 'Bislama'), (b'bo', 'Tibetan'), (b'bs', 'Bosnian'), (b'br', 'Breton'), (b'bg', 'Bulgarian'), (b'my', 'Burmese'), (b'ca', 'Catalan; Valencian'), (b'cs', 'Czech'), (b'ch', 'Chamorro'), (b'ce', 'Chechen'), (b'zh', 'Chinese'), (b'cu', 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic'), (b'cv', 'Chuvash'), (b'kw', 'Cornish'), (b'co', 'Corsican'), (b'cr', 'Cree'), (b'cy', 'Welsh'), (b'cs', 'Czech'), (b'da', 'Danish'), (b'de', 'German'), (b'dv', 'Divehi; Dhivehi; Maldivian'), (b'nl', 'Dutch; Flemish'), (b'dz', 'Dzongkha'), (b'el', 'Greek, Modern (1453-)'), (b'en', 'English'), (b'eo', 'Esperanto'), (b'et', 'Estonian'), (b'eu', 'Basque'), (b'ee', 'Ewe'), (b'fo', 'Faroese'), (b'fa', 'Persian'), (b'fj', 'Fijian'), (b'fi', 'Finnish'), (b'fr', 'French'), (b'fr', 'French'), (b'fy', 'Western Frisian'), (b'ff', 'Fulah'), (b'ka', 'Georgian'), (b'de', 'German'), (b'gd', 'Gaelic; Scottish Gaelic'), (b'ga', 'Irish'), (b'gl', 'Galician'), (b'gv', 'Manx'), (b'el', 'Greek, Modern (1453-)'), (b'gn', 'Guarani'), (b'gu', 'Gujarati'), (b'ht', 'Haitian; Haitian Creole'), (b'ha', 'Hausa'), (b'he', 'Hebrew'), (b'hz', 'Herero'), (b'hi', 'Hindi'), (b'ho', 'Hiri Motu'), (b'hr', 'Croatian'), (b'hu', 'Hungarian'), (b'hy', 'Armenian'), (b'ig', 'Igbo'), (b'is', 'Icelandic'), (b'io', 'Ido'), (b'ii', 'Sichuan Yi; Nuosu'), (b'iu', 'Inuktitut'), (b'ie', 'Interlingue; Occidental'), (b'ia', 'Interlingua (International Auxiliary Language Association)'), (b'id', 'Indonesian'), (b'ik', 'Inupiaq'), (b'is', 'Icelandic'), (b'it', 'Italian'), (b'jv', 'Javanese'), (b'ja', 'Japanese'), (b'kl', 'Kalaallisut; Greenlandic'), (b'kn', 'Kannada'), (b'ks', 'Kashmiri'), (b'ka', 'Georgian'), (b'kr', 'Kanuri'), (b'kk', 'Kazakh'), (b'km', 'Central Khmer'), (b'ki', 'Kikuyu; Gikuyu'), (b'rw', 'Kinyarwanda'), (b'ky', 'Kirghiz; Kyrgyz'), (b'kv', 'Komi'), (b'kg', 'Kongo'), (b'ko', 'Korean'), (b'kj', 'Kuanyama; Kwanyama'), (b'ku', 'Kurdish'), (b'lo', 'Lao'), (b'la', 'Latin'), (b'lv', 'Latvian'), (b'li', 'Limburgan; Limburger; Limburgish'), (b'ln', 'Lingala'), (b'lt', 'Lithuanian'), (b'lb', 'Luxembourgish; Letzeburgesch'), (b'lu', 'Luba-Katanga'), (b'lg', 'Ganda'), (b'mk', 'Macedonian'), (b'mh', 'Marshallese'), (b'ml', 'Malayalam'), (b'mi', 'Maori'), (b'mr', 'Marathi'), (b'ms', 'Malay'), (b'mk', 'Macedonian'), (b'mg', 'Malagasy'), (b'mt', 'Maltese'), (b'mn', 'Mongolian'), (b'mi', 'Maori'), (b'ms', 'Malay'), (b'my', 'Burmese'), (b'na', 'Nauru'), (b'nv', 'Navajo; Navaho'), (b'nr', 'Ndebele, South; South Ndebele'), (b'nd', 'Ndebele, North; North Ndebele'), (b'ng', 'Ndonga'), (b'ne', 'Nepali'), (b'nl', 'Dutch; Flemish'), (b'nn', 'Norwegian Nynorsk; Nynorsk, Norwegian'), (b'nb', 'Bokmal, Norwegian; Norwegian Bokmal'), (b'no', 'Norwegian'), (b'ny', 'Chichewa; Chewa; Nyanja'), (b'oc', 'Occitan (post 1500)'), (b'oj', 'Ojibwa'), (b'or', 'Oriya'), (b'om', 'Oromo'), (b'os', 'Ossetian; Ossetic'), (b'pa', 'Panjabi; Punjabi'), (b'fa', 'Persian'), (b'pi', 'Pali'), (b'pl', 'Polish'), (b'pt', 'Portuguese'), (b'ps', 'Pushto; Pashto'), (b'qu', 'Quechua'), (b'rm', 'Romansh'), (b'ro', 'Romanian; Moldavian; Moldovan'), (b'ro', 'Romanian; Moldavian; Moldovan'), (b'rn', 'Rundi'), (b'ru', 'Russian'), (b'sg', 'Sango'), (b'sa', 'Sanskrit'), (b'si', 'Sinhala; Sinhalese'), (b'sk', 'Slovak'), (b'sk', 'Slovak'), (b'sl', 'Slovenian'), (b'se', 'Northern Sami'), (b'sm', 'Samoan'), (b'sn', 'Shona'), (b'sd', 'Sindhi'), (b'so', 'Somali'), (b'st', 'Sotho, Southern'), (b'es', 'Spanish; Castilian'), (b'sq', 'Albanian'), (b'sc', 'Sardinian'), (b'sr', 'Serbian'), (b'ss', 'Swati'), (b'su', 'Sundanese'), (b'sw', 'Swahili'), (b'sv', 'Swedish'), (b'ty', 'Tahitian'), (b'ta', 'Tamil'), (b'tt', 'Tatar'), (b'te', 'Telugu'), (b'tg', 'Tajik'), (b'tl', 'Tagalog'), (b'th', 'Thai'), (b'bo', 'Tibetan'), (b'ti', 'Tigrinya'), (b'to', 'Tonga (Tonga Islands)'), (b'tn', 'Tswana'), (b'ts', 'Tsonga'), (b'tk', 'Turkmen'), (b'tr', 'Turkish'), (b'tw', 'Twi'), (b'ug', 'Uighur; Uyghur'), (b'uk', 'Ukrainian'), (b'ur', 'Urdu'), (b'uz', 'Uzbek'), (b've', 'Venda'), (b'vi', 'Vietnamese'), (b'vo', 'Volapuk'), (b'cy', 'Welsh'), (b'wa', 'Walloon'), (b'wo', 'Wolof'), (b'xh', 'Xhosa'), (b'yi', 'Yiddish'), (b'yo', 'Yoruba'), (b'za', 'Zhuang; Chuang'), (b'zh', 'Chinese'), (b'zu', 'Zulu')], max_length=2, blank=True, null=True, verbose_name='Text-to-Speech language')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('campaign', models.ForeignKey(verbose_name='campaign', blank=True, to='dialer_campaign.Campaign', null=True)),
                ('user', models.ForeignKey(related_name='survey_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'survey',
                'verbose_name_plural': 'surveys',
                'permissions': (('view_survey', 'can see survey'), ('view_sealed_survey', 'can see sealed survey'), ('seal_survey', 'can seal survey'), ('export_survey', 'can export survey'), ('import_survey', 'can import survey'), ('view_survey_report', 'can see survey report')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Survey_template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=90, verbose_name='name')),
                ('tts_language', django_lets_go.language_field.LanguageField(default=b'en', choices=[(b'aa', 'Afar'), (b'ab', 'Abkhazian'), (b'af', 'Afrikaans'), (b'ak', 'Akan'), (b'sq', 'Albanian'), (b'am', 'Amharic'), (b'ar', 'Arabic'), (b'an', 'Aragonese'), (b'hy', 'Armenian'), (b'as', 'Assamese'), (b'av', 'Avaric'), (b'ae', 'Avestan'), (b'ay', 'Aymara'), (b'az', 'Azerbaijani'), (b'ba', 'Bashkir'), (b'bm', 'Bambara'), (b'eu', 'Basque'), (b'be', 'Belarusian'), (b'bn', 'Bengali'), (b'bh', 'Bihari languages'), (b'bi', 'Bislama'), (b'bo', 'Tibetan'), (b'bs', 'Bosnian'), (b'br', 'Breton'), (b'bg', 'Bulgarian'), (b'my', 'Burmese'), (b'ca', 'Catalan; Valencian'), (b'cs', 'Czech'), (b'ch', 'Chamorro'), (b'ce', 'Chechen'), (b'zh', 'Chinese'), (b'cu', 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic'), (b'cv', 'Chuvash'), (b'kw', 'Cornish'), (b'co', 'Corsican'), (b'cr', 'Cree'), (b'cy', 'Welsh'), (b'cs', 'Czech'), (b'da', 'Danish'), (b'de', 'German'), (b'dv', 'Divehi; Dhivehi; Maldivian'), (b'nl', 'Dutch; Flemish'), (b'dz', 'Dzongkha'), (b'el', 'Greek, Modern (1453-)'), (b'en', 'English'), (b'eo', 'Esperanto'), (b'et', 'Estonian'), (b'eu', 'Basque'), (b'ee', 'Ewe'), (b'fo', 'Faroese'), (b'fa', 'Persian'), (b'fj', 'Fijian'), (b'fi', 'Finnish'), (b'fr', 'French'), (b'fr', 'French'), (b'fy', 'Western Frisian'), (b'ff', 'Fulah'), (b'ka', 'Georgian'), (b'de', 'German'), (b'gd', 'Gaelic; Scottish Gaelic'), (b'ga', 'Irish'), (b'gl', 'Galician'), (b'gv', 'Manx'), (b'el', 'Greek, Modern (1453-)'), (b'gn', 'Guarani'), (b'gu', 'Gujarati'), (b'ht', 'Haitian; Haitian Creole'), (b'ha', 'Hausa'), (b'he', 'Hebrew'), (b'hz', 'Herero'), (b'hi', 'Hindi'), (b'ho', 'Hiri Motu'), (b'hr', 'Croatian'), (b'hu', 'Hungarian'), (b'hy', 'Armenian'), (b'ig', 'Igbo'), (b'is', 'Icelandic'), (b'io', 'Ido'), (b'ii', 'Sichuan Yi; Nuosu'), (b'iu', 'Inuktitut'), (b'ie', 'Interlingue; Occidental'), (b'ia', 'Interlingua (International Auxiliary Language Association)'), (b'id', 'Indonesian'), (b'ik', 'Inupiaq'), (b'is', 'Icelandic'), (b'it', 'Italian'), (b'jv', 'Javanese'), (b'ja', 'Japanese'), (b'kl', 'Kalaallisut; Greenlandic'), (b'kn', 'Kannada'), (b'ks', 'Kashmiri'), (b'ka', 'Georgian'), (b'kr', 'Kanuri'), (b'kk', 'Kazakh'), (b'km', 'Central Khmer'), (b'ki', 'Kikuyu; Gikuyu'), (b'rw', 'Kinyarwanda'), (b'ky', 'Kirghiz; Kyrgyz'), (b'kv', 'Komi'), (b'kg', 'Kongo'), (b'ko', 'Korean'), (b'kj', 'Kuanyama; Kwanyama'), (b'ku', 'Kurdish'), (b'lo', 'Lao'), (b'la', 'Latin'), (b'lv', 'Latvian'), (b'li', 'Limburgan; Limburger; Limburgish'), (b'ln', 'Lingala'), (b'lt', 'Lithuanian'), (b'lb', 'Luxembourgish; Letzeburgesch'), (b'lu', 'Luba-Katanga'), (b'lg', 'Ganda'), (b'mk', 'Macedonian'), (b'mh', 'Marshallese'), (b'ml', 'Malayalam'), (b'mi', 'Maori'), (b'mr', 'Marathi'), (b'ms', 'Malay'), (b'mk', 'Macedonian'), (b'mg', 'Malagasy'), (b'mt', 'Maltese'), (b'mn', 'Mongolian'), (b'mi', 'Maori'), (b'ms', 'Malay'), (b'my', 'Burmese'), (b'na', 'Nauru'), (b'nv', 'Navajo; Navaho'), (b'nr', 'Ndebele, South; South Ndebele'), (b'nd', 'Ndebele, North; North Ndebele'), (b'ng', 'Ndonga'), (b'ne', 'Nepali'), (b'nl', 'Dutch; Flemish'), (b'nn', 'Norwegian Nynorsk; Nynorsk, Norwegian'), (b'nb', 'Bokmal, Norwegian; Norwegian Bokmal'), (b'no', 'Norwegian'), (b'ny', 'Chichewa; Chewa; Nyanja'), (b'oc', 'Occitan (post 1500)'), (b'oj', 'Ojibwa'), (b'or', 'Oriya'), (b'om', 'Oromo'), (b'os', 'Ossetian; Ossetic'), (b'pa', 'Panjabi; Punjabi'), (b'fa', 'Persian'), (b'pi', 'Pali'), (b'pl', 'Polish'), (b'pt', 'Portuguese'), (b'ps', 'Pushto; Pashto'), (b'qu', 'Quechua'), (b'rm', 'Romansh'), (b'ro', 'Romanian; Moldavian; Moldovan'), (b'ro', 'Romanian; Moldavian; Moldovan'), (b'rn', 'Rundi'), (b'ru', 'Russian'), (b'sg', 'Sango'), (b'sa', 'Sanskrit'), (b'si', 'Sinhala; Sinhalese'), (b'sk', 'Slovak'), (b'sk', 'Slovak'), (b'sl', 'Slovenian'), (b'se', 'Northern Sami'), (b'sm', 'Samoan'), (b'sn', 'Shona'), (b'sd', 'Sindhi'), (b'so', 'Somali'), (b'st', 'Sotho, Southern'), (b'es', 'Spanish; Castilian'), (b'sq', 'Albanian'), (b'sc', 'Sardinian'), (b'sr', 'Serbian'), (b'ss', 'Swati'), (b'su', 'Sundanese'), (b'sw', 'Swahili'), (b'sv', 'Swedish'), (b'ty', 'Tahitian'), (b'ta', 'Tamil'), (b'tt', 'Tatar'), (b'te', 'Telugu'), (b'tg', 'Tajik'), (b'tl', 'Tagalog'), (b'th', 'Thai'), (b'bo', 'Tibetan'), (b'ti', 'Tigrinya'), (b'to', 'Tonga (Tonga Islands)'), (b'tn', 'Tswana'), (b'ts', 'Tsonga'), (b'tk', 'Turkmen'), (b'tr', 'Turkish'), (b'tw', 'Twi'), (b'ug', 'Uighur; Uyghur'), (b'uk', 'Ukrainian'), (b'ur', 'Urdu'), (b'uz', 'Uzbek'), (b've', 'Venda'), (b'vi', 'Vietnamese'), (b'vo', 'Volapuk'), (b'cy', 'Welsh'), (b'wa', 'Walloon'), (b'wo', 'Wolof'), (b'xh', 'Xhosa'), (b'yi', 'Yiddish'), (b'yo', 'Yoruba'), (b'za', 'Zhuang; Chuang'), (b'zh', 'Chinese'), (b'zu', 'Zulu')], max_length=2, blank=True, null=True, verbose_name='Text-to-Speech language')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(related_name='survey_template_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'survey template',
                'verbose_name_plural': 'survey templates',
                'permissions': (('view_survey_template', 'can see survey template'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='section_template',
            name='survey',
            field=models.ForeignKey(verbose_name='survey', to='survey.Survey_template'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='survey',
            field=models.ForeignKey(verbose_name='survey', to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resultaggregate',
            name='section',
            field=models.ForeignKey(related_name='ResultSum Section', to='survey.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resultaggregate',
            name='survey',
            field=models.ForeignKey(related_name='ResultSum Survey', to='survey.Survey'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='resultaggregate',
            unique_together=set([('survey', 'section', 'response')]),
        ),
        migrations.AddField(
            model_name='result',
            name='section',
            field=models.ForeignKey(related_name='Result Section', to='survey.Section'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='result',
            unique_together=set([('callrequest', 'section')]),
        ),
        migrations.AddField(
            model_name='branching_template',
            name='goto',
            field=models.ForeignKey(related_name='Goto Template Section', blank=True, to='survey.Section_template', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='branching_template',
            name='section',
            field=models.ForeignKey(related_name='Branching Template Section', to='survey.Section_template'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='branching_template',
            unique_together=set([('keys', 'section')]),
        ),
        migrations.AddField(
            model_name='branching',
            name='goto',
            field=models.ForeignKey(related_name='Goto Section', blank=True, to='survey.Section', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='branching',
            name='section',
            field=models.ForeignKey(related_name='Branching Section', to='survey.Section'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='branching',
            unique_together=set([('keys', 'section')]),
        ),
    ]
