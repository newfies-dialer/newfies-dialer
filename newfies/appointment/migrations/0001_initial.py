# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CalendarSetting'
        db.create_table('calendar_setting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('callerid', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('caller_name', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('call_timeout', self.gf('django.db.models.fields.IntegerField')(default='60')),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='manager_user', to=orm['auth.User'])),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(related_name='calendar_survey', to=orm['survey.Survey'])),
            ('aleg_gateway', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_gateway.Gateway'])),
            ('sms_gateway', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sms_gateway', to=orm['sms.Gateway'])),
            ('voicemail', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('amd_behavior', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('voicemail_audiofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audiofield.AudioFile'], null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('appointment', ['CalendarSetting'])

        # Adding model 'CalendarUserProfile'
        db.create_table('calendar_user_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('country', self.gf('django_countries.fields.CountryField')(max_length=2, null=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('phone_no', self.gf('django.db.models.fields.CharField')(max_length=90, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=90, null=True, blank=True)),
            ('company_name', self.gf('django.db.models.fields.CharField')(max_length=90, null=True, blank=True)),
            ('company_website', self.gf('django.db.models.fields.URLField')(max_length=90, null=True, blank=True)),
            ('language', self.gf('common.language_field.LanguageField')(max_length=2, null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('accountcode', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('manager', self.gf('django.db.models.fields.related.ForeignKey')(related_name='manager_of_calendar_user', to=orm['auth.User'])),
            ('calendar_setting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['appointment.CalendarSetting'])),
        ))
        db.send_create_signal('appointment', ['CalendarUserProfile'])

        # Adding model 'Calendar'
        db.create_table(u'appointment_calendar', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='calendar user', null=True, to=orm['auth.User'])),
            ('max_concurrent', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('appointment', ['Calendar'])

        # Adding model 'Rule'
        db.create_table(u'appointment_rule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('frequency', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('params', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('appointment', ['Rule'])

        # Adding model 'Event'
        db.create_table(u'appointment_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 12, 9, 0, 0))),
            ('end', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 12, 9, 0, 0))),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='creator', to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end_recurring_period', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 1, 9, 0, 0), null=True, blank=True)),
            ('rule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['appointment.Rule'], null=True, blank=True)),
            ('calendar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['appointment.Calendar'])),
            ('notify_count', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('data', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('parent_event', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='parent event', null=True, to=orm['appointment.Event'])),
            ('occ_count', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('appointment', ['Event'])

        # Adding model 'Occurrence'
        db.create_table(u'appointment_occurrence', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['appointment.Event'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('cancelled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('original_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('original_end', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('appointment', ['Occurrence'])

        # Adding model 'Alarm'
        db.create_table(u'appointment_alarm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alarm_phonenumber', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('alarm_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('daily_start', self.gf('django.db.models.fields.TimeField')(default='00:00:00')),
            ('daily_stop', self.gf('django.db.models.fields.TimeField')(default='23:59:59')),
            ('advance_notice', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('maxretry', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('retry_delay', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('num_attempt', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('method', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='survey', null=True, to=orm['survey.Survey'])),
            ('mail_template', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='mail template', null=True, to=orm['mod_mailer.MailTemplate'])),
            ('sms_template', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sms template', null=True, to=orm['sms_module.SMSTemplate'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='event', to=orm['appointment.Event'])),
            ('date_start_notice', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 12, 9, 0, 0))),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('result', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('url_cancel', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('url_confirm', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('phonenumber_transfer', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('phonenumber_sms_failure', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('appointment', ['Alarm'])

        # Adding model 'AlarmRequest'
        db.create_table(u'appointment_alarmrequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alarm', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='request_alarm', null=True, to=orm['appointment.Alarm'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('callstatus', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('callrequest', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='callrequest_alarm', null=True, to=orm['dialer_cdr.Callrequest'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('appointment', ['AlarmRequest'])

    def backwards(self, orm):
        # Deleting model 'CalendarSetting'
        db.delete_table('calendar_setting')

        # Deleting model 'CalendarUserProfile'
        db.delete_table('calendar_user_profile')

        # Deleting model 'Calendar'
        db.delete_table(u'appointment_calendar')

        # Deleting model 'Rule'
        db.delete_table(u'appointment_rule')

        # Deleting model 'Event'
        db.delete_table(u'appointment_event')

        # Deleting model 'Occurrence'
        db.delete_table(u'appointment_occurrence')

        # Deleting model 'Alarm'
        db.delete_table(u'appointment_alarm')

        # Deleting model 'AlarmRequest'
        db.delete_table(u'appointment_alarmrequest')

    models = {
        'appointment.alarm': {
            'Meta': {'object_name': 'Alarm'},
            'advance_notice': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'alarm_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'alarm_phonenumber': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'daily_start': ('django.db.models.fields.TimeField', [], {'default': "'00:00:00'"}),
            'daily_stop': ('django.db.models.fields.TimeField', [], {'default': "'23:59:59'"}),
            'date_start_notice': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 12, 9, 0, 0)'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event'", 'to': "orm['appointment.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_template': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'mail template'", 'null': 'True', 'to': u"orm['mod_mailer.MailTemplate']"}),
            'maxretry': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'method': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'num_attempt': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'phonenumber_sms_failure': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phonenumber_transfer': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'retry_delay': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'sms_template': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sms template'", 'null': 'True', 'to': u"orm['sms_module.SMSTemplate']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey'", 'null': 'True', 'to': u"orm['survey.Survey']"}),
            'url_cancel': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'url_confirm': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'})
        },
        'appointment.alarmrequest': {
            'Meta': {'object_name': 'AlarmRequest'},
            'alarm': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'request_alarm'", 'null': 'True', 'to': "orm['appointment.Alarm']"}),
            'callrequest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'callrequest_alarm'", 'null': 'True', 'to': u"orm['dialer_cdr.Callrequest']"}),
            'callstatus': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'})
        },
        'appointment.calendar': {
            'Meta': {'object_name': 'Calendar'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_concurrent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar user'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        'appointment.calendarsetting': {
            'Meta': {'object_name': 'CalendarSetting', 'db_table': "'calendar_setting'"},
            'aleg_gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_gateway.Gateway']"}),
            'amd_behavior': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'call_timeout': ('django.db.models.fields.IntegerField', [], {'default': "'60'"}),
            'caller_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'sms_gateway': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sms_gateway'", 'to': "orm['sms.Gateway']"}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'calendar_survey'", 'to': u"orm['survey.Survey']"}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'manager_user'", 'to': u"orm['auth.User']"}),
            'voicemail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'voicemail_audiofile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audiofield.AudioFile']", 'null': 'True', 'blank': 'True'})
        },
        'appointment.calendaruserprofile': {
            'Meta': {'object_name': 'CalendarUserProfile', 'db_table': "'calendar_user_profile'"},
            'accountcode': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'calendar_setting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['appointment.CalendarSetting']"}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '90', 'null': 'True', 'blank': 'True'}),
            'company_website': ('django.db.models.fields.URLField', [], {'max_length': '90', 'null': 'True', 'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '90', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('common.language_field.LanguageField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'manager_of_calendar_user'", 'to': u"orm['auth.User']"}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'phone_no': ('django.db.models.fields.CharField', [], {'max_length': '90', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'})
        },
        'appointment.event': {
            'Meta': {'object_name': 'Event'},
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['appointment.Calendar']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'creator'", 'to': u"orm['auth.User']"}),
            'data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 12, 9, 0, 0)'}),
            'end_recurring_period': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 9, 0, 0)', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notify_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'occ_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'parent_event': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'parent event'", 'null': 'True', 'to': "orm['appointment.Event']"}),
            'rule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['appointment.Rule']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 12, 9, 0, 0)'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'appointment.occurrence': {
            'Meta': {'object_name': 'Occurrence'},
            'cancelled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['appointment.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_end': ('django.db.models.fields.DateTimeField', [], {}),
            'original_start': ('django.db.models.fields.DateTimeField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'appointment.rule': {
            'Meta': {'object_name': 'Rule'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'params': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'audiofield.audiofile': {
            'Meta': {'object_name': 'AudioFile', 'db_table': "u'audio_file'"},
            'audio_file': ('audiofield.fields.AudioField', [], {'ext_whitelist': "['.mp3', '.wav', '.ogg']", 'max_length': '100', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dialer_campaign.campaign': {
            'Meta': {'object_name': 'Campaign', 'db_table': "u'dialer_campaign'"},
            'agent_script': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'aleg_gateway': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'A-Leg Gateway'", 'to': u"orm['dialer_gateway.Gateway']"}),
            'amd_behavior': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'caller_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'callmaxduration': ('django.db.models.fields.IntegerField', [], {'default': "'1800'", 'null': 'True', 'blank': 'True'}),
            'calltimeout': ('django.db.models.fields.IntegerField', [], {'default': "'45'", 'null': 'True', 'blank': 'True'}),
            'campaign_code': ('django.db.models.fields.CharField', [], {'default': "'ZZBQT'", 'unique': 'True', 'max_length': '20', 'blank': 'True'}),
            'completed': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'completion_intervalretry': ('django.db.models.fields.IntegerField', [], {'default': "'900'", 'null': 'True', 'blank': 'True'}),
            'completion_maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'daily_start_time': ('django.db.models.fields.TimeField', [], {'default': "'00:00:00'"}),
            'daily_stop_time': ('django.db.models.fields.TimeField', [], {'default': "'23:59:59'"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dnc': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'DNC'", 'null': 'True', 'to': u"orm['dnc.DNC']"}),
            'expirationdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 12, 10, 0, 0)'}),
            'external_link': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'extra_data': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {'default': "'10'", 'null': 'True', 'blank': 'True'}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'has_been_duplicated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_been_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_phonebook': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'intervalretry': ('django.db.models.fields.IntegerField', [], {'default': "'300'", 'null': 'True', 'blank': 'True'}),
            'lead_disposition': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'phonebook': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['dialer_contact.Phonebook']", 'null': 'True', 'blank': 'True'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sms_gateway': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'campaign_sms_gateway'", 'null': 'True', 'to': "orm['sms.Gateway']"}),
            'startingdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 12, 9, 0, 0)'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2', 'null': 'True', 'blank': 'True'}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'totalcontact': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Campaign owner'", 'to': u"orm['auth.User']"}),
            'voicemail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'voicemail_audiofile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['audiofield.AudioFile']", 'null': 'True', 'blank': 'True'}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'dialer_campaign.subscriber': {
            'Meta': {'unique_together': "(['contact', 'campaign'],)", 'object_name': 'Subscriber', 'db_table': "u'dialer_subscriber'"},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'agent'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'collected_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'completion_count_attempt': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_contact.Contact']", 'null': 'True', 'blank': 'True'}),
            'count_attempt': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'disposition': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'duplicate_contact': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        u'dialer_cdr.callrequest': {
            'Meta': {'object_name': 'Callrequest', 'db_table': "u'dialer_callrequest'"},
            'alarm_request_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'aleg_gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_gateway.Gateway']", 'null': 'True', 'blank': 'True'}),
            'aleg_uuid': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'call_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 12, 9, 0, 0)'}),
            'call_type': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'caller_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'extra_data': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'extra_dial_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'hangup_cause': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'num_attempt': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent_callrequest': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_cdr.Callrequest']", 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'request_uuid': ('django.db.models.fields.CharField', [], {'default': "'d7a4c0cc-606a-11e3-b387-00231470a30c'", 'max_length': '120', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '180', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_campaign.Subscriber']", 'null': 'True', 'blank': 'True'}),
            'timelimit': ('django.db.models.fields.IntegerField', [], {'default': '3600', 'blank': 'True'}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'default': '30', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'dialer_contact.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "u'dialer_contact'"},
            'additional_vars': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'phonebook': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_contact.Phonebook']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'unit_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dialer_contact.phonebook': {
            'Meta': {'object_name': 'Phonebook', 'db_table': "u'dialer_phonebook'"},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Phonebook owner'", 'to': u"orm['auth.User']"})
        },
        u'dialer_gateway.gateway': {
            'Meta': {'object_name': 'Gateway', 'db_table': "u'dialer_gateway'"},
            'addparameter': ('django.db.models.fields.CharField', [], {'max_length': '360', 'blank': 'True'}),
            'addprefix': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'count_call': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'count_in_use': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'failover': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'Failover Gateway'", 'null': 'True', 'to': u"orm['dialer_gateway.Gateway']"}),
            'gateway_codecs': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gateway_retries': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gateway_timeouts': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gateways': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_call': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'originate_dial_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'removeprefix': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'secondused': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'dnc.dnc': {
            'Meta': {'object_name': 'DNC', 'db_table': "'dnc_list'"},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'DNC owner'", 'to': u"orm['auth.User']"})
        },
        u'mod_mailer.mailtemplate': {
            'Meta': {'object_name': 'MailTemplate'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'from_name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'message_html': ('django.db.models.fields.TextField', [], {'max_length': '5000'}),
            'message_plaintext': ('django.db.models.fields.TextField', [], {'max_length': '5000'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'template_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'sms.gateway': {
            'Meta': {'object_name': 'Gateway'},
            'base_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'charge_keyword': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'content_keyword': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'recipient_keyword': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'reply_content': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reply_date': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reply_date_format': ('django.db.models.fields.CharField', [], {'default': "'%Y-%m-%d %H:%M:%S'", 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'reply_sender': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'settings': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'status_date': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'status_date_format': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'status_error_code': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'status_mapping': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'status_msg_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'status_status': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'success_format': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'uuid_keyword': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'sms_module.smstemplate': {
            'Meta': {'object_name': 'SMSTemplate', 'db_table': "u'sms_template'"},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'sender_phonenumber': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'sms_text': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'template_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'survey.survey': {
            'Meta': {'object_name': 'Survey'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'tts_language': ('common.language_field.LanguageField', [], {'default': "'en'", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'survey_user'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['appointment']
