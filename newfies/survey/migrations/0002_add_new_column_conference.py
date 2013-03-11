# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Section.conference'
        db.add_column('survey_section', 'conference',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Section_template.conference'
        db.add_column('survey_section_template', 'conference',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Section.conference'
        db.delete_column('survey_section', 'conference')

        # Deleting field 'Section_template.conference'
        db.delete_column('survey_section_template', 'conference')


    models = {
        'audiofield.audiofile': {
            'Meta': {'object_name': 'AudioFile', 'db_table': "u'audio_file'"},
            'audio_file': ('audiofield.fields.AudioField', [], {'ext_whitelist': "['.mp3', '.wav', '.ogg']", 'max_length': '100', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dialer_campaign.campaign': {
            'Meta': {'object_name': 'Campaign', 'db_table': "u'dialer_campaign'"},
            'aleg_gateway': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'A-Leg Gateway'", 'to': "orm['dialer_gateway.Gateway']"}),
            'amd_behavior': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'caller_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'callmaxduration': ('django.db.models.fields.IntegerField', [], {'default': "'1800'", 'null': 'True', 'blank': 'True'}),
            'calltimeout': ('django.db.models.fields.IntegerField', [], {'default': "'45'", 'null': 'True', 'blank': 'True'}),
            'campaign_code': ('django.db.models.fields.CharField', [], {'default': "'CRJIF'", 'unique': 'True', 'max_length': '20', 'blank': 'True'}),
            'completed': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'completion_intervalretry': ('django.db.models.fields.IntegerField', [], {'default': "'900'", 'null': 'True', 'blank': 'True'}),
            'completion_maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'daily_start_time': ('django.db.models.fields.TimeField', [], {'default': "'00:00:00'"}),
            'daily_stop_time': ('django.db.models.fields.TimeField', [], {'default': "'23:59:59'"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expirationdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 3, 12, 0, 0)'}),
            'extra_data': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {'default': "'10'", 'null': 'True', 'blank': 'True'}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'has_been_duplicated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_been_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_phonebook': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'intervalretry': ('django.db.models.fields.IntegerField', [], {'default': "'300'", 'null': 'True', 'blank': 'True'}),
            'maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'phonebook': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['dialer_contact.Phonebook']", 'null': 'True', 'blank': 'True'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'startingdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 3, 11, 0, 0)'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2', 'null': 'True', 'blank': 'True'}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'totalcontact': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Campaign owner'", 'to': "orm['auth.User']"}),
            'voicemail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'voicemail_audiofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['audiofield.AudioFile']", 'null': 'True', 'blank': 'True'}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'dialer_campaign.subscriber': {
            'Meta': {'unique_together': "(['contact', 'campaign'],)", 'object_name': 'Subscriber', 'db_table': "u'dialer_subscriber'"},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'completion_count_attempt': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_contact.Contact']", 'null': 'True', 'blank': 'True'}),
            'count_attempt': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duplicate_contact': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        'dialer_cdr.callrequest': {
            'Meta': {'object_name': 'Callrequest', 'db_table': "u'dialer_callrequest'"},
            'aleg_gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_gateway.Gateway']", 'null': 'True', 'blank': 'True'}),
            'aleg_uuid': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'call_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 3, 11, 0, 0)'}),
            'call_type': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'extra_data': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'extra_dial_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'hangup_cause': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'num_attempt': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent_callrequest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_cdr.Callrequest']", 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'request_uuid': ('django.db.models.fields.CharField', [], {'default': "'58f52fc4-8a3b-11e2-88b4-00231470a30c'", 'max_length': '120', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '180', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Subscriber']", 'null': 'True', 'blank': 'True'}),
            'timelimit': ('django.db.models.fields.IntegerField', [], {'default': '3600', 'blank': 'True'}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'default': '30', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'dialer_contact.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "u'dialer_contact'"},
            'additional_vars': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'phonebook': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_contact.Phonebook']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dialer_contact.phonebook': {
            'Meta': {'object_name': 'Phonebook', 'db_table': "u'dialer_phonebook'"},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Phonebook owner'", 'to': "orm['auth.User']"})
        },
        'dialer_gateway.gateway': {
            'Meta': {'object_name': 'Gateway', 'db_table': "u'dialer_gateway'"},
            'addparameter': ('django.db.models.fields.CharField', [], {'max_length': '360', 'blank': 'True'}),
            'addprefix': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'count_call': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'count_in_use': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'failover': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'Failover Gateway'", 'null': 'True', 'to': "orm['dialer_gateway.Gateway']"}),
            'gateway_codecs': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gateway_retries': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gateway_timeouts': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'gateways': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_call': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'originate_dial_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'removeprefix': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'secondused': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.branching': {
            'Meta': {'unique_together': "(('keys', 'section'),)", 'object_name': 'Branching'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'goto': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'Goto Section'", 'null': 'True', 'to': "orm['survey.Section']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keys': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Branching Section'", 'to': "orm['survey.Section']"}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.branching_template': {
            'Meta': {'unique_together': "(('keys', 'section'),)", 'object_name': 'Branching_template'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'goto': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'Goto Template Section'", 'null': 'True', 'to': "orm['survey.Section_template']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keys': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Branching Template Section'", 'to': "orm['survey.Section_template']"}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.result': {
            'Meta': {'unique_together': "(('callrequest', 'section'),)", 'object_name': 'Result'},
            'callrequest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey_callrequest'", 'null': 'True', 'to': "orm['dialer_cdr.Callrequest']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'record_file': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'recording_duration': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Result Section'", 'to': "orm['survey.Section']"})
        },
        'survey.resultaggregate': {
            'Meta': {'unique_together': "(('campaign', 'survey', 'section', 'response'),)", 'object_name': 'ResultAggregate'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '20'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ResultSum Section'", 'to': "orm['survey.Section']"}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ResultSum Survey'", 'to': "orm['survey.Survey']"})
        },
        'survey.section': {
            'Meta': {'ordering': "['order', 'survey']", 'object_name': 'Section'},
            'audiofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['audiofield.AudioFile']", 'null': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'conference': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid_audiofile': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey_invalid_audiofile'", 'null': 'True', 'to': "orm['audiofield.AudioFile']"}),
            'key_0': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_3': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_4': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_5': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_6': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_7': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_8': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_9': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_number': ('django.db.models.fields.BigIntegerField', [], {'default': '99', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'min_number': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'number_digits': ('django.db.models.fields.IntegerField', [], {'default': "'2'", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'phonenumber': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'rating_laps': ('django.db.models.fields.IntegerField', [], {'default': '9', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'retries': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'script': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'section_template': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Survey']"}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'default': '5', 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'validate_number': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'survey.section_template': {
            'Meta': {'ordering': "['order', 'survey']", 'object_name': 'Section_template'},
            'audiofile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['audiofield.AudioFile']", 'null': 'True', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'conference': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invalid_audiofile': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'survey_template_invalid_audiofile'", 'null': 'True', 'to': "orm['audiofield.AudioFile']"}),
            'key_0': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_3': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_4': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_5': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_6': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_7': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_8': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'key_9': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'max_number': ('django.db.models.fields.BigIntegerField', [], {'default': '99', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'min_number': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'number_digits': ('django.db.models.fields.IntegerField', [], {'default': "'2'", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'phonenumber': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'rating_laps': ('django.db.models.fields.IntegerField', [], {'default': '9', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'retries': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'script': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Survey_template']"}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'default': '5', 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'validate_number': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'survey.survey': {
            'Meta': {'object_name': 'Survey'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'tts_language': ('common.language_field.LanguageField', [], {'default': "'en'", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'survey_user'", 'to': "orm['auth.User']"})
        },
        'survey.survey_template': {
            'Meta': {'object_name': 'Survey_template'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'tts_language': ('common.language_field.LanguageField', [], {'default': "'en'", 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'survey_template_user'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['survey']