# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SurveyApp'
        db.create_table('survey_surveyapp', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=1, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=90)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owner', to=orm['auth.User'])),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('survey', ['SurveyApp'])

        # Adding model 'SurveyQuestion'
        db.create_table('survey_surveyquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=1, db_index=True)),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('tags', self.gf('tagging.fields.TagField')(max_length=1000)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Survey owner', to=orm['auth.User'])),
            ('surveyapp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.SurveyApp'])),
            ('audio_message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audiofield.AudioFile'], null=True, blank=True)),
            ('message_type', self.gf('django.db.models.fields.IntegerField')(default='1', max_length=20, null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('survey', ['SurveyQuestion'])

        # Adding model 'SurveyResponse'
        db.create_table('survey_surveyresponse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('keyvalue', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('surveyquestion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='SurveyQuestion', to=orm['survey.SurveyQuestion'])),
            ('goto_surveyquestion', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='Goto SurveyQuestion', null=True, to=orm['survey.SurveyQuestion'])),
        ))
        db.send_create_signal('survey', ['SurveyResponse'])

        # Adding unique constraint on 'SurveyResponse', fields ['key', 'surveyquestion']
        db.create_unique('survey_surveyresponse', ['key', 'surveyquestion_id'])

        # Adding model 'SurveyCampaignResult'
        db.create_table('survey_surveycampaignresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_campaign.Campaign'], null=True, blank=True)),
            ('surveyapp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='SurveyApp', to=orm['survey.SurveyApp'])),
            ('callid', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('response', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('survey', ['SurveyCampaignResult'])


    def backwards(self, orm):
        # Removing unique constraint on 'SurveyResponse', fields ['key', 'surveyquestion']
        db.delete_unique('survey_surveyresponse', ['key', 'surveyquestion_id'])

        # Deleting model 'SurveyApp'
        db.delete_table('survey_surveyapp')

        # Deleting model 'SurveyQuestion'
        db.delete_table('survey_surveyquestion')

        # Deleting model 'SurveyResponse'
        db.delete_table('survey_surveyresponse')

        # Deleting model 'SurveyCampaignResult'
        db.delete_table('survey_surveycampaignresult')


    models = {
        'audiofield.audiofile': {
            'Meta': {'object_name': 'AudioFile', 'db_table': "u'audio_file'"},
            'audio_file': ('audiofield.fields.AudioField', [], {'ext_whitelist': '(".mp3", ".wav", ".ogg")', 'upload_to': '"upload/audiofiles"', 'blank': 'True'}),
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
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'callmaxduration': ('django.db.models.fields.IntegerField', [], {'default': "'1800'", 'null': 'True', 'blank': 'True'}),
            'calltimeout': ('django.db.models.fields.IntegerField', [], {'default': "'45'", 'null': 'True', 'blank': 'True'}),
            'campaign_code': ('django.db.models.fields.CharField', [], {'default': "'NDISB'", 'unique': 'True', 'max_length': '20', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'daily_start_time': ('django.db.models.fields.TimeField', [], {'default': "'00:00:00'"}),
            'daily_stop_time': ('django.db.models.fields.TimeField', [], {'default': "'23:59:59'"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expirationdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 5, 0, 0)'}),
            'extra_data': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {'default': "'10'", 'null': 'True', 'blank': 'True'}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_phonebook': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'}),
            'intervalretry': ('django.db.models.fields.IntegerField', [], {'default': "'300'", 'null': 'True', 'blank': 'True'}),
            'maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'phonebook': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['dialer_campaign.Phonebook']", 'null': 'True', 'blank': 'True'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'startingdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 5, 0, 0)'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'2'", 'null': 'True', 'blank': 'True'}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Campaign owner'", 'to': "orm['auth.User']"}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'dialer_campaign.phonebook': {
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
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.surveyapp': {
            'Meta': {'object_name': 'SurveyApp'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': "orm['auth.User']"})
        },
        'survey.surveycampaignresult': {
            'Meta': {'object_name': 'SurveyCampaignResult'},
            'callid': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'response': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'surveyapp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'SurveyApp'", 'to': "orm['survey.SurveyApp']"})
        },
        'survey.surveyquestion': {
            'Meta': {'ordering': "['order', 'surveyapp']", 'object_name': 'SurveyQuestion'},
            'audio_message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['audiofield.AudioFile']", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_type': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'surveyapp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyApp']"}),
            'tags': ('tagging.fields.TagField', [], {'max_length': '1000'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Survey owner'", 'to': "orm['auth.User']"})
        },
        'survey.surveyresponse': {
            'Meta': {'unique_together': "(('key', 'surveyquestion'),)", 'object_name': 'SurveyResponse'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'goto_surveyquestion': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'Goto SurveyQuestion'", 'null': 'True', 'to': "orm['survey.SurveyQuestion']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'keyvalue': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'surveyquestion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'SurveyQuestion'", 'to': "orm['survey.SurveyQuestion']"}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['survey']