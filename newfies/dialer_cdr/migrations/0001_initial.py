# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Callrequest'
        db.create_table(u'dialer_callrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('request_uuid', self.gf('django.db.models.fields.CharField')(default='e03605de-0b08-11e1-815a-00231470a30c', max_length=120, null=True, db_index=True, blank=True)),
            ('call_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 11, 9, 20, 27, 34, 808198))),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('call_type', self.gf('django.db.models.fields.IntegerField')(default='1', null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default='1', null=True, blank=True)),
            ('callerid', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('timeout', self.gf('django.db.models.fields.IntegerField')(default=30, blank=True)),
            ('timelimit', self.gf('django.db.models.fields.IntegerField')(default=3600, blank=True)),
            ('extra_dial_string', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('campaign_subscriber', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_campaign.CampaignSubscriber'], null=True, blank=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_campaign.Campaign'], null=True, blank=True)),
            ('aleg_gateway', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_gateway.Gateway'], null=True, blank=True)),
            ('voipapp', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voip_app.VoipApp'], null=True, blank=True)),
            ('extra_data', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('num_attempt', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_attempt_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=180, blank=True)),
            ('hangup_cause', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('parent_callrequest', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_cdr.Callrequest'], null=True, blank=True)),
        ))
        db.send_create_signal('dialer_cdr', ['Callrequest'])

        # Adding model 'VoIPCall'
        db.create_table('dialer_cdr', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Call Sender', to=orm['auth.User'])),
            ('request_uuid', self.gf('django.db.models.fields.CharField')(default='e03682d4-0b08-11e1-815a-00231470a30c', max_length=120, null=True, db_index=True, blank=True)),
            ('used_gateway', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_gateway.Gateway'], null=True, blank=True)),
            ('callrequest', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_cdr.Callrequest'], null=True, blank=True)),
            ('callid', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('callerid', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('dialcode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prefix_country.Prefix'], null=True, blank=True)),
            ('starting_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('billsec', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('progresssec', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('answersec', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('waitsec', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('disposition', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('hangup_cause', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('hangup_cause_q850', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal('dialer_cdr', ['VoIPCall'])

    def backwards(self, orm):
        # Deleting model 'Callrequest'
        db.delete_table(u'dialer_callrequest')

        # Deleting model 'VoIPCall'
        db.delete_table('dialer_cdr')

    models = {
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
            'campaign_code': ('django.db.models.fields.CharField', [], {'default': "'IBJPZ'", 'unique': 'True', 'max_length': '20', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'daily_start_time': ('django.db.models.fields.TimeField', [], {'default': "'00:00:00'"}),
            'daily_stop_time': ('django.db.models.fields.TimeField', [], {'default': "'23:59:59'"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expirationdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 9, 20, 27, 34, 845674)'}),
            'extra_data': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'frequency': ('django.db.models.fields.IntegerField', [], {'default': "'10'", 'null': 'True', 'blank': 'True'}),
            'friday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervalretry': ('django.db.models.fields.IntegerField', [], {'default': "'300'", 'null': 'True', 'blank': 'True'}),
            'maxretry': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'monday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phonebook': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['dialer_campaign.Phonebook']", 'null': 'True', 'blank': 'True'}),
            'saturday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'startingdate': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 11, 9, 20, 27, 34, 845594)'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'2'", 'null': 'True', 'blank': 'True'}),
            'sunday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'thursday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tuesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Campaign owner'", 'to': "orm['auth.User']"}),
            'voipapp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'VoIP Application'", 'to': "orm['voip_app.VoipApp']"}),
            'wednesday': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'dialer_campaign.campaignsubscriber': {
            'Meta': {'unique_together': "(['contact', 'campaign'],)", 'object_name': 'CampaignSubscriber', 'db_table': "u'dialer_campaign_subscriber'"},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Contact']", 'null': 'True', 'blank': 'True'}),
            'count_attempt': ('django.db.models.fields.IntegerField', [], {'default': "'0'", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duplicate_contact': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dialer_campaign.contact': {
            'Meta': {'unique_together': "(['contact', 'phonebook'],)", 'object_name': 'Contact', 'db_table': "u'dialer_contact'"},
            'additional_vars': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['prefix_country.Country']", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'phonebook': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Phonebook']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dialer_campaign.phonebook': {
            'Meta': {'object_name': 'Phonebook', 'db_table': "u'dialer_phonebook'"},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '90'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Phonebook owner'", 'to': "orm['auth.User']"})
        },
        'dialer_cdr.callrequest': {
            'Meta': {'object_name': 'Callrequest', 'db_table': "u'dialer_callrequest'"},
            'aleg_gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_gateway.Gateway']", 'null': 'True', 'blank': 'True'}),
            'call_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 11, 9, 20, 27, 34, 851116)'}),
            'call_type': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'}),
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.Campaign']", 'null': 'True', 'blank': 'True'}),
            'campaign_subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_campaign.CampaignSubscriber']", 'null': 'True', 'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'extra_data': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'extra_dial_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'hangup_cause': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_attempt_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'num_attempt': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent_callrequest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_cdr.Callrequest']", 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'request_uuid': ('django.db.models.fields.CharField', [], {'default': "'e03605de-0b08-11e1-815a-00231470a30c'", 'max_length': '120', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '180', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'null': 'True', 'blank': 'True'}),
            'timelimit': ('django.db.models.fields.IntegerField', [], {'default': '3600', 'blank': 'True'}),
            'timeout': ('django.db.models.fields.IntegerField', [], {'default': '30', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'voipapp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voip_app.VoipApp']", 'null': 'True', 'blank': 'True'})
        },
        'dialer_cdr.voipcall': {
            'Meta': {'object_name': 'VoIPCall', 'db_table': "'dialer_cdr'"},
            'answersec': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'billsec': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'callerid': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'callid': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'callrequest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_cdr.Callrequest']", 'null': 'True', 'blank': 'True'}),
            'dialcode': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['prefix_country.Prefix']", 'null': 'True', 'blank': 'True'}),
            'disposition': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'hangup_cause': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'hangup_cause_q850': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'progresssec': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'request_uuid': ('django.db.models.fields.CharField', [], {'default': "'e03682d4-0b08-11e1-815a-00231470a30c'", 'max_length': '120', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'starting_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'used_gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_gateway.Gateway']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Call Sender'", 'to': "orm['auth.User']"}),
            'waitsec': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
        u'prefix_country.country': {
            'Meta': {'object_name': 'Country', 'db_table': "'simu_country'"},
            'countrycode': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'countryname': ('django.db.models.fields.CharField', [], {'max_length': '240'}),
            'countryprefix': ('django.db.models.fields.IntegerField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'prefix_country.prefix': {
            'Meta': {'ordering': "['prefix']", 'object_name': 'Prefix', 'db_table': "'simu_prefix'"},
            'carrier_name': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'country_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['prefix_country.Country']", 'null': 'True', 'db_column': "'country_id'", 'blank': 'True'}),
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'prefix': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'prefix_type': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'voip_app.voipapp': {
            'Meta': {'object_name': 'VoipApp', 'db_table': "u'voip_app'"},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gateway': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dialer_gateway.Gateway']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '90'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': "'1'", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'VoIP App owner'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['dialer_cdr']