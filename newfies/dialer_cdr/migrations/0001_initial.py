# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Callrequest'
        db.create_table(u'dialer_callrequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('request_uuid', self.gf('django.db.models.fields.CharField')(default='9044872e-6067-11e3-a48e-00231470a30c', max_length=120, null=True, db_index=True, blank=True)),
            ('aleg_uuid', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('call_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 12, 9, 0, 0))),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('call_type', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, db_index=True, blank=True)),
            ('callerid', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('timeout', self.gf('django.db.models.fields.IntegerField')(default=30, blank=True)),
            ('timelimit', self.gf('django.db.models.fields.IntegerField')(default=3600, blank=True)),
            ('extra_dial_string', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('subscriber', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_campaign.Subscriber'], null=True, blank=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_campaign.Campaign'], null=True, blank=True)),
            ('aleg_gateway', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_gateway.Gateway'], null=True, blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('extra_data', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('num_attempt', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_attempt_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=180, blank=True)),
            ('hangup_cause', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('parent_callrequest', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_cdr.Callrequest'], null=True, blank=True)),
        ))
        db.send_create_signal(u'dialer_cdr', ['Callrequest'])

        # Adding model 'VoIPCall'
        db.create_table('dialer_cdr', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Call Sender', to=orm['auth.User'])),
            ('request_uuid', self.gf('django.db.models.fields.CharField')(default='904536ce-6067-11e3-a48e-00231470a30c', max_length=120, null=True, blank=True)),
            ('used_gateway', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_gateway.Gateway'], null=True, blank=True)),
            ('callrequest', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_cdr.Callrequest'], null=True, blank=True)),
            ('callid', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('callerid', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('dialcode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['country_dialcode.Prefix'], null=True, blank=True)),
            ('starting_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('billsec', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('progresssec', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('answersec', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('waitsec', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('disposition', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('hangup_cause', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('hangup_cause_q850', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('leg_type', self.gf('django.db.models.fields.SmallIntegerField')(default=1, null=True, blank=True)),
            ('amd_status', self.gf('django.db.models.fields.SmallIntegerField')(default=1, null=True, blank=True)),
        ))
        db.send_create_signal(u'dialer_cdr', ['VoIPCall'])

    def backwards(self, orm):
        # Deleting model 'Callrequest'
        db.delete_table(u'dialer_callrequest')

        # Deleting model 'VoIPCall'
        db.delete_table('dialer_cdr')

    models = {
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
        u'country_dialcode.country': {
            'Meta': {'object_name': 'Country', 'db_table': "'dialcode_country'"},
            'countrycode': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'countryname': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'countryprefix': ('django.db.models.fields.IntegerField', [], {'max_length': '12'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2'})
        },
        u'country_dialcode.prefix': {
            'Meta': {'ordering': "['prefix']", 'object_name': 'Prefix', 'db_table': "'dialcode_prefix'"},
            'carrier_name': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'country_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['country_dialcode.Country']", 'null': 'True', 'db_column': "'country_id'", 'blank': 'True'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'prefix': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'prefix_type': ('django.db.models.fields.IntegerField', [], {'default': '1'})
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
            'campaign_code': ('django.db.models.fields.CharField', [], {'default': "'EIMCG'", 'unique': 'True', 'max_length': '20', 'blank': 'True'}),
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
            'aleg_gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_gateway.Gateway']", 'null': 'True', 'blank': 'True'}),
            'aleg_uuid': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'call_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 12, 9, 0, 0)'}),
            'call_type': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
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
            'request_uuid': ('django.db.models.fields.CharField', [], {'default': "'9044872e-6067-11e3-a48e-00231470a30c'", 'max_length': '120', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '180', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_campaign.Subscriber']", 'null': 'True', 'blank': 'True'}),
            'timelimit': ('django.db.models.fields.IntegerField', [], {'default': '3600', 'blank': 'True'}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'default': '30', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'dialer_cdr.voipcall': {
            'Meta': {'object_name': 'VoIPCall', 'db_table': "'dialer_cdr'"},
            'amd_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'answersec': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'billsec': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'callid': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'callrequest': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_cdr.Callrequest']", 'null': 'True', 'blank': 'True'}),
            'dialcode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['country_dialcode.Prefix']", 'null': 'True', 'blank': 'True'}),
            'disposition': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hangup_cause': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'hangup_cause_q850': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leg_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'progresssec': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'request_uuid': ('django.db.models.fields.CharField', [], {'default': "'904536ce-6067-11e3-a48e-00231470a30c'", 'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'starting_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'used_gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dialer_gateway.Gateway']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Call Sender'", 'to': u"orm['auth.User']"}),
            'waitsec': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['dialer_cdr']
