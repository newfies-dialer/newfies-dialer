# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Campaign'
        db.create_table(u'dialer_campaign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('campaign_code', self.gf('django.db.models.fields.CharField')(default='XWZXJ', unique=True, max_length=20, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Campaign owner', to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=2, null=True, blank=True)),
            ('callerid', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('caller_name', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('startingdate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 3, 11, 0, 0))),
            ('expirationdate', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 3, 12, 0, 0))),
            ('daily_start_time', self.gf('django.db.models.fields.TimeField')(default='00:00:00')),
            ('daily_stop_time', self.gf('django.db.models.fields.TimeField')(default='23:59:59')),
            ('monday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tuesday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('wednesday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('thursday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('friday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('saturday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sunday', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('frequency', self.gf('django.db.models.fields.IntegerField')(default='10', null=True, blank=True)),
            ('callmaxduration', self.gf('django.db.models.fields.IntegerField')(default='1800', null=True, blank=True)),
            ('maxretry', self.gf('django.db.models.fields.IntegerField')(default='0', null=True, blank=True)),
            ('intervalretry', self.gf('django.db.models.fields.IntegerField')(default='300', null=True, blank=True)),
            ('completion_maxretry', self.gf('django.db.models.fields.IntegerField')(default='0', null=True, blank=True)),
            ('completion_intervalretry', self.gf('django.db.models.fields.IntegerField')(default='900', null=True, blank=True)),
            ('calltimeout', self.gf('django.db.models.fields.IntegerField')(default='45', null=True, blank=True)),
            ('aleg_gateway', self.gf('django.db.models.fields.related.ForeignKey')(related_name='A-Leg Gateway', to=orm['dialer_gateway.Gateway'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('extra_data', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('imported_phonebook', self.gf('django.db.models.fields.CharField')(default='', max_length=500, blank=True)),
            ('totalcontact', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('completed', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('has_been_started', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_been_duplicated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('voicemail', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('amd_behavior', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('voicemail_audiofile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['audiofield.AudioFile'], null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dialer_campaign', ['Campaign'])

        # Adding M2M table for field phonebook on 'Campaign'
        db.create_table(u'dialer_campaign_phonebook', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('campaign', models.ForeignKey(orm['dialer_campaign.campaign'], null=False)),
            ('phonebook', models.ForeignKey(orm['dialer_contact.phonebook'], null=False))
        ))
        db.create_unique(u'dialer_campaign_phonebook', ['campaign_id', 'phonebook_id'])

        # Adding model 'Subscriber'
        db.create_table(u'dialer_subscriber', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_contact.Contact'], null=True, blank=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dialer_campaign.Campaign'], null=True, blank=True)),
            ('last_attempt', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('count_attempt', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('completion_count_attempt', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('duplicate_contact', self.gf('django.db.models.fields.CharField')(max_length=90)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('dialer_campaign', ['Subscriber'])

        # Adding unique constraint on 'Subscriber', fields ['contact', 'campaign']
        db.create_unique(u'dialer_subscriber', ['contact_id', 'campaign_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'Subscriber', fields ['contact', 'campaign']
        db.delete_unique(u'dialer_subscriber', ['contact_id', 'campaign_id'])

        # Deleting model 'Campaign'
        db.delete_table(u'dialer_campaign')

        # Removing M2M table for field phonebook on 'Campaign'
        db.delete_table('dialer_campaign_phonebook')

        # Deleting model 'Subscriber'
        db.delete_table(u'dialer_subscriber')

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
            'campaign_code': ('django.db.models.fields.CharField', [], {'default': "'AILDP'", 'unique': 'True', 'max_length': '20', 'blank': 'True'}),
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
        }
    }

    complete_apps = ['dialer_campaign']
